import cv2
import numpy as np
import pyglet


class FrameTransformer:
    @staticmethod
    def cv2_to_pyglet(img: np.ndarray) -> pyglet.image.ImageData:
        rows, cols, channels = img.shape
        bytes_per_row = channels * cols
        return pyglet.image.ImageData(width=cols, height=rows, fmt="RGB", data=img.tobytes(), pitch=-bytes_per_row)
    
    @staticmethod
    def postprocess_frame(frame: np.ndarray) -> np.ndarray:
        """Cleanup the final frame before rendering"""
        # TODO: Clean up static in the frame and adjust brightness/contrast
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        return blurred
