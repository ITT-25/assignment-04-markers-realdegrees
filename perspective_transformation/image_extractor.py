import cv2
import numpy as np
import click
from typing import Any, List, Tuple, Optional

ESCAPE_KEY = 27
SAVE_KEY = "s"

MAIN_WINDOW_NAME = "Select Region (ESC to reset)"
RESULT_WINDOW_NAME = "Warped Result (S to save, ESC to restart)"


class ImageTransformer:
    def __init__(self) -> None:
        print("Initializing image transformer...")
        self.points: List[Tuple[int, int]] = []
        self.display_image: Optional[np.ndarray] = None
        self.original_image: Optional[np.ndarray] = None
        self.width: Optional[int] = None
        self.height: Optional[int] = None

    def handle_click(self, btn: int, x: int, y: int, _flag: int, _param: Any) -> None:
        if btn == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            # Check if point layout is valid
            ordered_points = self.order_points(self.points + [(x, y)])
            if len(self.points) == 3 and ordered_points is None:
                print("Invalid point. The points must form a quad.")
                return

            # Add point and display it
            self.points.append((x, y))
            print(f"Point {len(self.points)} selected at coordinates ({x}, {y})")
            cv2.circle(self.display_image, (x, y), 8, (0, 0, 255), -1)

            if len(self.points) == 4:
                # Use ordered points to draw the quad outline
                self.points = ordered_points
                for i in range(4):
                    pt1 = tuple(map(int, self.points[i]))
                    pt2 = tuple(map(int, self.points[(i + 1) % 4]))
                    cv2.line(self.display_image, pt1, pt2, (0, 255, 0), 2)

            cv2.imshow(MAIN_WINDOW_NAME, self.display_image)

    def transform_perspective(
        self, image: np.ndarray, points: np.ndarray, *, width: int, height: int, copy: bool = False
    ) -> np.ndarray:
        """Apply perspective transformation based on selected points"""
        print("Applying perspective transformation with ordered points...")
        dst_pts = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)

        matrix = cv2.getPerspectiveTransform(points, dst_pts)
        if copy:
            image = image.copy()
        return cv2.warpPerspective(image, matrix, (width, height))

    # ? This is required because apparently the order of points influences the final "perspective origin" so by manually reordering it outputs the result image at the same rotation as the original image
    def order_points(self, points: List[Tuple[int, int]]) -> Optional[np.ndarray]:
        """Sort 4 points into top-left, top-right, bottom-right, bottom-left robustly."""
        points_np = np.array(points, dtype="float32")

        if len(points_np) != 4:
            return None

        # Sort by y (vertical position)
        y_sorted = points_np[np.argsort(points_np[:, 1]), :]
        top_two = y_sorted[:2, :]
        bottom_two = y_sorted[2:, :]

        # Sort top two by x (horizontal position)
        tl, tr = top_two[np.argsort(top_two[:, 0]), :]
        # Sort bottom two by x
        bl, br = bottom_two[np.argsort(bottom_two[:, 0]), :]

        ordered = np.array([tl, tr, br, bl], dtype="float32")

        # Ensure all points are unique (no duplicates)
        if len({tuple(pt) for pt in ordered}) != 4:
            return None

        return ordered

    def is_main_window_closed(self) -> bool:
        """Check if the main window is still open"""
        win = cv2.getWindowProperty(MAIN_WINDOW_NAME, cv2.WND_PROP_VISIBLE)
        return win < 1

    def process_image(self, input_path: str, output_path: str, width: int, height: int) -> None:
        """Main processing function to handle image transformation workflow"""
        print(f"Processing image from {input_path}")
        print(f"Output dimensions set to {width}x{height}")
        self.width = width
        self.height = height

        # Load the image
        print("Loading image...")
        self.original_image = cv2.imread(input_path)

        if self.original_image is None:
            print(f"Error: Could not load image from {input_path}")
            return

        print(f"Image loaded successfully. Dimensions: {self.original_image.shape}")

        # Setup display window and callback
        print("Setting up display window. Please select 4 corner points...")
        cv2.namedWindow(MAIN_WINDOW_NAME)
        cv2.setMouseCallback(MAIN_WINDOW_NAME, self.handle_click)

        while True:
            # Reset points and create fresh copy for display
            self.points = []
            self.display_image = self.original_image.copy()
            cv2.imshow(MAIN_WINDOW_NAME, self.display_image)
            print("Ready for point selection. Click 4 points to define the region.")

            # Wait for points, reset or close
            while len(self.points) < 4:
                key = cv2.waitKey(100) & 0xFF
                if key == ESCAPE_KEY:
                    break
                elif self.is_main_window_closed():
                    print("Exiting due to window closure.")
                    return

            if key == ESCAPE_KEY:
                print("Resetting selection...")
                continue

            # Transform and display result
            warped_image = self.transform_perspective(
                self.original_image, self.points, width=self.width, height=self.height
            )

            print("Displaying warped result. Press S to save or ESC to restart.")
            cv2.imshow(RESULT_WINDOW_NAME, warped_image)

            # Wait for save, close or reset
            while True:
                key = cv2.waitKey(100) & 0xFF
                save_pressed = key == ord(SAVE_KEY.lower()) or key == ord(SAVE_KEY.upper())
                if save_pressed:
                    print(f"Saving warped image to {output_path}...")
                    cv2.imwrite(output_path, warped_image)
                    print(f"Warped image saved to {output_path}")
                    try:
                        cv2.destroyWindow(RESULT_WINDOW_NAME)
                    except Exception:
                        pass
                    break
                elif key == ESCAPE_KEY:
                    print("Restarting selection...")
                    try:
                        cv2.destroyWindow(RESULT_WINDOW_NAME)
                    except Exception:
                        pass
                    break
                elif self.is_main_window_closed():
                    print("Exiting due to window closure.")
                    return


@click.command()
@click.option("--input", "-i", required=True, type=click.Path(exists=True), help="Path to input image.")
@click.option("--output", "-o", required=True, type=click.Path(), help="Path to save the warped image.")
@click.option(
    "--width", "-w", required=False, default=1200, type=int, help="Width of the output image", show_default=True
)
@click.option(
    "--height", "-h", required=False, default=800, type=int, help="Height of the output image", show_default=True
)
def main(input: str, output: str, width: int, height: int) -> None:
    """Extract and transform a region from an image using perspective transformation."""
    print("Starting perspective transformation tool...")
    print(f"Input: {input}")
    print(f"Output: {output}")
    print(f"Target dimensions: {width}x{height}")

    transformer = ImageTransformer()
    transformer.process_image(input, output, width, height)


if __name__ == "__main__":
    main()
