import cv2
import numpy as np
from typing import List, Tuple, Optional
from config import Config

class PerspectiveTransformer:
    def transform(self, frame: np.ndarray, points: List[Tuple[int, int]]) -> Optional[np.ndarray]:
        """Transform the perspective of the frame based on selected points"""
        if len(points) != 4 or frame is None:
            return None
        
        # Order the points for consistent transformation
        ordered_points = self._order_points(points)
        if ordered_points is None:
            return None
        dst_pts = np.array([
            [0, 0],
            [Config.WINDOW_WIDTH - 1, 0],
            [Config.WINDOW_WIDTH - 1, Config.WINDOW_HEIGHT - 1],
            [0, Config.WINDOW_HEIGHT - 1]
        ], dtype=np.float32)
        matrix = cv2.getPerspectiveTransform(ordered_points, dst_pts)
        return cv2.warpPerspective(frame, matrix, (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))

    def _order_points(self, points: List[Tuple[int, int]]) -> Optional[np.ndarray]:
        """Sort 4 points into top-left, top-right, bottom-right, bottom-left."""
        points_np = np.array(points, dtype="float32")
        if len(points_np) != 4:
            return None
        # Calculate the center of the points
        center = np.mean(points_np, axis=0)
        # Classify points based on their position relative to the center
        top_left = None
        top_right = None
        bottom_right = None
        bottom_left = None
        for point in points_np:
            is_above = point[1] < center[1]
            is_left = point[0] < center[0]
            if is_above and is_left:
                top_left = point
            elif is_above and not is_left:
                top_right = point
            elif not is_above and not is_left:
                bottom_right = point
            elif not is_above and is_left:
                bottom_left = point
        if top_left is None or top_right is None or bottom_right is None or bottom_left is None:
            return None
        return np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")