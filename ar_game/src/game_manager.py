import math
from collections import deque
from typing import Deque, List
import pyglet
from pyglet.graphics import Batch
from src.level_manager import LevelManager
from src.config import Config
from src.image_loader import ImageLoader
from src.vector_2d import Vector2D
import random
from src.game_object import GameObject


class GameManager:
    gameobjects: list[GameObject] = []
    sword: GameObject
    point_labels: Deque[pyglet.text.Label] = deque(maxlen=10)
    spawning_enabled: bool = False
    _spawn_cooldown: float = Config.OBJECT_INTERVAL
    _last_spawn_time: float = 0.0
    _min_objects: int = 10

    def __init__(self, batch: Batch):
        self.batch = batch
        self.sword = GameObject(ImageLoader().get_sprite("sword.png", rotation=45, scale=1.2))
        self.sword.batch = self.batch
        self.sword.visible = False

        self.level_manager = LevelManager(self, self.batch)

        self.fruit_names = [
            "apple.png",
            "banana.png",
            "cherry.png",
            "grape.png",
            "kiwi.png",
            "lemon.png",
            "orange.png",
            "peach.png",
            "pear.png",
            "pineapple.png",
            "strawberry.png",
            "watermelon.png",
        ]

    def spawn_gameobject(self):
        spawn_bomb = random.random() < Config.BOMB_CHANCE

        if spawn_bomb:
            # Pick a random bomb image
            sprite = ImageLoader().get_sprite("bomb.png", scale=random.uniform(0.8, 1.1))
            gameobject = GameObject(
                sprite,
                y=random.uniform(Config.WINDOW_HEIGHT * 0.2, Config.WINDOW_HEIGHT * 0.45),
                points=Config.BOMB_POINTS,
            )

        else:
            # Pick a random fruit image
            fruit_name = random.choice(self.fruit_names)
            sprite = ImageLoader().get_sprite(fruit_name, scale=random.uniform(0.8, 1.1))
            gameobject = GameObject(
                sprite,
                y=random.uniform(Config.WINDOW_HEIGHT * 0.2, Config.WINDOW_HEIGHT * 0.45),
                points=Config.FRUIT_POINTS,
            )

        # Choose left or right
        side = random.choice(["left", "right"])
        gameobject.y = random.uniform(Config.WINDOW_HEIGHT * 0.2, Config.WINDOW_HEIGHT * 0.5)
        gameobject.x = (
            -gameobject.width if side == "left" else Config.WINDOW_WIDTH + gameobject.width
        )  # off-screen left or right

        # Random upward angle offset
        angle_offset = random.uniform(25, 40)
        angle_rad = math.radians(angle_offset)

        # Random speed
        speed_range = Config.get_fruit_speed_range()
        speed = random.uniform(speed_range[0], speed_range[1])
        direction = 1 if side == "left" else -1
        vx = direction * speed * math.cos(angle_rad)
        vy = speed * math.sin(angle_rad)
        gameobject.velocity = Vector2D(vx, vy)

        # Random angular velocity
        angular_velocity = random.uniform(160, 360) * random.choice([-1, 1])
        gameobject.angular_velocity = angular_velocity
        gameobject.batch = self.batch
        self.gameobjects.append(gameobject)

    def set_spawning_enabled(self, enabled: bool):
        self.spawning_enabled = enabled

    def update(self, dt: float, high: tuple[float, float] = None, low: tuple[float, float] = None):
        """Update the game state."""

        # Spawn gameobjects if needed
        import time

        now = time.time()
        if self.spawning_enabled and len(self.gameobjects) < self._min_objects:
            if now - self._last_spawn_time > self._spawn_cooldown:
                self.spawn_gameobject()
                self._last_spawn_time = now
                self._spawn_cooldown = random.uniform(
                    Config.OBJECT_INTERVAL * 0.4, Config.OBJECT_INTERVAL * 1.2
                )  # Randomize spawn interval

        # Update gameobjects
        self._update_sword(high, low)
        for obj in self.gameobjects:
            obj.physics_update(dt)

        self.check_collisions()
        self.cleanup_gameobjects()
        self.animate_point_labels(dt)

    def animate_point_labels(self, dt: float):
        for label in self.point_labels:
            label.opacity -= dt * 255 / 2  # Fade out labels
            label.opacity = max(0, label.opacity)  # Ensure opacity doesn't go below 0

            # Move labels toward the top center of the screen
            target_x, target_y = self.level_manager.get_bar_progress_position()
            target_y -= label.content_height

            # Calculate direction vector to top center
            dir_x = target_x - label.x
            dir_y = target_y - label.y

            # Normalize and scale the movement
            move_speed = 40 * dt
            label.x += dir_x * 0.03 * move_speed
            label.y += dir_y * 0.05 * move_speed

    def cleanup_gameobjects(self):
        if not self.spawning_enabled:
            for obj in self.gameobjects:
                obj.delete()
            self.gameobjects.clear()  # Clear all game objects when spawning is disabled
            return

        # Remove off-screen or deleted objects immediately after collision check
        # Split objects into those on-screen and those off-screen
        on_screen_objects: List[GameObject] = []
        off_screen_objects: List[GameObject] = []

        for obj in self.gameobjects:
            if obj.off_screen:
                off_screen_objects.append(obj)
            else:
                on_screen_objects.append(obj)

        # Update our game objects list to only contain on-screen objects
        self.gameobjects = on_screen_objects

        for obj in off_screen_objects:
            if obj.points > 0:
                subtract_points = obj.points // 2
                self.level_manager.increment_points(-subtract_points)
                label = pyglet.text.Label(
                    f"-{subtract_points}",
                    font_name="Arial",
                    font_size=int(42 * Config.get_text_scale()),
                    x=min(max(0, obj.x), Config.WINDOW_WIDTH),
                    y=min(max(0, obj.y), Config.WINDOW_HEIGHT),
                    anchor_x="center",
                    anchor_y="center",
                    color=(255, 0, 0, 255),
                    batch=self.batch,
                )
                label.x += label.content_width // 2 * (-1 if obj.x > 0 else 1) * 1.2
                label.y += label.content_height // 2 * (-1 if obj.y > 0 else 1) * 1.2
                self.point_labels.append(label)
            obj.delete()

    def check_collisions(self):
        """Check for collisions between the sword and game objects."""
        for obj in self.gameobjects:
            if obj.off_screen:
                continue

            # Calculate distance between centers
            dx = abs(self.sword.x - obj.x)
            dy = abs(self.sword.y - obj.y)

            # Check if the objects' rectangles overlap
            colliding = dx < (self.sword.width // 2 + obj.width // 2) and dy < (
                self.sword.height // 2 + obj.height // 2
            )

            if self.sword.visible and colliding:
                # Update points, init points label, delete object
                self.level_manager.increment_points(obj.points)
                label = pyglet.text.Label(
                    f"{'+' if obj.points > 0 else ''}{obj.points}",
                    font_name="Arial",
                    font_size=int(48 * Config.get_text_scale()),
                    x=obj.x,
                    y=obj.y,
                    anchor_x="center",
                    anchor_y="center",
                    color=(0, 255, 0, 255) if obj.points > 0 else (255, 0, 0, 255),
                    batch=self.batch,
                )
                self.point_labels.append(label)
                self.gameobjects.remove(obj)
                obj.delete()

    def _update_sword(self, high: tuple[float, float] = None, low: tuple[float, float] = None):
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
            position_lerp_factor = 0.45
            self.sword.x = self.sword.x + (high[0] - self.sword.x) * position_lerp_factor
            self.sword.y = self.sword.y + (high[1] - self.sword.y) * position_lerp_factor

            # Lerp rotation with slightly lower factor for smoother rotation
            rotation_lerp_factor = 0.18
            angle_diff = (angle - self.sword.rotation) % 360
            if angle_diff > 180:
                angle_diff -= 360

            self.sword.rotation = self.sword.rotation + angle_diff * rotation_lerp_factor
        else:
            self.sword.visible = False
