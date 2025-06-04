"""
Game Manager class for the 3D AR Game
"""

import numpy as np
from typing import List
from src.character import Character
from src.config import INTERACTION_DISTANCE


class GameManager:
    """Manages the 3D AR game state and interactions"""

    def __init__(self):
        self.characters: List[Character] = []
        self.game_time = 0

    def add_character(self, character: Character):
        """Add a character to the game"""
        self.characters.append(character)

    def update(self, dt: float):
        """Update game state"""
        self.game_time += dt

        # Update all characters
        for character in [c for c in self.characters if c.delete_flag is False]:
            character.update(dt)

        self.check_character_interactions()

    def check_character_interactions(self):
        """Check if characters can see each other and interact"""
        visible_chars = [char for char in self.characters if char.is_visible and char.health > 0]

        if len(visible_chars) >= 2:
            char1, char2 = visible_chars[0], visible_chars[1]

            if char1.marker_position and char2.marker_position:
                # Calculate distance between characters
                distance = np.linalg.norm(np.array(char1.marker_position) - np.array(char2.marker_position))

                # Trigger attack with random fail chance
                if distance <= INTERACTION_DISTANCE:
                    if char1.can_attack() and char2.health > 0:
                        fail = np.random.rand() < 0.1  # 10% chance to fail attack
                        if not fail:
                            char1.attack(char2)
                        else:
                            print(f"{char1.name}'s attack on {char2.name} failed!")
                    elif char2.can_attack() and char1.health > 0:
                        fail = np.random.rand() < 0.1  # 10% chance to fail attack
                        if not fail:
                            char2.attack(char1)
                        else:
                            print(f"{char2.name}'s attack on {char1.name} failed!")
