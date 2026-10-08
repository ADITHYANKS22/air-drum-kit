import logging
from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class StrikeEvent:
    pad_id: str
    velocity: float  # Normalized playback volume scale [0.3, 1.0]
    timestamp: float


class MotionTracker:
    """Tracks fingertip trajectory to compute velocity vectors and detect drumming strikes."""

    def __init__(
        self,
        history_size: int = 5,
        min_strike_velocity: float = 350.0,  # Minimum downward pixels/sec to trigger
        cooldown_seconds: float = 0.12,
    ) -> None:
        self.history_size = history_size
        self.min_strike_velocity = min_strike_velocity
        self.cooldown_seconds = cooldown_seconds

        self.history: Dict[str, deque] = {
            "Left": deque(maxlen=history_size),
            "Right": deque(maxlen=history_size),
        }
        self.last_strike_time: Dict[str, float] = {"Left": 0.0, "Right": 0.0}

    def update_and_detect_strike(
        self,
        hand_label: str,
        pixel_x: int,
        pixel_y: int,
        timestamp: float,
        current_pad_id: Optional[str],
    ) -> Optional[StrikeEvent]:
        """Updates position history and determines if a downward drum strike occurred."""
        if hand_label not in self.history:
            self.history[hand_label] = deque(maxlen=self.history_size)

        track = self.history[hand_label]
        track.append((timestamp, pixel_x, pixel_y))

        if len(track) < 2 or current_pad_id is None:
            return None

        # Prevent duplicate triggering on the same stroke
        if timestamp - self.last_strike_time.get(hand_label, 0.0) < self.cooldown_seconds:
            return None

        # Calculate vertical velocity vy (positive Y = downward movement)
        t_old, _, y_old = track[0]
        t_new, _, y_new = track[-1]
        dt = t_new - t_old

        if dt <= 0:
            return None

        vy = (y_new - y_old) / dt

        if vy >= self.min_strike_velocity:
            # Map downward velocity (350 px/s - 1800 px/s) to audio volume (0.35 - 1.0)
            norm_velocity = min(1.0, max(0.35, vy / 1800.0))
            self.last_strike_time[hand_label] = timestamp
            logger.debug(
                "Strike detected on %s by %s hand (vy=%.1f px/s, velocity=%.2f)",
                current_pad_id,
                hand_label,
                vy,
                norm_velocity,
            )
            return StrikeEvent(pad_id=current_pad_id, velocity=norm_velocity, timestamp=timestamp)

        return None