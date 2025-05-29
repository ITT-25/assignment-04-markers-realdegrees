import pyglet
from src.vector_2d import Vector2D
from src.config import Config


class GameObject(pyglet.sprite.Sprite):
    velocity: Vector2D = Vector2D(0.0, 0.0)
    angular_velocity: float = 0.0
    off_screen: bool = False  # Mark for deletion if off-screen
    points: int

    def __init__(self, sprite: pyglet.sprite.Sprite, x: float = 0.0, y: float = 0.0, points: int = 0):
        super().__init__(sprite.image, x=x, y=y)
        self.rotation = sprite.rotation
        self.scale = sprite.scale
        self.points = points

    def physics_update(self, dt: float):
        """Update the position of the game object based on its velocity. Delete if off-screen."""
        # Apply linear drag
        self.velocity.x *= 1 - Config.LINEAR_DRAG

        # Apply gravity (downward force)
        self.velocity.y -= Config.GRAVITY * dt

        # Update position based on velocity
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt

        # Apply angular drag
        self.angular_velocity *= 1 - Config.ANGULAR_DRAG
        self.rotation += self.angular_velocity * dt

        # Mark for deletion if completely off-screen (Ignore top off-screen)
        if Config.WINDOW_WIDTH is not None and Config.WINDOW_HEIGHT is not None:
            if self.x + self.width < 0 or self.x > Config.WINDOW_WIDTH + self.width or self.y + self.height < 0:
                self.off_screen = True
