import cv2
import numpy as np
import pyglet
from PIL import Image

def cv2glet(img, fmt):
    """Convert OpenCV image to pyglet image format"""
    if fmt == 'GRAY':
        rows, cols = img.shape
        channels = 1
    else:
        rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()
    top_to_bottom_flag = -1
    bytes_per_row = channels * cols
    
    return pyglet.image.ImageData(
        width=cols, 
        height=rows, 
        fmt=fmt, 
        data=raw_img, 
        pitch=top_to_bottom_flag * bytes_per_row
    )


def estimatePoseMarker(corners, mtx, distortion):
    """Estimate marker pose in camera coordinate system"""
    # Calculate marker length from corners
    length = abs(corners[0][0][0] - corners[0][1][0]) if (
        abs(corners[0][0][0] - corners[0][1][0]) > abs(corners[0][0][0] - corners[0][2][0])
    ) else abs(corners[0][0][0] - corners[0][2][0])
    
    marker_points = np.array([
        [-length / 2, length / 2, 0],
        [length / 2, length / 2, 0],
        [length / 2, -length / 2, 0],
        [-length / 2, -length / 2, 0]
    ], dtype=np.float32)
    
    rvecs = []
    tvecs = []
    for c in corners:
        _, r, t = cv2.solvePnP(marker_points, c, mtx, distortion, False, cv2.SOLVEPNP_IPPE_SQUARE)
        rvecs.append(r)
        tvecs.append(t)
        
    return np.array([rvecs]), np.array([tvecs]), length


def get_center_of_marker(corners):
    """Get center coordinates of a marker"""
    # ArUco corners are in format: [top-left, top-right, bottom-right, bottom-left]
    # Calculate center by averaging all 4 corners
    center_x = np.mean([corners[0][0], corners[1][0], corners[2][0], corners[3][0]])
    center_y = np.mean([corners[0][1], corners[1][1], corners[2][1], corners[3][1]])
    return (center_x, center_y)
