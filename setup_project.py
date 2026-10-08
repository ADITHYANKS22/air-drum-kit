import os

files = {
    # Package Root & Domain Types
    "src/airdrum/__init__.py": '"""Air Drum Kit package root."""\n',
    "src/airdrum/types.py": '''from dataclasses import dataclass


@dataclass(frozen=True)
class TrackedPoint:
    """Immutable data structure representing a tracked point."""
    pointer_id: str
    x_px: int
    y_px: int
    timestamp_ms: float
    confidence: float


@dataclass(frozen=True)
class StrikeEvent:
    """Immutable data structure representing a drum strike event."""
    pad_name: str
    pointer_id: str
    velocity: float
    timestamp_ms: float
''',

    # Configuration
    "src/airdrum/config.py": '''from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


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
''',

    # Module Stubs
    "src/airdrum/__main__.py": '''import logging

logging.basicConfig(level=logging.INFO)


def main() -> None:
    logging.info("Initializing Virtual Air Drum Kit...")


if __name__ == "__main__":
    main()
''',
    "src/airdrum/camera.py": '''from typing import Optional, Tuple
import numpy as np
from airdrum.config import CameraConfig


class Camera:
    def __init__(self, config: CameraConfig) -> None:
        self.config = config

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        raise NotImplementedError("Implemented in Phase 1")

    def release(self) -> None:
        raise NotImplementedError("Implemented in Phase 1")
''',
    "src/airdrum/preprocess.py": '''from typing import Tuple
import numpy as np


def mirror_frame(frame: np.ndarray) -> np.ndarray:
    raise NotImplementedError("Implemented in Phase 1")


def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    raise NotImplementedError("Implemented in Phase 1")


def bgr_to_hsv(frame: np.ndarray) -> np.ndarray:
    raise NotImplementedError("Implemented in Phase 1")
''',
    "src/airdrum/hand_tracker.py": '''from typing import List
import numpy as np
from airdrum.config import TrackingConfig
from airdrum.types import TrackedPoint


class HandTracker:
    def __init__(self, config: TrackingConfig) -> None:
        self.config = config

    def process(self, frame_rgb: np.ndarray, timestamp_ms: float) -> List[TrackedPoint]:
        raise NotImplementedError("Implemented in Phase 2")
''',
    "src/airdrum/stick_tracker.py": '''from typing import List
import numpy as np
from airdrum.config import TrackingConfig
from airdrum.types import TrackedPoint


class StickTracker:
    def __init__(self, config: TrackingConfig) -> None:
        self.config = config

    def process(self, frame_hsv: np.ndarray, timestamp_ms: float) -> List[TrackedPoint]:
        raise NotImplementedError("Implemented in Phase 3")
''',
    "src/airdrum/drum_layout.py": '''from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from airdrum.types import TrackedPoint


@dataclass
class DrumPad:
    name: str
    rect_norm: Tuple[float, float, float, float]
    sound_file: str
    color_bgr: Tuple[int, int, int]


class DrumLayout:
    def __init__(self, layout_file: str) -> None:
        self.layout_file = layout_file
        self.pads: Dict[str, DrumPad] = {}

    def get_pad_at(self, point: TrackedPoint, frame_width: int, frame_height: int) -> Optional[str]:
        raise NotImplementedError("Implemented in Phase 4")
''',
    "src/airdrum/strike_detector.py": '''from typing import List
from airdrum.config import StrikeConfig
from airdrum.drum_layout import DrumLayout
from airdrum.types import StrikeEvent, TrackedPoint


class StrikeDetector:
    def __init__(self, config: StrikeConfig) -> None:
        self.config = config

    def update(self, points: List[TrackedPoint], layout: DrumLayout) -> List[StrikeEvent]:
        raise NotImplementedError("Implemented in Phase 5")
''',
    "src/airdrum/ml_detector.py": '''from typing import List
from airdrum.drum_layout import DrumLayout
from airdrum.types import StrikeEvent, TrackedPoint


class MLStrikeDetector:
    def __init__(self, model_path: str) -> None:
        self.model_path = model_path

    def update(self, points: List[TrackedPoint], layout: DrumLayout) -> List[StrikeEvent]:
        raise NotImplementedError("Implemented in Phase 7")
''',
    "src/airdrum/audio_engine.py": '''from airdrum.config import AudioConfig


class AudioEngine:
    def __init__(self, config: AudioConfig) -> None:
        self.config = config

    def play(self, pad_name: str, volume: float = 1.0) -> None:
        raise NotImplementedError("Implemented in Phase 4")
''',
    "src/airdrum/ui.py": '''import numpy as np
from airdrum.drum_layout import DrumLayout


def render_overlay(frame: np.ndarray, layout: DrumLayout, fps: float) -> np.ndarray:
    raise NotImplementedError("Implemented in Phase 6")
''',
    "src/airdrum/main.py": '''from airdrum.config import AppConfig


def run_app(config: AppConfig) -> None:
    raise NotImplementedError("Implemented in Phase 6")
''',

    # Project Metadata & Environment
    "requirements.txt": "opencv-python>=4.8.0\nmediapipe>=0.10.0\npygame>=2.5.0\nnumpy>=1.24.0\nscikit-learn>=1.3.0\npandas>=2.0.0\nmatplotlib>=3.7.0\njoblib>=1.3.0\npytest>=7.4.0\n",
    ".gitignore": ".venv/\n__pycache__/\n*.pyc\n.pytest_cache/\n*.egg-info/\ndist/\nbuild/\ndata/raw/*.csv\n*.joblib\n.DS_Store\nsetup_project.py\n",
    "LICENSE": "MIT License\n\nCopyright (c) 2026\n",
    "AGENTS.md": "Master Context Prompt for Air Drum Kit Project.\n",
    "README.md": "# AI-Powered Virtual Air Drum Kit\n",

    # Unit Tests
    "tests/test_config_and_types.py": '''from airdrum.config import AppConfig
from airdrum.types import TrackedPoint


def test_default_config_instantiation():
    config = AppConfig()
    assert config.camera.width == 1280
    assert config.audio.buffer_size == 256


def test_tracked_point_immutability():
    point = TrackedPoint("left_index", 100, 200, 1000.0, 0.95)
    assert point.x_px == 100
    try:
        point.x_px = 150
        assert False, "TrackedPoint should be immutable"
    except Exception:
        pass
''',

    # Placeholder Folders
    "assets/models/.gitkeep": "",
    "assets/sounds/.gitkeep": "",
    "assets/layouts/.gitkeep": "",
    "ml/.gitkeep": "",
    "data/raw/.gitkeep": "",
    "scripts/.gitkeep": "",
    "docs/.gitkeep": "",
}

for path, content in files.items():
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {path}")

print("\nProject scaffold created successfully!")