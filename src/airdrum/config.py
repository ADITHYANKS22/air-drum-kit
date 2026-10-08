from dataclasses import dataclass, field
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

from typing import Tuple


@dataclass
class HSVConfig:
    """HSV color thresholding configuration for physical drumstick tips."""
    # Default HSV bounds tuned for bright green tape/tips
    lower_hsv: Tuple[int, int, int] = (35, 100, 100)
    upper_hsv: Tuple[int, int, int] = (85, 255, 255)
    min_area: float = 100.0  # Minimum pixel area to filter out noise
    max_targets: int = 2     # Track up to 2 stick tips (Left / Right)


@dataclass
class CameraConfig:
    device_index: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 60


@dataclass
class TrackingConfig:
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.7
    max_hands: int = 2
    model_path: str = "assets/models/hand_landmarker.task"
    hsv_config_path: str = "assets/layouts/hsv.json"


@dataclass
class StrikeConfig:
    velocity_threshold: float = 1.0
    cooldown_ms: float = 120.0
    smoothing_window: int = 5
    min_confidence: float = 0.5


@dataclass
class AudioConfig:
    sample_rate: int = 44100
    bit_depth: int = -16
    channels: int = 2
    buffer_size: int = 256
    polyphony_channels: int = 16


@dataclass
class AppConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    strike: StrikeConfig = field(default_factory=StrikeConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    layout_path: str = "assets/layouts/default.json"
