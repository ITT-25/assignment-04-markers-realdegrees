# Main entry point for AR game
import click
import pyglet
from pyglet.window import Window
from pyglet.graphics import Batch
from camera import Camera
from config import Config


class GameManager(Window):
    def __init__(
        self,
        video_id: int,
        mirror: bool,
    ):
        super().__init__(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT, "Fitness Trainer")
        
        self.camera = Camera(video_id=video_id)

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
        print(self.camera.get_dimensions())
        self.background.image = self.camera.get_pyglet_frame()
        self.background.scale = Config.WINDOW_WIDTH / self.camera.get_dimensions()[0]
        self.batch.draw()

    def on_close(self):
        self.camera.release()
        pyglet.app.exit()


@click.command()
@click.option('--video-id', default=0, type=int, help='Camera video ID')
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
