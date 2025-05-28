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
        board_ids=None,
    ):
        super().__init__(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT, "Fitness Trainer")
        self.mirror = mirror
        self.camera = Camera(video_id=video_id)
        self.marker_detection = MarkerDetection(board_ids)

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
            perspective_transformed_frame = PerspectiveTransformer.transform(frame, inner_corners)
            if perspective_transformed_frame is not None:
                if self.mirror:
                    perspective_transformed_frame = cv2.flip(perspective_transformed_frame, 1)
                
                perspective_transformed_frame = FrameTransformer.postprocess_frame(perspective_transformed_frame)
        
        # Update background image
        self.background.image = FrameTransformer.cv2_to_pyglet(
            perspective_transformed_frame if perspective_transformed_frame is not None else frame
        )
        
        # Adjust game state
        new_game_state = GameState.RUNNING if perspective_transformed_frame is not None else GameState.SEARCHING_AREA
        self.handle_game_state(dt, new_game_state)
        

    def handle_game_state(self, dt:float, new_game_state: GameState):
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
        self.background.draw()
        
        # Draw the game state label or the batch depending on the current game state
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
@click.option(
    "--board-ids",
    default="0,1,2,3",
    show_default=True,
    help="Comma-separated list of marker IDs that are reserved for the game board",
)
def main(video_id: int, mirror: bool, width: int, height: int, debug: bool, board_ids: str) -> None:
    """Start the AR board game with the given configuration"""

    Config.WINDOW_WIDTH = width
    Config.WINDOW_HEIGHT = height
    Config.DEBUG = debug

    # Parse board_ids string into a list of ints
    board_ids_list = [int(x) for x in board_ids.split(",") if x.strip().isdigit()]

    GameManager(video_id=video_id, mirror=mirror, board_ids=board_ids_list)


if __name__ == "__main__":
    main()
