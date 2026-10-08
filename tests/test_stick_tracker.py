import time
from airdrum.stick_tracker import MotionTracker, StrikeEvent


def test_motion_tracker_strike_detection():
    tracker = MotionTracker(history_size=3, min_strike_velocity=100.0, cooldown_seconds=0.05)
    t0 = time.time()

    # Position 1: y = 100
    strike1 = tracker.update_and_detect_strike("Right", 500, 100, t0, "snare")
    assert strike1 is None

    # Downward stroke: y = 200 over 0.02s (vy = 5000 px/s)
    strike2 = tracker.update_and_detect_strike("Right", 500, 200, t0 + 0.02, "snare")
    assert strike2 is not None
    assert isinstance(strike2, StrikeEvent)
    assert strike2.pad_id == "snare"
    assert strike2.velocity > 0.0


def test_motion_tracker_cooldown():
    tracker = MotionTracker(history_size=3, min_strike_velocity=100.0, cooldown_seconds=0.2)
    t0 = time.time()

    tracker.update_and_detect_strike("Right", 500, 100, t0, "snare")
    strike1 = tracker.update_and_detect_strike("Right", 500, 200, t0 + 0.02, "snare")
    assert strike1 is not None

    # Immediate follow up within cooldown interval should be ignored
    strike2 = tracker.update_and_detect_strike("Right", 500, 250, t0 + 0.04, "snare")
    assert strike2 is None