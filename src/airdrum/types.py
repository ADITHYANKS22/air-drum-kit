from dataclasses import dataclass


@dataclass(frozen=True)
class TrackedPoint:
    """Immutable data structure representing a tracked point."""
    pointer_id: str
    x_px: int
    y_px: int
    timestamp_ms: float
    confidence: float


@dataclass(frozen=True)
class StrikeEvent:
    """Immutable data structure representing a drum strike event."""
    pad_name: str
    pointer_id: str
    velocity: float
    timestamp_ms: float
