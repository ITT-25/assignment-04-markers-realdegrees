from typing import Optional, Tuple
import cv2
import numpy as np
from config import Config

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
    

    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame in pyglet-compatible format.
        
        Returns: Tuple containing pyglet image and original OpenCV frame (BGR).
        """
        success, frame = self.cap.read()
        if not success:
            return None
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize the frame to match the window dimensions
        rgb_frame = cv2.resize(rgb_frame, (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))

        return rgb_frame

    def get_dimensions(self) -> Tuple[int, int]:
        """Get camera frame dimensions."""
        return (self.width, self.height)
    
    def release(self):
        """Release the camera resource."""
        self.cap.release()
        
    def __del__(self):
        """Destructor to ensure camera resources are released."""
        self.release()