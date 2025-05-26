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
                # Draw lines between all points to form a quadrilateral
                cv2.line(self.display_image, self.points[0], self.points[1], (0, 255, 0), 2)
                cv2.line(self.display_image, self.points[1], self.points[2], (0, 255, 0), 2)
                cv2.line(self.display_image, self.points[2], self.points[3], (0, 255, 0), 2)
                cv2.line(self.display_image, self.points[3], self.points[0], (0, 255, 0), 2)
                self.points = ordered_points

            cv2.imshow(MAIN_WINDOW_NAME, self.display_image)

    def transform_perspective(self, image: np.ndarray, points: np.ndarray, *, width: int, height: int, copy: bool = False) -> np.ndarray:
        """Apply perspective transformation based on selected points"""
        print("Applying perspective transformation...")        
        dst_pts = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype=np.float32)

        print(f"Source points (ordered): {points}")
        print(f"Destination points: {dst_pts}")
        
        matrix = cv2.getPerspectiveTransform(points, dst_pts)
        if copy:
            image = image.copy()
        return cv2.warpPerspective(image, matrix, (width, height))

    # ? This is required because apparently the order of points influences the final "perspective origin" so by manually reordering it outputs the result image at the same rotation as the original image
    def order_points(self, points: List[Tuple[int, int]]) -> Optional[np.ndarray]:
        """Sort 4 points into top-left, top-right, bottom-right, bottom-left."""
        print("Ordering points for consistent transformation...")
        points_np = np.array(points, dtype="float32")
        
        if len(points_np) != 4:
            return

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
            return
        
        return np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")
            
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
            warped_image = self.transform_perspective(self.original_image, self.points, width=self.width, height=self.height)
            
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
                    cv2.destroyWindow(RESULT_WINDOW_NAME)
                    break
                elif key == ESCAPE_KEY:
                    print("Restarting selection...")
                    cv2.destroyWindow(RESULT_WINDOW_NAME)
                    break
                elif self.is_main_window_closed():
                    print("Exiting due to window closure.")
                    return
            
            


@click.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True), help='Path to input image.')
@click.option('--output', '-o', required=True, type=click.Path(), help='Path to save the warped image.')
@click.option('--width', '-w', required=False, default=1200, type=int, help='Width of the output image. (Default: 1200)')
@click.option('--height', '-h', required=False, default=800, type=int, help='Height of the output image. (Default: 800)')
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
