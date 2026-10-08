from dataclasses import dataclass
import logging
import platform
import threading
import time
from typing import Optional, Tuple

import cv2
import numpy as np

from airdrum.config import CameraConfig

logger = logging.getLogger(__name__)


class Camera:
    """Threaded webcam reader to prevent frame buffer accumulation and lag."""

    def __init__(self, config: CameraConfig) -> None:
        self.config = config
        
        # Select OpenCV backend based on operating system
        backend = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(self.config.device_index, backend)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Could not open camera at index {self.config.device_index}. "
                "Ensure webcam is connected and not in use by another application."
            )

        # Configure requested frame dimensions and frame rate
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)

        # Capture state & lock
        self._lock = threading.Lock()
        self._latest_frame: Optional[np.ndarray] = None
        self._running = True

        # Read initial frame to verify camera output
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.cap.release()
            raise RuntimeError("Camera opened successfully but failed to capture initial frame.")

        self._latest_frame = frame

        # Start asynchronous background thread
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()
        logger.info(
            "Camera thread started: Resolution %dx%d @ %d FPS requested",
            self.config.width,
            self.config.height,
            self.config.fps,
        )

    def _update_loop(self) -> None:
        """Background thread loop continuously polling camera hardware."""
        while self._running:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self._lock:
                    self._latest_frame = frame
            else:
                time.sleep(0.005)

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Returns the most recent frame captured by the background thread."""
        with self._lock:
            if self._latest_frame is None:
                return False, None
            return True, self._latest_frame.copy()

    def release(self) -> None:
        """Stops background thread and releases camera hardware."""
        self._running = False
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self.cap.isOpened():
            self.cap.release()
        logger.info("Camera device released cleanly.")