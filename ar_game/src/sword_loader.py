import os
from PIL import Image
import pyglet

class SwordLoader:
    def __init__(self):
        self.sword_sprite = None
        self.sword_image = None
        self.load_sword()
        
    def load_sword(self):
        """Load a single sword image."""
        # Get the absolute path to the image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "..", "assets", "sword.png")
        
        # Load the image using PIL
        image = Image.open(image_path).convert("RGBA")
        
        # Create a transparent background for rotation
        # This helps prevent artifacts during rotation
        background = Image.new('RGBA', image.size, (0, 0, 0, 0))
        background.paste(image, (0, 0), image)
        
        # Rotate the sword image by 45 degrees counter-clockwise
        rotated_sword = background.rotate(45, expand=True, resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
        
        # Convert PIL image to pyglet image
        sword_data = rotated_sword.tobytes()
        sword_pyglet_image = pyglet.image.ImageData(
            rotated_sword.width, rotated_sword.height, 'RGBA', sword_data, 
            pitch=-rotated_sword.width * 4
        )
        
        # Set the anchor point to the center of the image
        sword_pyglet_image.anchor_x = sword_pyglet_image.width // 2
        sword_pyglet_image.anchor_y = sword_pyglet_image.height // 2
        
        self.sword_image = sword_pyglet_image
        self.sword_sprite = pyglet.sprite.Sprite(sword_pyglet_image)
        self.sword_sprite.scale = 15

    def get_sword_image(self):
        """Return the sword image."""
        return self.sword_image
    
    def get_sword_sprite(self):
        """Return the sword sprite."""
        return self.sword_sprite
