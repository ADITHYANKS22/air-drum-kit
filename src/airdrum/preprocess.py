from typing import Tuple
import cv2
import numpy as np


def mirror_frame(frame: np.ndarray) -> np.ndarray:
    """Flips frame horizontally to act like a natural user mirror."""
    return cv2.flip(frame, 1)


def gaussian_blur(frame: np.ndarray, kernel_size: Tuple[int, int] = (5, 5)) -> np.ndarray:
    """Applies Gaussian Blur to smooth out high-frequency noise."""
    return cv2.GaussianBlur(frame, kernel_size, 0)


def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    """Converts OpenCV default BGR channel order to RGB for MediaPipe."""
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def bgr_to_hsv(frame: np.ndarray) -> np.ndarray:
    """Converts BGR image to HSV color space for color segmentation."""
    return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)