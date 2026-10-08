import numpy as np
from airdrum.config import TrackingConfig
from airdrum.hand_tracker import HandTracker


def test_hand_tracker_empty_frame():
    config = TrackingConfig(max_hands=2)
    tracker = HandTracker(config)

    blank_rgb = np.zeros((480, 640, 3), dtype=np.uint8)
    results = tracker.process(blank_rgb)

    assert isinstance(results, list)
    assert len(results) == 0

    tracker.close()