# Main entry point for AR game
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


class GameManager(Window):
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
        self.background = pyglet.sprite.Sprite(
            pyglet.image.Texture.create(
                width=Config.WINDOW_WIDTH,
                height=Config.WINDOW_HEIGHT,
            ),
            batch=self.batch
        )
        
        
        # TODO: Initialize marker detection module that detects markers in the camera feed and returns their positions, orientations and ids
        # TODO: Initialize game area module that transforms the area between the inner corners of the markers to the window size and returns it as a pyglet compatible image
        # TODO: Initialize object detection module that detects objects in the game area and returns their positions or provides a way to check if a specific position is occupied
        # TODO: Initialize game logic module that uses the object detection module to allow interaction with game objects (e.g. hand could push or pickup a ball)

        # Start the pyglet loop
        pyglet.clock.schedule_interval(self.update, 1.0 / Config.UPDATE_RATE)
        pyglet.app.run()


    def update(self, dt: float):
        pass

    def on_draw(self):
        self.clear()
        frame = self.camera.get_frame()
        if frame is None:
            return
                    
        inner_corners, board_center = self.marker_detection.get_board_data(frame)
        perspective_transformed_frame = None
        if inner_corners is not None:
            perspective_transformed_frame = self.perspective_transformer.transform(frame, inner_corners)
            if self.mirror:
                perspective_transformed_frame = cv2.flip(perspective_transformed_frame, 1)
        
        self.background.image = FrameTransformer.cv2_to_pyglet(perspective_transformed_frame if perspective_transformed_frame is not None else frame)

        self.batch.draw()
    
        

    def on_close(self):
        self.camera.release()
        pyglet.app.exit()


@click.command()
@click.option('--video-id', default=0, type=int, help='Camera video ID')
@click.option('--mirror', is_flag=True, help='Mirror the camera feed horizontally')
@click.option('--width', default=1920, type=int, help='Width of the application window')
@click.option('--height', default=1080, type=int, help='Height of the application window')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def main(video_id: int, mirror: bool, width: int, height: int, debug: bool) -> None:
    """Start the AR board game with the given configuration"""

    Config.WINDOW_WIDTH = width
    Config.WINDOW_HEIGHT = height
    Config.DEBUG = debug
    
    GameManager(
        video_id=video_id,
        mirror=mirror
    )

if __name__ == "__main__":
    main()
