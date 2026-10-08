from typing import List
from airdrum.config import StrikeConfig
from airdrum.drum_layout import DrumLayout
from airdrum.types import StrikeEvent, TrackedPoint


class StrikeDetector:
    def __init__(self, config: StrikeConfig) -> None:
        self.config = config

    def update(self, points: List[TrackedPoint], layout: DrumLayout) -> List[StrikeEvent]:
        raise NotImplementedError("Implemented in Phase 5")
