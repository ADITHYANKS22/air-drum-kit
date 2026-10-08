from dataclasses import dataclass
import logging
import os
import urllib.request
from typing import List, Optional

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from airdrum.config import TrackingConfig

logger = logging.getLogger(__name__)

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"


@dataclass
class HandLandmark:
    x: float  # Normalized coordinate [0.0, 1.0]
    y: float  # Normalized coordinate [0.0, 1.0]
    z: float  # Normalized depth relative to wrist
    pixel_x: int  # Exact frame pixel coordinate X
    pixel_y: int  # Exact frame pixel coordinate Y


@dataclass
class TrackedHand:
    label: str  # 'Left' or 'Right'
    confidence: float  # Classification confidence score
    landmarks: List[HandLandmark]

    @property
    def index_tip(self) -> HandLandmark:
        """Returns Landmark 8 (INDEX_FINGER_TIP)."""
        return self.landmarks[8]

    @property
    def wrist(self) -> HandLandmark:
        """Returns Landmark 0 (WRIST)."""
        return self.landmarks[0]


class HandTracker:
    """Hand tracking implementation using MediaPipe Tasks API (HandLandmarker)."""

    def __init__(self, config: TrackingConfig) -> None:
        self.config = config
        self._ensure_model_exists(self.config.model_path)

        base_options = python.BaseOptions(model_asset_path=self.config.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=self.config.max_hands,
            min_hand_detection_confidence=self.config.min_detection_confidence,
            min_tracking_confidence=self.config.min_tracking_confidence,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        logger.info("HandTracker initialized with model: %s", self.config.model_path)

    def _ensure_model_exists(self, model_path: str) -> None:
        """Downloads official MediaPipe hand_landmarker.task if not present locally."""
        if not os.path.exists(model_path):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            logger.info("Downloading hand_landmarker.task model...")
            urllib.request.urlretrieve(MODEL_URL, model_path)
            logger.info("Model downloaded successfully to %s", model_path)

    def process(self, frame_rgb: np.ndarray) -> List[TrackedHand]:
        """Processes an RGB frame and returns structured tracking data for all detected hands."""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        detection_result = self.detector.detect(mp_image)

        tracked_hands: List[TrackedHand] = []
        if not detection_result.hand_landmarks:
            return tracked_hands

        h, w, _ = frame_rgb.shape

        for i, hand_landmarks in enumerate(detection_result.hand_landmarks):
            label = "Right"
            confidence = 1.0
            if detection_result.handedness and i < len(detection_result.handedness):
                category = detection_result.handedness[i][0]
                label = category.category_name
                confidence = category.score

            landmarks: List[HandLandmark] = []
            for lm in hand_landmarks:
                px = min(int(lm.x * w), w - 1)
                py = min(int(lm.y * h), h - 1)
                landmarks.append(
                    HandLandmark(
                        x=lm.x,
                        y=lm.y,
                        z=lm.z,
                        pixel_x=px,
                        pixel_y=py,
                    )
                )

            tracked_hands.append(
                TrackedHand(label=label, confidence=confidence, landmarks=landmarks)
            )

        return tracked_hands

    def draw_landmarks(self, frame_bgr: np.ndarray, tracked_hands: List[TrackedHand]) -> np.ndarray:
        """Draws target circles at index finger tips and hand labels."""
        output = frame_bgr.copy()
        for hand in tracked_hands:
            tip = hand.index_tip
            cv2.circle(output, (tip.pixel_x, tip.pixel_y), 12, (0, 255, 255), -1)
            cv2.circle(output, (tip.pixel_x, tip.pixel_y), 14, (0, 0, 0), 2)

            wrist = hand.wrist
            cv2.putText(
                output,
                f"{hand.label} ({hand.confidence:.2f})",
                (wrist.pixel_x - 30, wrist.pixel_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
        return output

    def close(self) -> None:
        """Releases detector resources."""
        self.detector.close()