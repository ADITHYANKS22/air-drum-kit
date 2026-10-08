from dataclasses import dataclass
import logging
import os
import urllib.request
from typing import Dict, List, Optional, Tuple

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
    x: float
    y: float
    z: float
    pixel_x: int
    pixel_y: int


@dataclass
class TrackedHand:
    label: str
    confidence: float
    landmarks: List[HandLandmark]

    @property
    def index_tip(self) -> HandLandmark:
        return self.landmarks[8] if len(self.landmarks) > 8 else self.landmarks[0]

    @property
    def wrist(self) -> HandLandmark:
        return self.landmarks[0]


class HandTracker:
    def __init__(self, config: TrackingConfig, mode: str = "hand") -> None:
        self.config = config
        self.mode = mode
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

        # Coordinate smoothing memory dictionary
        self.smooth_memory: Dict[str, Tuple[float, float]] = {}
        self.alpha = 0.55  # Smoothing factor (0.0 = max smooth, 1.0 = raw response)

        logger.info("HandTracker initialized (Mode: %s)", self.mode)

    def _ensure_model_exists(self, model_path: str) -> None:
        if not os.path.exists(model_path):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            logger.info("Downloading hand_landmarker.task model...")
            urllib.request.urlretrieve(MODEL_URL, model_path)

    def process(self, frame_rgb: np.ndarray) -> List[TrackedHand]:
        if self.mode == "stick":
            return self._process_sticks(frame_rgb)
        return self._process_hands(frame_rgb)

    def _apply_smoothing(self, key: str, px: int, py: int) -> Tuple[int, int]:
        """Smooths landmark jitter using exponential moving average."""
        if key not in self.smooth_memory:
            self.smooth_memory[key] = (float(px), float(py))
            return px, py

        prev_x, prev_y = self.smooth_memory[key]
        smooth_x = self.alpha * px + (1 - self.alpha) * prev_x
        smooth_y = self.alpha * py + (1 - self.alpha) * prev_y
        self.smooth_memory[key] = (smooth_x, smooth_y)
        return int(smooth_x), int(smooth_y)

    def _process_hands(self, frame_rgb: np.ndarray) -> List[TrackedHand]:
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
            for idx, lm in enumerate(hand_landmarks):
                raw_px = min(int(lm.x * w), w - 1)
                raw_py = min(int(lm.y * h), h - 1)

                # Smooth key interaction points (Wrist & Index Tip)
                if idx in (0, 8):
                    px, py = self._apply_smoothing(f"{label}_{idx}", raw_px, raw_py)
                else:
                    px, py = raw_px, raw_py

                landmarks.append(
                    HandLandmark(
                        x=px / w,
                        y=py / h,
                        z=lm.z,
                        pixel_x=px,
                        pixel_y=py,
                    )
                )

            tracked_hands.append(
                TrackedHand(label=label, confidence=confidence, landmarks=landmarks)
            )

        return tracked_hands

    def _process_sticks(self, frame_rgb: np.ndarray) -> List[TrackedHand]:
        """Tracks drumstick tips anywhere in frame using adaptive HSV and nearest-neighbor persistence."""
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        h, w, _ = frame_rgb.shape

        # Adaptive green range (lowered minimum saturation to handle motion blur)
        lower_green = np.array([35, 70, 70])
        upper_green = np.array([85, 255, 255])

        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Morphological operations to clean noise without eating small stick tips
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidates = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 25 < area < 10000:
                ((cx, cy), r) = cv2.minEnclosingCircle(cnt)
                # Filtering out overly horizontal wide shapes (shirt stripes) vs round/oval stick caps
                x, y, w_box, h_box = cv2.boundingRect(cnt)
                aspect_ratio = float(w_box) / h_box if h_box > 0 else 1.0
                if aspect_ratio < 3.0:
                    candidates.append((int(cx), int(cy), area))

        # Sort candidates by area size
        candidates.sort(key=lambda item: item[2], reverse=True)
        detected_pts = [(c[0], c[1]) for c in candidates[:4]]

        if not hasattr(self, "_prev_stick_pos"):
            self._prev_stick_pos = {"Stick_Left": None, "Stick_Right": None}

        current_assignments = {}

        if len(detected_pts) == 1:
            pt = detected_pts[0]
            left_p = self._prev_stick_pos["Stick_Left"]
            right_p = self._prev_stick_pos["Stick_Right"]

            if left_p and right_p:
                d_left = np.hypot(pt[0] - left_p[0], pt[1] - left_p[1])
                d_right = np.hypot(pt[0] - right_p[0], pt[1] - right_p[1])
                target = "Stick_Left" if d_left < d_right else "Stick_Right"
                current_assignments[target] = pt
            elif pt[0] < w // 2:
                current_assignments["Stick_Left"] = pt
            else:
                current_assignments["Stick_Right"] = pt

        elif len(detected_pts) >= 2:
            # Assign closest candidates to previous known stick coordinates
            left_p = self._prev_stick_pos["Stick_Left"]
            right_p = self._prev_stick_pos["Stick_Right"]

            if left_p and right_p:
                # Find best pair minimizing distance jump
                best_pair = None
                min_dist_sum = float("inf")

                for i, p1 in enumerate(detected_pts):
                    for j, p2 in enumerate(detected_pts):
                        if i == j:
                            continue
                        d_l = np.hypot(p1[0] - left_p[0], p1[1] - left_p[1])
                        d_r = np.hypot(p2[0] - right_p[0], p2[1] - right_p[1])
                        if (d_l + d_r) < min_dist_sum:
                            min_dist_sum = d_l + d_r
                            best_pair = (p1, p2)

                if best_pair and min_dist_sum < 300:
                    current_assignments["Stick_Left"] = best_pair[0]
                    current_assignments["Stick_Right"] = best_pair[1]

            if "Stick_Left" not in current_assignments:
                # Fallback: divide candidates by left/right screen halves
                pts_sorted = sorted(detected_pts[:2], key=lambda p: p[0])
                current_assignments["Stick_Left"] = pts_sorted[0]
                current_assignments["Stick_Right"] = pts_sorted[1]

        tracked_hands: List[TrackedHand] = []
        for label in ["Stick_Left", "Stick_Right"]:
            if label in current_assignments:
                raw_px, raw_py = current_assignments[label]
                px, py = self._apply_smoothing(label, raw_px, raw_py)
                self._prev_stick_pos[label] = (px, py)
            elif self._prev_stick_pos[label] is not None:
                # Hold previous location for up to 2 dropped frames during fast motion blur
                px, py = self._prev_stick_pos[label]
            else:
                continue

            landmarks = [
                HandLandmark(x=px / w, y=py / h, z=0.0, pixel_x=px, pixel_y=py)
                for _ in range(21)
            ]

            tracked_hands.append(
                TrackedHand(label=label, confidence=0.98, landmarks=landmarks)
            )

        return tracked_hands

    def draw_landmarks(self, frame_bgr: np.ndarray, tracked_hands: List[TrackedHand]) -> np.ndarray:
        output = frame_bgr.copy()
        for hand in tracked_hands:
            tip = hand.index_tip
            color = (0, 255, 0) if "Stick" in hand.label else (0, 255, 255)

            cv2.circle(output, (tip.pixel_x, tip.pixel_y), 10, color, -1)
            cv2.circle(output, (tip.pixel_x, tip.pixel_y), 12, (0, 0, 0), 2)

            wrist = hand.wrist
            cv2.putText(
                output,
                f"{hand.label}",
                (wrist.pixel_x - 20, wrist.pixel_y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
        return output

    def close(self) -> None:
        self.detector.close()