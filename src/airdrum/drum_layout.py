import json
import logging
import os
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DrumPad:
    id: str
    name: str
    x: float          # Normalized X origin [0.0, 1.0]
    y: float          # Normalized Y origin [0.0, 1.0]
    width: float      # Normalized width [0.0, 1.0]
    height: float     # Normalized height [0.0, 1.0]
    color: Tuple[int, int, int]  # BGR color tuple
    sound_file: str
    is_active: bool = False
    active_timer: float = 0.0

    def contains_point(self, px: int, py: int, frame_width: int, frame_height: int) -> bool:
        """Checks if exact pixel coordinates (px, py) fall within pad bounding box."""
        left = int(self.x * frame_width)
        top = int(self.y * frame_height)
        right = left + int(self.width * frame_width)
        bottom = top + int(self.height * frame_height)

        return left <= px <= right and top <= py <= bottom


class DrumLayout:
    """Manages virtual drum pad configurations, collision checking, and UI rendering."""

    def __init__(self, layout_path: str = "assets/layouts/default.json") -> None:
        self.layout_path = layout_path
        self.pads: List[DrumPad] = []
        self.load_layout(layout_path)

    def load_layout(self, path: str) -> None:
        """Loads pad definitions from a JSON file."""
        if not os.path.exists(path):
            logger.warning("Layout path %s not found. Initializing empty layout.", path)
            return

        with open(path, "r") as f:
            data = json.load(f)

        self.pads = []
        for p in data.get("pads", []):
            color = tuple(p.get("color", [0, 255, 0]))
            self.pads.append(
                DrumPad(
                    id=p["id"],
                    name=p["name"],
                    x=p["x"],
                    y=p["y"],
                    width=p["width"],
                    height=p["height"],
                    color=(color[0], color[1], color[2]),
                    sound_file=p.get("sound_file", ""),
                )
            )
        logger.info("Loaded %d drum pads from %s", len(self.pads), path)

    def check_collisions(self, point_x: int, point_y: int, frame_w: int, frame_h: int) -> Optional[DrumPad]:
        """Returns the DrumPad colliding with the specified pixel point, if any."""
        for pad in self.pads:
            if pad.contains_point(point_x, point_y, frame_w, frame_h):
                return pad
        return None

    def draw(self, frame_bgr: np.ndarray) -> np.ndarray:
        """Renders semi-transparent drum pads onto the frame."""
        h, w, _ = frame_bgr.shape
        overlay = frame_bgr.copy()

        for pad in self.pads:
            left = int(pad.x * w)
            top = int(pad.y * h)
            pad_w = int(pad.width * w)
            pad_h = int(pad.height * h)
            right = left + pad_w
            bottom = top + pad_h

            # Choose stroke/fill based on active hit state
            fill_color = pad.color if pad.is_active else (50, 50, 50)
            alpha = 0.65 if pad.is_active else 0.35

            # Semi-transparent pad rectangle
            cv2.rectangle(overlay, (left, top), (right, bottom), fill_color, -1)
            cv2.rectangle(frame_bgr, (left, top), (right, bottom), pad.color, 2)

            # Pad name text
            text_size, _ = cv2.getTextSize(pad.name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            text_x = left + (pad_w - text_size[0]) // 2
            text_y = top + (pad_h + text_size[1]) // 2

            cv2.putText(
                frame_bgr,
                pad.name,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        # Blend semi-transparent shapes into the main frame
        cv2.addWeighted(overlay, 0.4, frame_bgr, 0.6, 0, frame_bgr)
        return frame_bgr