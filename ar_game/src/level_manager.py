import pyglet
from pyglet.graphics import Batch
from pyglet.shapes import Rectangle
from src.config import Config
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.game_manager import GameManager
    
class LevelManager:
    def __init__(self, game_manager: "GameManager", batch: Batch):
        self.game_manager = game_manager
        self.level = 1
        self.points = 0
        self.required_points = self._calculate_required_points(self.level)
        self.bar_height = 32
        self.bar_margin = 16
        self.bar_bg = Rectangle(
            x=0,
            y=Config.WINDOW_HEIGHT - self.bar_height - self.bar_margin,
            width=Config.WINDOW_WIDTH,
            height=self.bar_height,
            color=(49, 49, 49),
            batch=batch
        )
        self.point_bar = Rectangle(
            x=0,
            y=Config.WINDOW_HEIGHT - self.bar_height - self.bar_margin,
            width=0,
            height=self.bar_height,
            color=(32, 253, 58),
            batch=batch
        )
        self.loss_threshold_bar = Rectangle(
            x=Config.WINDOW_WIDTH,
            y=Config.WINDOW_HEIGHT - self.bar_height - self.bar_margin,
            width=0,
            height=self.bar_height,
            color=(253, 65, 32),
            batch=batch
        )
        self.label = pyglet.text.Label(
            self._get_label_text(),
            font_name='Arial',
            font_size=18,
            x=Config.WINDOW_WIDTH // 2,
            y=Config.WINDOW_HEIGHT - self.bar_height // 2 - self.bar_margin,
            anchor_x='center',
            anchor_y='center',
            color=(255, 255, 255, 255),
            batch=batch
        )
        self.countdown_label = pyglet.text.Label(
            '',
            font_name='Arial',
            font_size=36,
            x=Config.WINDOW_WIDTH // 2,
            y=Config.WINDOW_HEIGHT // 2,
            anchor_x='center',
            anchor_y='center',
            color=(255, 255, 255, 255),
            batch=batch
        )
        self.countdown_time = 0
        self.countdown_active = False
        self._update_bar()

    def _calculate_required_points(self, level):
        return 30 + (level - 1) * 10

    def _get_label_text(self):
        return f'Level {self.level} | {self.points}/{self.required_points} points'

    def increment_points(self, amount: int):
        self.points += amount
        if self.points >= self.required_points:
            self.next_level()
        self._update_bar()

    def decrement_points(self, amount: int):
        self.points = self.points - amount
        self._update_bar()

    def _update_bar(self):
        ratio = min(1.0, self.points / self.required_points)
        self.point_bar.width = int(Config.WINDOW_WIDTH * ratio)
        # Negative points bar
        negative_points = max(0, -self.points)
        neg_ratio = min(1.0, negative_points / Config.GAME_OVER_POINT_THRESHOLD)
        neg_width = int(Config.WINDOW_WIDTH * neg_ratio)
        self.loss_threshold_bar.width = neg_width
        self.loss_threshold_bar.x = Config.WINDOW_WIDTH - neg_width
        self.label.text = self._get_label_text()

    def next_level(self):
        self.level += 1
        self.points = 0
        self.required_points = self._calculate_required_points(self.level)
        # Adjust game difficulty
        self.game_manager._min_fruits = min(20, 10 + self.level * 2)
        from src.config import Config as GameConfig
        GameConfig.BOMB_CHANCE = min(0.5, 0.2 + self.level * 0.03)
        self.game_manager.set_spawning_enabled(False)
        self._start_countdown(3)
        self._update_bar()

    def _start_countdown(self, seconds):
        self.countdown_time = seconds
        self.countdown_active = True
        self.countdown_label.text = f'Next level in {int(self.countdown_time)}...'
        pyglet.clock.schedule_interval(self._countdown_update, 1.0)

    def _countdown_update(self, dt):
        if not self.countdown_active:
            return
        self.countdown_time -= 1
        if self.countdown_time > 0:
            self.countdown_label.text = f'Next level in {int(self.countdown_time)}...'
        else:
            self.countdown_label.text = ''
            self.countdown_active = False
            self.game_manager.set_spawning_enabled(True)
            pyglet.clock.unschedule(self._countdown_update)

