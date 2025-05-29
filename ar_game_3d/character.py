import time
import random
from typing import TYPE_CHECKING
from config import ATTACK_COOLDOWN

if TYPE_CHECKING:
    from AR_model import Model

class Character:
    
    def __init__(self, model: 'Model', character_id: int, name: str):        
        self.model = model
        self.character_id = character_id
        self.name = name
        self.position = None
        self.marker_position = None
        self.is_visible = False
        self.last_attack_time = 0
        self.is_attacking = False
        self.attack_animation_time = 0
        self.target_character = None
        self.delete_flag = False
        self.health = 100
        self.max_health = 100
        self.is_defeated = False
        self.death_animation_time = 0
        self.death_animation_duration = 2.0  # 2 seconds to shrink
        self.original_scale = model._scaling_factor
        
        # Marker caching properties
        self.last_marker_seen_time = 0
        self.marker_cache_duration = 1.0  # Cache marker data for 1 second
        self.cached_view_matrix = None
        self.cached_position = None
        self.cached_marker_length = None
        self.marker_currently_detected = False
        
    def update_marker_data(self, view_matrix, position, marker_length):
        """Update marker data and cache it"""
        current_time = time.time()
        self.last_marker_seen_time = current_time
        self.marker_currently_detected = True
        self.cached_view_matrix = view_matrix.copy() if view_matrix is not None else None
        self.cached_position = position
        self.cached_marker_length = marker_length
        self.marker_position = position
        
    def should_be_visible(self):
        """Check if character should be visible based on marker detection and cache"""
        current_time = time.time()
        time_since_last_seen = current_time - self.last_marker_seen_time
        
        # If marker is currently detected, always visible
        if self.marker_currently_detected:
            return True
            
        # If within cache duration and we have cached data, stay visible
        if time_since_last_seen <= self.marker_cache_duration and self.cached_view_matrix is not None:
            return True
            
        return False
        
    def get_current_marker_data(self):
        """Get current marker data (either live or cached)"""
        if self.marker_currently_detected:
            return self.cached_view_matrix, self.cached_position, self.cached_marker_length
        elif self.should_be_visible():
            # Use cached data
            return self.cached_view_matrix, self.cached_position, self.cached_marker_length
        else:
            return None, None, None

    def update(self, dt: float):
        """Update character state and animations"""
        # Reset marker detection flag at start of frame
        self.marker_currently_detected = False
        
        # Update visibility based on marker cache
        self.is_visible = self.should_be_visible()
        
        if self.is_attacking:
            self.attack_animation_time += dt
            # Attack animation lasts 1 second
            if self.attack_animation_time >= 1.0:
                self.is_attacking = False
                self.attack_animation_time = 0
                
        # Handle death animation
        if self.is_defeated and not self.health > 0:
            self.death_animation_time += dt
            # Gradually shrink the character
            progress = min(1.0, self.death_animation_time / self.death_animation_duration)
            scale_factor = (1.0 - progress) * self.original_scale
            self.model._scaling_factor = max(0.01, scale_factor)

            if self.death_animation_time >= self.death_animation_duration:
                self.is_visible = False
                self.delete_flag = True
                
    def can_attack(self) -> bool:
        """Check if character can perform an attack"""
        current_time = time.time()
        return current_time - self.last_attack_time >= ATTACK_COOLDOWN
    
    def attack(self, target: 'Character'):
        """Perform attack on target character"""
        if self.can_attack() and target:
            self.is_attacking = True
            self.attack_animation_time = 0
            self.last_attack_time = time.time()
            self.target_character = target
            
            # Deal damage to target
            damage = random.randint(15, 25)
            target.take_damage(damage)
            
            print(f"{self.name} attacks {target.name} for {damage} damage!")
            
    def take_damage(self, damage: int):
        """Take damage and update health"""
        self.health = max(0, self.health - damage)        
        if self.health <= 0 and not self.is_defeated:
            print(f"{self.name} has been defeated!")
            self.is_defeated = True
            self.death_animation_time = 0
