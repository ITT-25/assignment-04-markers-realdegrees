# Main entry point for AR game
import enum
import math
import click
import cv2
import pyglet
from pyglet.window import Window
from pyglet.graphics import Batch
from src.sword_loader import SwordLoader
from src.frame_transformer import FrameTransformer
from src.marker_detection import MarkerDetection
from src.camera import Camera
from src.config import Config
from src.perspective_transformer import PerspectiveTransformer
from src.object_detection import ObjectDetection


class GameState(enum.Enum):
    RUNNING = ""
    SEARCHING_AREA = "Unable to find game area! Required markers: {:d}/3"
    RESUMING = "Resuming in {:.1f} seconds..."


class GameManager(Window):
    game_state: GameState = GameState.SEARCHING_AREA
    resume_time: float = 0.0

    def __init__(
        self,
        video_id: int,
        board_ids=None,
    ):
        super().__init__(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT, "Fitness Trainer")
        self.camera = Camera(video_id=video_id)
        self.marker_detection = MarkerDetection(board_ids)
        self.object_detection = ObjectDetection()

        # Init graphics stuff
        self.batch = Batch()

        self.sword = SwordLoader().get_sword_sprite()
        self.sword.batch = self.batch
        self.sword.visible = False

        # ! Background drawn manually, not included in batch
        self.background = pyglet.shapes.Rectangle(
            0, 0, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT,
            color=(255, 255, 255),
        )
        # Create a persistent texture and sprite for the video frame
        self.frame_texture = pyglet.image.Texture.create(
            width=Config.WINDOW_WIDTH,
            height=Config.WINDOW_HEIGHT,
        )
        self.frame = pyglet.sprite.Sprite(self.frame_texture)

        # ! State label drawn manually, not included in batch
        self.game_state_label = pyglet.text.Label(
            "",
            font_name="Arial",
            font_size=24,
            x=Config.WINDOW_WIDTH // 2,
            y=50,
            color=(15, 15, 15, 255),
            anchor_x="center",
            anchor_y="bottom",
        )

        # TODO: Initialize object detection module that detects objects in the game area and returns their positions or provides a way to check if a specific position is occupied
        # TODO: Initialize game logic module that uses the object detection module to allow interaction with game objects (e.g. hand could push or pickup a ball)

        # Start the pyglet loop
        pyglet.clock.schedule_interval(self.update, 1.0 / Config.UPDATE_RATE)
        pyglet.app.run()

    def update(self, dt: float):
        frame = self.camera.get_frame()
        if frame is None:
            return

        # Get board data from raw frame
        inner_corners, _ = self.marker_detection.get_board_data(frame)

        # Transform game board perspective to screen space, apply modifiers and postprocessing
        perspective_transformed_frame = None
        if inner_corners is not None:
            perspective_transformed_frame = PerspectiveTransformer.transform(
                frame, inner_corners)
            if perspective_transformed_frame is not None:
                perspective_transformed_frame = cv2.flip(perspective_transformed_frame, 1)

                # Object detection
                high, low = self.object_detection.detect_object(
                    perspective_transformed_frame)
                self.handle_sword(high, low)

        image_data = FrameTransformer.cv2_to_pyglet(perspective_transformed_frame if perspective_transformed_frame is not None else frame)
        self.frame_texture.blit_into(
            image_data,
            0, 0, 0
        )

        # Adjust game state
        new_game_state = GameState.RUNNING if perspective_transformed_frame is not None else GameState.SEARCHING_AREA
        self.handle_game_state(dt, new_game_state)

    def handle_sword(self, high: tuple[float, float] = None, low: tuple[float, float] = None):
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

    def handle_game_state(self, dt: float, new_game_state: GameState):
        # Update game state based on whether we can see the board

        # Handle state transitions
        if self.game_state == GameState.SEARCHING_AREA and new_game_state == GameState.RUNNING:
            # Start resuming countdown when board is found
            self.game_state = GameState.RESUMING
        elif self.game_state == GameState.RESUMING:
            # If board is lost while resuming, go back to searching
            if new_game_state == GameState.SEARCHING_AREA:
                self.game_state = GameState.SEARCHING_AREA
                self.resume_time = Config.RESUME_DURATION
            # Otherwise count down to running state
            elif self.resume_time <= 0:
                self.game_state = GameState.RUNNING
            else:
                self.resume_time -= dt
        elif self.game_state == GameState.RUNNING and new_game_state == GameState.SEARCHING_AREA:
            # If board is lost while running, go back to searching
            self.game_state = GameState.SEARCHING_AREA
            self.resume_time = Config.RESUME_DURATION

    def on_draw(self):
        self.clear()

        # Draw background and frame
        if self.game_state != GameState.SEARCHING_AREA:
            self.background.draw()
            self.frame.opacity = int(255 * 0.3)
        else:
            self.frame.opacity = 255
        self.frame.draw()

        # Draw game state label or the batch depending on the current game state
        # Update label text based on game state
        if self.game_state != GameState.RUNNING:
            self.game_state_label.text = (
                self.game_state.value.format(self.marker_detection.get_cached_marker_count())
                if self.game_state == GameState.SEARCHING_AREA
                else self.game_state.value.format(self.resume_time)
            )
            self.game_state_label.draw()
        else:
            self.batch.draw()

    def on_close(self):
        self.camera.release()
        pyglet.app.exit()


@click.command()
@click.option("--video-id", default=0, type=int, help="Camera video ID")
@click.option("--width", default=1920, type=int, help="Width of the application window")
@click.option("--height", default=1080, type=int, help="Height of the application window")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option(
    "--board-ids",
    default="0,1,2,3",
    show_default=True,
    help="Comma-separated list of marker IDs that are reserved for the game board",
)
def main(video_id: int, width: int, height: int, debug: bool, board_ids: str) -> None:
    """Start the AR board game with the given configuration"""

    Config.WINDOW_WIDTH = width
    Config.WINDOW_HEIGHT = height
    Config.DEBUG = debug

    # Parse board_ids string into a list of ints
    board_ids_list = [int(x) for x in board_ids.split(",") if x.strip().isdigit()]

    GameManager(video_id=video_id, board_ids=board_ids_list)


if __name__ == "__main__":
    main()
