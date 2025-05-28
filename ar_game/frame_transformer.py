import numpy as np
import pyglet


class FrameTransformer:
    @staticmethod
    def cv2_to_pyglet(img: np.ndarray) -> pyglet.image.ImageData:
        rows, cols, channels = img.shape
        bytes_per_row = channels * cols
        return pyglet.image.ImageData(width=cols, height=rows, fmt="RGB", data=img.tobytes(), pitch=-bytes_per_row)
