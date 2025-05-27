from typing import Optional, Tuple
import cv2
import numpy as np
import pyglet

COMMON_RESOLUTIONS_ASCENDING = [
    (640, 480),
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1920, 1080)
]

class Camera:
    def __init__(self, video_id: int):
        """Initialize camera capture with specified device ID."""
        self.cap = cv2.VideoCapture(video_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera with ID {video_id}")
        
        # Find and set the highest possible reslution supported by the camera
        for width, height in COMMON_RESOLUTIONS_ASCENDING.__reversed__():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if self.width == width and self.height == height:
                break
    

    def get_pyglet_frame(self) -> Optional[pyglet.image.ImageData]:
        """Get current frame in pyglet-compatible format."""
        success, frame = self.cap.read()
        if not success:
            return None
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = self._cv2pyglet(frame)
        return image

    def _cv2pyglet(self, img: np.ndarray) -> pyglet.image.ImageData:
        """Convert OpenCV image to pyglet image."""
        rows, cols, channels = img.shape
        bytes_per_row = channels * cols
        
        img = pyglet.image.ImageData(
            width=cols, 
            height=rows, 
            fmt="RGB", 
            data=img.tobytes(), 
            pitch=-bytes_per_row
        )
        return img
    
    def get_dimensions(self) -> Tuple[int, int]:
        """Get camera frame dimensions."""
        return (self.width, self.height)
    
    def release(self):
        """Release the camera resource."""
        self.cap.release()
        
    def __del__(self):
        """Destructor to ensure camera resources are released."""
        self.release()