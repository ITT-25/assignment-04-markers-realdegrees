# ArUco marker detection and processing
import cv2
import cv2.aruco as aruco
import numpy as np
import time
from typing import Tuple, Optional, Dict
from config import Config


class MarkerDetection:
    def __init__(self, board_ids: list[int], *, dictionary_type: int = aruco.DICT_6X6_250):
        self.aruco_dict = aruco.getPredefinedDictionary(dictionary_type)
        self.detector = aruco.ArucoDetector(self.aruco_dict, aruco.DetectorParameters())
        self.marker_cache: Dict[int, Tuple[np.ndarray, float]] = {}
        self.cache_timeout = 1
        self.board_ids = board_ids

    def get_inner_corner(self, marker_corners: np.ndarray, board_center: np.ndarray) -> np.ndarray:
        """Get the inner corner of a marker (closest to board center)"""
        distances = np.linalg.norm(marker_corners - board_center, axis=1)
        return marker_corners[np.argmin(distances)]
    
    def get_cached_marker_count(self) -> int:
        """Get the count of recent cached markers."""
        current_time = time.time()
        
        # Count only markers that haven't timed out
        recent_markers = [marker_id for marker_id, (_, timestamp) in self.marker_cache.items() 
                          if current_time - timestamp < 5 / Config.UPDATE_RATE]
        return len(recent_markers)

    def _extrapolate_fourth_corner(self, corners: np.ndarray) -> np.ndarray:
        """Extrapolate the fourth corner of a rectangle given three corners."""
        # Find the diagonal (longest distance between corners)
        distances = np.array([np.linalg.norm(corners[i] - corners[j]) for i in range(3) for j in range(i + 1, 3)])
        max_dist_idx = np.argmax(distances)

        # Convert flat index to corner indices
        diagonal_pairs = [(i, j) for i in range(3) for j in range(i + 1, 3)]
        diagonal_corners = diagonal_pairs[max_dist_idx]
        right_angle_corner = next(i for i in range(3) if i not in diagonal_corners)

        # Fourth point = diagonal_point1 + diagonal_point2 - right_angle_point
        return corners[diagonal_corners[0]] + corners[diagonal_corners[1]] - corners[right_angle_corner]

    def _get_marker_data(self, frame: np.ndarray, current_time: float) -> list:
        """Get marker data from detection or cache, limited to allowed marker IDs"""
        board_ids = self.board_ids

        # Detect markers
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected_markers, marker_ids, _ = self.detector.detectMarkers(gray)

        # Draw markers for debugging
        if Config.DEBUG and detected_markers:
            aruco.drawDetectedMarkers(frame, detected_markers, marker_ids)

        # Update cache with detected markers
        if marker_ids is not None:
            for i, marker in enumerate(detected_markers):
                marker_id = int(marker_ids[i][0])
                if marker_id in board_ids:
                    marker_corners = marker[0]
                    self.marker_cache[marker_id] = (marker_corners, current_time)

        # Try to use detected markers first (if enough)
        marker_data = []
        if marker_ids is not None:
            for i, marker in enumerate(detected_markers):
                marker_id = int(marker_ids[i][0])
                if marker_id in board_ids:
                    corners = marker[0]
                    center = np.mean(corners, axis=0)
                    marker_data.append((center, corners))
            if len(marker_data) >= 3:
                return marker_data

        # Fall back to cached markers if not enough fresh detections
        cached_marker_data = []
        for marker_id, (cached_corners, timestamp) in self.marker_cache.items():
            if marker_id in board_ids:
                # Only use recent cached markers
                if current_time - timestamp < self.cache_timeout:
                    center = np.mean(cached_corners, axis=0)
                    cached_marker_data.append((center, cached_corners))

        # Return cached data only if we have enough markers
        return cached_marker_data if len(cached_marker_data) >= 3 else []

    def get_board_data(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        marker_data = self._get_marker_data(frame, time.time())

        if len(marker_data) < 3:
            return None, None

        centers = np.array([center for center, _ in marker_data])
        board_center = np.mean(centers, axis=0)

        # Sort markers by y-coordinate, then arrange properly
        y_sorted_indices = np.argsort(centers[:, 1])

        if len(marker_data) == 4:
            # Clockwise order: top-left, top-right, bottom-right, bottom-left
            top_indices = sorted(y_sorted_indices[:2], key=lambda i: centers[i][0])
            bottom_indices = sorted(y_sorted_indices[2:], key=lambda i: centers[i][0])
            ordered_indices = [top_indices[0], top_indices[1], bottom_indices[1], bottom_indices[0]]
        else:
            ordered_indices = y_sorted_indices[:3]

        # Get inner corners
        inner_corners = np.array(
            [self.get_inner_corner(marker_data[idx][1], board_center) for idx in ordered_indices], dtype=np.float32
        )

        # Extrapolate fourth corner if only 3 markers
        if len(marker_data) == 3:
            fourth_corner = self._extrapolate_fourth_corner(inner_corners)
            inner_corners = np.vstack([inner_corners, fourth_corner])

        return inner_corners, board_center
