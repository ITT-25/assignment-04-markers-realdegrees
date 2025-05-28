import math
from pyglet.graphics import Batch
from src.image_loader import ImageLoader

class GameManager:
    def __init__(self, batch: Batch):
        self.batch = batch
        self.sword = ImageLoader().get_sprite("sword.png", rotation=45, scale=1.2)
        self.sword.batch = self.batch
        self.sword.visible = False

    def update(self, dt: float):
        """Update the game state."""
        pass
    
    def update_sword(self, high: tuple[float, float] = None, low: tuple[float, float] = None):
        """Set the visibility, position, and rotation of the sword based on high and low coordinates."""
        if high is not None and low is not None:
            # Handle sword positioning and rotation
            self.sword.visible = True

            # Calculate rotation angle based on direction from low to high
            dx = high[0] - low[0]
            dy = high[1] - low[1]

            # Calculate rotation angle in degrees from the vector direction
            angle = 90  # Base angle adjustment for the sword image
            if dx == 0:
                angle += 180 if dy < 0 else 0
            else:
                angle_rad = math.atan2(dy, dx)
                angle -= math.degrees(angle_rad)

            # Lerp position with higher factor for smoother movement
            position_lerp_factor = 0.8
            self.sword.x = self.sword.x + (high[0] - self.sword.x) * position_lerp_factor
            self.sword.y = self.sword.y + (high[1] - self.sword.y) * position_lerp_factor

            # Lerp rotation with slightly lower factor for smoother rotation
            rotation_lerp_factor = 0.6
            angle_diff = (angle - self.sword.rotation) % 360
            if angle_diff > 180:
                angle_diff -= 360

            self.sword.rotation = self.sword.rotation + angle_diff * rotation_lerp_factor
        else:
            self.sword.visible = False

