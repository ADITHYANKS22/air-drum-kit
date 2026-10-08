import numpy as np
from airdrum.config import HSVConfig
from airdrum.stick_detector import StickDetector


def test_stick_detector_synthetic_circle():
    config = HSVConfig(lower_hsv=(35, 100, 100), upper_hsv=(85, 255, 255), min_area=50.0)
    detector = StickDetector(config)

    # Create synthetic BGR frame with a green blob at (300, 200)
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Bright green circle in BGR: (0, 255, 0)
    import cv2
    cv2.circle(img, (300, 200), radius=15, color=(0, 255, 0), thickness=-1)

    centroids, mask = detector.process(img)

    assert len(centroids) == 1
    cx, cy = centroids[0]
    assert abs(cx - 300) <= 2
    assert abs(cy - 200) <= 2
    assert mask[200, 300] == 255