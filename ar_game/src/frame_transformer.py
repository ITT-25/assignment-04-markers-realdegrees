import cv2
import numpy as np
import pyglet
from src.config import Config


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
        brightened = cv2.convertScaleAbs(frame, alpha=1.2, beta=30)

        # Sharpen the image to enhance details
        sharpen_kernel = np.array([[0, -1, 0],
                                   [-1, 6.5, -1],
                                   [0, -1, 0]])

        sharpened = cv2.filter2D(brightened, -1, sharpen_kernel)
        
        # Remove noise
        denoised = cv2.medianBlur(sharpened, 3)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        

        if Config.DEBUG:
            cv2.imshow("Postprocessed Frame", closed)
            cv2.imshow("Original Frame", frame)

        return closed

