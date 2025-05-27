# Main entry point for AR game
import click
import pyglet
from pyglet.window import Window
from pyglet.graphics import Batch
from config import Config


class GameManager(Window):
    def __init__(
        self,
        video_id: int,
        mirror: bool,
    ):
        super().__init__(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT, "Fitness Trainer")

        # Init graphics stuff
        self.batch = Batch()
        
        # TODO: Initialize camera module that returns the camera feed as pyglet compatible image
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
        self.batch.draw()

    def on_close(self):
        pyglet.app.exit()


@click.command()
@click.option('--video-id', default=1, type=int, help='Camera video ID')
@click.option('--mirror', is_flag=True, help='Mirror the camera feed horizontally')
@click.option('--width', default=1920, type=int, help='Width of the application window')
@click.option('--height', default=1080, type=int, help='Height of the application window')
def main(video_id: int, mirror: bool, width: int, height: int) -> None:
    """Start the AR board game with the given configuration"""

    Config.WINDOW_WIDTH = width
    Config.WINDOW_HEIGHT = height
    
    GameManager(
        video_id=video_id,
        mirror=mirror
    )

if __name__ == "__main__":
    main()
