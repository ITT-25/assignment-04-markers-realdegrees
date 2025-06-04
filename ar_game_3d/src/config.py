import numpy as np

# Window configuration
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_Z = 420

# Game configuration
INTERACTION_DISTANCE = 150  # Distance for characters to recognize each other
ATTACK_COOLDOWN = 2.0  # Seconds between attacks

# Matrix constants
INVERSE_MATRIX = np.array(
    [[1.0, 1.0, 1.0, 1.0], [-1.0, -1.0, -1.0, -1.0], [-1.0, -1.0, -1.0, -1.0], [1.0, 1.0, 1.0, 1.0]]
)

# Camera configuration
CAMERA_MATRIX = np.array(
    [[534.34144579, 0.0, 339.15527836], [0.0, 534.68425882, 233.84359494], [0.0, 0.0, 1.0]], dtype=np.float64
)

DIST_COEFFS = np.array([0, 0, 0, 0], dtype=np.float64)
