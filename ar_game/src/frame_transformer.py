import cv2
import numpy as np
import pyglet


class FrameTransformer:
    @staticmethod
    def cv2_to_pyglet(img: np.ndarray) -> pyglet.image.ImageData:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for pyglet
        rows, cols, channels = img.shape
        bytes_per_row = channels * cols
        return pyglet.image.ImageData(width=cols, height=rows, fmt="RGB", data=img.tobytes(), pitch=-bytes_per_row)

    @staticmethod
    def postprocess_frame(frame: np.ndarray) -> np.ndarray:
        """Cleanup the final frame before rendering"""
        # Increase Brightness
        brightened = cv2.convertScaleAbs(frame, alpha=1.1, beta=25)

        return brightened
