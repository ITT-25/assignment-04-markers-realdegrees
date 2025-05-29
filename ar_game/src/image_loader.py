import os
from PIL import Image
import pyglet
from typing import Dict
from src.config import Config


class ImageLoader:
    def __init__(self):
        self.images: Dict[str, pyglet.image.ImageData] = {}
        self.sprites: Dict[str, pyglet.sprite.Sprite] = {}
        self.assets_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

    def load_image(self, image_name: str, rotation: float = 0, scale: float = 1.0) -> pyglet.sprite.Sprite:
        """Load an image from the assets folder by name."""
        if image_name in self.sprites:
            return self.sprites[image_name]

        # Get the absolute path to the image
        image_path = os.path.join(self.assets_path, image_name)

        # Load the image using PIL
        image = Image.open(image_path).convert("RGBA")

        # Create a transparent background for rotation
        background = Image.new("RGBA", image.size, (0, 0, 0, 0))
        background = Image.alpha_composite(background, image)

        # Rotate the image if needed
        if rotation != 0:
            processed_image = background.rotate(
                rotation, expand=True, resample=Image.Resampling.BICUBIC, fillcolor=(255, 255, 255, 0)
            )
        else:
            processed_image = background

        # Set all fully transparent pixels to (0,0,0,0) to avoid black corners
        data = processed_image.getdata()
        new_data = []
        for item in data:
            if item[3] == 0:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        processed_image.putdata(new_data)

        # Convert PIL image to pyglet image
        image_data = processed_image.tobytes()
        pyglet_image = pyglet.image.ImageData(
            processed_image.width, processed_image.height, "RGBA", image_data, pitch=-processed_image.width * 4
        )

        # Set the anchor point to the center of the image
        pyglet_image.anchor_x = pyglet_image.width // 2
        pyglet_image.anchor_y = pyglet_image.height // 2

        # Store the image and create a sprite
        self.images[image_name] = pyglet_image
        sprite = pyglet.sprite.Sprite(pyglet_image)
        sprite.scale = scale * Config.GAMEOBJECT_BASE_SCALE
        self.sprites[image_name] = sprite

        return sprite

    def get_sprite(self, image_name: str, rotation: float = 0, scale: float = 1.0) -> pyglet.sprite.Sprite:
        """Load image as sprite (Cached)"""
        key = f"{image_name}_{rotation}_{scale}"
        if key in self.sprites:
            return self.sprites[key]
        return self.load_image(image_name, rotation, scale)
