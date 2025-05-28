# Main entry point for AR game
import enum
import click
import cv2
import pyglet
from pyglet.window import Window
from pyglet.graphics import Batch
from frame_transformer import FrameTransformer
from marker_detection import MarkerDetection
from camera import Camera
from config import Config
from perspective_transformer import PerspectiveTransformer

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
        mirror: bool,
    ):
        super().__init__(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT, "Fitness Trainer")
        self.mirror = mirror
        self.camera = Camera(video_id=video_id)
        self.marker_detection = MarkerDetection()
        self.perspective_transformer = PerspectiveTransformer()

        # Init graphics stuff
        self.batch = Batch()
        # ! Background drawn manually, not included in batch
        self.background = pyglet.sprite.Sprite(
            pyglet.image.Texture.create(
                width=Config.WINDOW_WIDTH,
                height=Config.WINDOW_HEIGHT,
            ),
        )
        
        self.game_state_label = pyglet.text.Label(
            "",
            font_name="Arial",
            font_size=24,
            x=Config.WINDOW_WIDTH // 2, y=50,
            color=(255, 255, 255, 255),
            anchor_x="center", anchor_y="bottom",
        )

        # TODO: Initialize marker detection module that detects markers in the camera feed and returns their positions, orientations and ids
        # TODO: Initialize game area module that transforms the area between the inner corners of the markers to the window size and returns it as a pyglet compatible image
        # TODO: Initialize object detection module that detects objects in the game area and returns their positions or provides a way to check if a specific position is occupied
        # TODO: Initialize game logic module that uses the object detection module to allow interaction with game objects (e.g. hand could push or pickup a ball)

        # Start the pyglet loop
        pyglet.clock.schedule_interval(self.update, 1.0 / Config.UPDATE_RATE)
        pyglet.app.run()

    def update(self, dt: float):
        frame = self.camera.get_frame()
        if frame is None:
            return

        inner_corners, board_center = self.marker_detection.get_board_data(frame)
        perspective_transformed_frame = None
        
        if inner_corners is not None:
            perspective_transformed_frame = self.perspective_transformer.transform(frame, inner_corners)
            if self.mirror and perspective_transformed_frame is not None:
                perspective_transformed_frame = cv2.flip(perspective_transformed_frame, 1)
            
        
        # Update game state based on whether we can see the board
        new_game_state = GameState.RUNNING if perspective_transformed_frame is not None else GameState.SEARCHING_AREA
        
        # Handle state transitions
        if self.game_state == GameState.SEARCHING_AREA and new_game_state == GameState.RUNNING:
            # Start resuming countdown when board is found
            self.resume_time = Config.RESUME_DURATION
            self.game_state = GameState.RESUMING
        elif self.game_state == GameState.RESUMING:
            # If board lost while resuming, go back to searching
            if new_game_state == GameState.SEARCHING_AREA:
                self.game_state = GameState.SEARCHING_AREA
            # Otherwise count down to running state
            elif self.resume_time <= 0:
                self.game_state = GameState.RUNNING
            else:
                self.resume_time -= dt
        elif self.game_state == GameState.RUNNING and new_game_state == GameState.SEARCHING_AREA:
            # If we lose the board while running, go back to searching
            self.game_state = GameState.SEARCHING_AREA
            self.resume_time = 0.0

        self.background.image = FrameTransformer.cv2_to_pyglet(
            perspective_transformed_frame if perspective_transformed_frame is not None else frame
        )
        
        print(f"Game state: {self.game_state}, Resume time: {self.resume_time:.1f}")

    def on_draw(self):
        self.clear()
        self.background.draw()
        
        if self.game_state == GameState.SEARCHING_AREA:
            self.game_state_label.text = self.game_state.value.format(self.marker_detection.get_cached_marker_count())
            self.game_state_label.draw()
        elif self.game_state == GameState.RESUMING:
            self.game_state_label.text = self.game_state.value.format(self.resume_time)
            self.game_state_label.draw()
        else:
            self.batch.draw()

    def on_close(self):
        self.camera.release()
        pyglet.app.exit()


@click.command()
@click.option("--video-id", default=0, type=int, help="Camera video ID")
@click.option("--mirror", is_flag=True, help="Mirror the camera feed horizontally")
@click.option("--width", default=1920, type=int, help="Width of the application window")
@click.option("--height", default=1080, type=int, help="Height of the application window")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def main(video_id: int, mirror: bool, width: int, height: int, debug: bool) -> None:
    """Start the AR board game with the given configuration"""

    Config.WINDOW_WIDTH = width
    Config.WINDOW_HEIGHT = height
    Config.DEBUG = debug

    GameManager(video_id=video_id, mirror=mirror)


if __name__ == "__main__":
    main()
