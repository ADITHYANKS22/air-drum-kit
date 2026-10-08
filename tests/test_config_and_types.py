from airdrum.config import AppConfig
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
