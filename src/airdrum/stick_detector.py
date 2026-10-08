import cv2
import numpy as np
from typing import List, Tuple, Optional
from airdrum.config import HSVConfig


class StickDetector:
    """Detects physical drumstick tips using HSV color segmentation."""

    def __init__(self, config: Optional[HSVConfig] = None) -> None:
        self.config = config or HSVConfig()

    def process(self, frame_bgr: np.ndarray) -> Tuple[List[Tuple[int, int]], np.ndarray]:
        """
        Extracts centroid coordinates (x, y) for up to `max_targets` detected tips.
        Returns a tuple of (list of centroids, binary mask).
        """
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        # Threshold the HSV image to get only target color
        lower = np.array(self.config.lower_hsv, dtype=np.uint8)
        upper = np.array(self.config.upper_hsv, dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)

        # Morphological operations to remove small noise artifacts
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        centroids: List[Tuple[int, int]] = []

        # Filter contours by area and sort descending
        valid_contours = [c for c in contours if cv2.contourArea(c) >= self.config.min_area]
        valid_contours = sorted(valid_contours, key=cv2.contourArea, reverse=True)[: self.config.max_targets]

        for cnt in valid_contours:
            M = cv2.moments(cnt)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroids.append((cx, cy))

        # Sort left-to-right to maintain consistent stick mapping
        centroids = sorted(centroids, key=lambda pt: pt[0])

        return centroids, mask