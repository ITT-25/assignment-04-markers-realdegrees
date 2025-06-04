# Main entry point for AR game
import enum
import click
import cv2
import pyglet
from pyglet.window import Window
from pyglet.graphics import Batch
from src.game_manager import GameManager
from src.frame_transformer import FrameTransformer
from src.marker_detection import MarkerDetection
from src.camera import Camera
from src.config import Config
from src.perspective_transformer import PerspectiveTransformer
from src.object_detection import ObjectDetection
import threading
import queue


class GameState(enum.Enum):
    RUNNING = ""
    SEARCHING_AREA = "Unable to find game area! Required markers: {:d}/3"
    RESUMING = "Starting in {:.1f} seconds..."


class GameWindow(Window):
    game_state: GameState = GameState.SEARCHING_AREA
    resume_time: float = 0.0

    def __init__(
        self,
        video_id: int,
        camera_width: int,
        camera_height: int,
        board_ids=None,        
    ):
        super().__init__(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT, "Frucht NinjAR")
        self.camera = Camera(video_id=video_id, resolution=(camera_width, camera_height))
        self.marker_detection = MarkerDetection(self, board_ids)
        self.object_detection = ObjectDetection()

        # Init graphics stuff
        self.game_batch = Batch()
        self.ui_batch = Batch()
        self.game_state_batch = Batch()

        self.game_manager = GameManager(self.game_batch)

        # ! Background drawn manually, not included in batch
        self.background = pyglet.shapes.Rectangle(
            0,
            0,
            Config.WINDOW_WIDTH,
            Config.WINDOW_HEIGHT,
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
            font_size=int(24 * Config.get_text_scale()),
            x=Config.WINDOW_WIDTH // 2,
            y=50,
            color=(15, 15, 15, 255),
            anchor_x="center",
            anchor_y="bottom",
            batch=self.game_state_batch,
        )
        self.game_state_background = pyglet.shapes.Rectangle(
            Config.WINDOW_WIDTH // 2,
            45,
            Config.WINDOW_WIDTH,
            int(self.game_state_label.font_size * 2),
            color=(255, 255, 255),
            batch=self.game_state_batch,
        )
        self.game_state_background.anchor_x = self.game_state_background.width // 2
        self.game_state_background.anchor_y = 0

        # Multithreading setup for frame processing
        self.frame_queue = queue.Queue(maxsize=1)
        self.result_queue = queue.Queue(maxsize=1)
        self.processing_thread = threading.Thread(target=self.processing_loop, daemon=True)
        self.last_processed_result = (None, None, None, None, None)
        self.processing_thread.start()
        pyglet.clock.schedule_interval(self.update, 1.0 / Config.UPDATE_RATE)
        pyglet.app.run()

    def processing_loop(self):
        while True:
            try:
                frame = self.frame_queue.get(timeout=1)
            except queue.Empty:
                continue
            # Downscale frame for processing
            h, w = frame.shape[:2]
            new_w, new_h = int(w * Config.PROCESSING_SCALE), int(h * Config.PROCESSING_SCALE)
            small_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            # Marker detection and perspective transform on downscaled frame
            inner_corners, _ = self.marker_detection.get_board_data(small_frame)
            perspective_transformed_frame = None
            high, low = None, None
            if inner_corners is not None:
                # Scale corners back up to original size for correct perspective
                scaled_corners = inner_corners / Config.PROCESSING_SCALE
                perspective_transformed_frame = PerspectiveTransformer.transform(frame, scaled_corners)
                if perspective_transformed_frame is not None:
                    perspective_transformed_frame = cv2.flip(perspective_transformed_frame, 1)
                    high, low = self.object_detection.detect_object(perspective_transformed_frame)
            # Put results in result_queue
            try:
                self.result_queue.put((frame, perspective_transformed_frame, high, low, inner_corners), timeout=0.1)
            except queue.Full:
                pass

    def is_full_board_visible(self) -> bool:
        return self.game_state != GameState.SEARCHING_AREA

    def update(self, dt: float):
        frame = self.camera.get_frame()
        if frame is not None:
            # Send frame to processing thread
            try:
                self.frame_queue.put(frame, timeout=0.01)
            except queue.Full:
                pass
        # Get latest processed result, or reuse last
        try:
            result = self.result_queue.get_nowait()
            self.last_processed_result = result
        except queue.Empty:
            result = self.last_processed_result
        frame, perspective_transformed_frame, high, low, inner_corners = result

        if frame is None:
            return
        image_data = FrameTransformer.cv2_to_pyglet(
            perspective_transformed_frame if perspective_transformed_frame is not None else frame
        )
        self.frame_texture.blit_into(image_data, 0, 0, 0)

        # Adjust game state
        desired_game_state = (
            GameState.RUNNING if perspective_transformed_frame is not None else GameState.SEARCHING_AREA
        )
        self.update_game_state(dt, desired_game_state)

        if self.game_state == GameState.RUNNING:
            self.game_manager.update(dt, high, low)

    def update_game_state(self, dt: float, new_game_state: GameState):
        # Update game state based on whether we can see the board

        # Handle state transitions
        if self.game_state == GameState.SEARCHING_AREA and new_game_state == GameState.RUNNING:
            # Start resuming countdown when board is found
            self.game_state = GameState.RESUMING
            if self.game_manager.level_manager.points <= -Config.GAME_OVER_POINT_THRESHOLD:
                self.game_manager.level_manager.reset()
        elif self.game_state == GameState.RESUMING:
            # If board is lost while resuming, go back to searching
            if new_game_state == GameState.SEARCHING_AREA:
                self.game_state = GameState.SEARCHING_AREA
                self.resume_time = Config.RESUME_DURATION
            # Otherwise count down to running state
            elif self.resume_time <= 0:
                self.game_state = GameState.RUNNING
                self.game_manager.set_spawning_enabled(True)
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
            self.game_state_batch.draw()
        if self.game_state != GameState.SEARCHING_AREA:
            self.game_batch.draw()

    def on_close(self):
        self.camera.release()
        pyglet.app.exit()


@click.command()
@click.option("--video-id", default=0, type=int, help="Camera video ID")
@click.option("--width", show_default=True, default=1280, type=int, help="Width of the application window")
@click.option("--height", show_default=True, default=720, type=int, help="Height of the application window")
@click.option("--camera-width", show_default=True, default=640, type=int, help="Width of the camera feed (Performance intensive)")
@click.option("--camera-height", show_default=True, default=480, type=int, help="Height of the camera feed (Performance intensive)")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--sensitivity", default=20, show_default=True, type=int, help="Contour sensitivity")
@click.option(
    "--board-ids",
    default="0,1,2,3",
    show_default=True,
    help="Comma-separated list of marker IDs that are reserved for the game board",
)
def main(video_id: int, width: int, height: int, camera_width: int, camera_height: int, debug: bool, sensitivity: int, board_ids: str) -> None:
    """Start the AR board game with the given configuration"""

    Config.WINDOW_WIDTH = width
    Config.WINDOW_HEIGHT = height
    Config.DEBUG = debug
    Config.CONTOUR_SENSITIVITY = sensitivity

    # Parse board_ids string into a list of ints
    board_ids_list = [int(x) for x in board_ids.split(",") if x.strip().isdigit()]

    GameWindow(video_id=video_id, camera_width=camera_width, camera_height=camera_height, board_ids=board_ids_list)


if __name__ == "__main__":
    main()
