class Config:
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 550
    DEBUG: bool = False
    RESUME_DURATION: float = 3
    ANGULAR_DRAG: float = 0.01
    LINEAR_DRAG: float = 0.005
    GRAVITY: float = 9.81 * 30
    FRUIT_POINTS: int = 10
    OBJECT_INTERVAL: float = 0.8
    BOMB_POINTS: int = -30
    BOMB_CHANCE: float = 0.2
    GAME_OVER_POINT_THRESHOLD: int = 100
    GAMEOBJECT_BASE_SCALE: float = 0.8
    UPDATE_RATE: int = 60
    CONTOUR_SENSITIVITY: int = 27
    MIN_CONTOUR_AREA: int = 1000
    PROCESSING_SCALE: float = 0.6
    
    @staticmethod
    def get_gameobject_base_scale() -> float:
        """Returns the base scale for game objects, relative to a reference width (e.g., 1920)."""
        return (Config.WINDOW_WIDTH / 1920) * 0.9

    @staticmethod
    def get_fruit_speed_range() -> tuple[float, float]:
        """Returns the range of fruit speeds, proportional to window width."""
        return Config.WINDOW_WIDTH * 0.4, Config.WINDOW_WIDTH * 0.6

    # Old
    COLUMN_GAP: int = 10
    IMAGE_ANIMATION_INTERVAL: float = 0.5

    STAGE_TRANSITION_DURATION: float = 1.5
    TEXT_COLOR: tuple[int, int, int] = (255, 255, 255, 255)
    PRIMARY_COLOR: tuple[int, int, int] = (31, 31, 31, 255)
    SECONDARY_COLOR: tuple[int, int, int] = (49, 49, 49, 255)
    SUCCESS_COLOR: tuple[int, int, int] = (32, 253, 58, 255)
    ERROR_COLOR: tuple[int, int, int] = (253, 65, 32, 255)
    WARNING_COLOR: tuple[int, int, int] = (253, 132, 32, 255)
    TRAINING_DATA_SUBSET_SIZE: int = 100
    LIVE_DATA_SUBSET_SIZE: int = 100
    IDLE_DATA_SUBSET_SIZE: int = UPDATE_RATE // 2
