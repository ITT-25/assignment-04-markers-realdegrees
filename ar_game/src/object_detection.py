import cv2
import numpy as np
from typing import Optional, Sequence, Tuple
from src.config import Config
from cv2.typing import MatLike


class ObjectDetection:
    def __init__(self):
        # Kernel for morphological operations
        self.kernel = np.ones((5, 5), np.uint8)

    def detect_object(self, frame: np.ndarray) -> Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]:
        """
        Detect the object in the frame and return its highest and lowest point coordinates.
        Returns a tuple of (highest_point, lowest_point) where each point is (x, y) or None if no object is detected.
        """
        # Pre process frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, Config.CONTOUR_SENSITIVITY, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Find the contour with the highest point and get its lowest point
        highest_point_coords, contour = self._find_highest_point(contours)
        lowest_point_coords = self._find_lowest_point(contour)

        if Config.DEBUG and contour is not None:
            # cv2.imshow("Thresholded Frame", thresh)
            cv2.drawContours(frame, [contour], 0, (0, 0, 255, 255), 3)
            cv2.circle(
                frame,
                (int(highest_point_coords[0]), int(Config.WINDOW_HEIGHT - highest_point_coords[1])),
                50,
                (255, 0, 0),
                15,
            )
            cv2.circle(
                frame,
                (int(lowest_point_coords[0]), int(Config.WINDOW_HEIGHT - lowest_point_coords[1])),
                50,
                (255, 0, 0),
                15,
            )
            cv2.line(
                frame,
                (int(highest_point_coords[0]), int(Config.WINDOW_HEIGHT - highest_point_coords[1])),
                (int(lowest_point_coords[0]), int(Config.WINDOW_HEIGHT - lowest_point_coords[1])),
                (0, 255, 0),
                5,
            )

        return (highest_point_coords, lowest_point_coords)

    def _find_lowest_point(self, contour: Optional[MatLike]) -> Optional[Tuple[float, float]]:
        """Find the lowest centered point in the contour."""
        if contour is None or len(contour) == 0:
            return None

        # Y range threshold for points to be considered at the "lowest" level
        Y_RANGE_THRESHOLD = 20

        contour_points = contour.reshape(-1, 2)
        highest_y = np.max(contour_points[:, 1])

        # Find all points within Y_RANGE_THRESHOLD of the lowest point
        lowest_points_indices = np.where(contour_points[:, 1] >= highest_y - Y_RANGE_THRESHOLD)[0]
        lowest_points = contour_points[lowest_points_indices]

        if len(lowest_points) == 0:
            return None

        # Find the point with the median x value among the lowest points
        median_x = np.median(lowest_points[:, 0])

        # Get the closest x to the median (in case the exact median isn't in the points)
        closest_idx = np.argmin(np.abs(lowest_points[:, 0] - median_x))
        x_at_median = lowest_points[closest_idx, 0]
        y_at_median = lowest_points[closest_idx, 1]

        lowest_point_coords = (float(x_at_median), float(Config.WINDOW_HEIGHT - y_at_median))
        return lowest_point_coords

    def _find_highest_point(
        self, contours: Sequence[MatLike]
    ) -> Tuple[Optional[Tuple[float, float]], Optional[MatLike]]:
        """Find the contour with the highest point."""
        best_contour = None
        lowest_y = float("inf")
        highest_point_coords = None

        for contour in contours:
            # Filter small contours
            if cv2.contourArea(contour) < Config.MIN_CONTOUR_AREA:
                continue

            # Find the point with the lowest y value in this contour
            contour_points = contour.reshape(-1, 2)
            min_y_in_contour = np.min(contour_points[:, 1])

            # Update highest point (lowest y-value)
            if min_y_in_contour < lowest_y:
                lowest_y = min_y_in_contour
                # Find the x coordinate at this y-value
                min_y_indices = np.where(contour_points[:, 1] == min_y_in_contour)[0]
                x_at_min_y = contour_points[min_y_indices[0], 0]
                highest_point_coords = (float(x_at_min_y), float(Config.WINDOW_HEIGHT - lowest_y))
                best_contour = contour  # Save the contour with the highest point

        # Set the highest point coordinates if a best contour was found
        if best_contour is not None:
            # Extract the contour points
            contour_points = best_contour.reshape(-1, 2)
            # Find the minimum y value (highest point in screen coordinates)
            lowest_y = np.min(contour_points[:, 1])
            # Find the x coordinate at this y-value
            min_y_indices = np.where(contour_points[:, 1] == lowest_y)[0]
            x_at_min_y = contour_points[min_y_indices[0], 0]
            highest_point_coords = (float(x_at_min_y), float(Config.WINDOW_HEIGHT - lowest_y))

        return highest_point_coords, best_contour
