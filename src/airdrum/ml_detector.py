from typing import List
from airdrum.drum_layout import DrumLayout
from airdrum.types import StrikeEvent, TrackedPoint


class MLStrikeDetector:
    def __init__(self, model_path: str) -> None:
        self.model_path = model_path

    def update(self, points: List[TrackedPoint], layout: DrumLayout) -> List[StrikeEvent]:
        raise NotImplementedError("Implemented in Phase 7")
