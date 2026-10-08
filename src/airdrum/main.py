import logging
import time
import cv2

from airdrum.audio_engine import AudioEngine
from airdrum.camera import Camera
from airdrum.config import AudioConfig, CameraConfig, TrackingConfig
from airdrum.drum_layout import DrumLayout
from airdrum.hand_tracker import HandTracker
from airdrum.preprocess import bgr_to_rgb, mirror_frame
from airdrum.stick_tracker import MotionTracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    cam_config = CameraConfig(width=1280, height=720, fps=60)
    tracker_config = TrackingConfig(max_hands=2)
    audio_config = AudioConfig(buffer_size=256)

    camera = Camera(cam_config)
    tracker = HandTracker(tracker_config, mode="hand")
    layout = DrumLayout("assets/layouts/default.json")
    audio = AudioEngine(audio_config)
    motion_tracker = MotionTracker(min_strike_velocity=220.0, cooldown_seconds=0.10)

    prev_time = time.perf_counter()
    fps_smoothed = 0.0

    try:
        while True:
            ret, frame = camera.read()
            if not ret or frame is None:
                continue

            curr_time = time.perf_counter()
            dt = curr_time - prev_time
            prev_time = curr_time
            if dt > 0:
                instant_fps = 1.0 / dt
                fps_smoothed = (0.9 * fps_smoothed) + (0.1 * instant_fps) if fps_smoothed > 0 else instant_fps

            mirrored = mirror_frame(frame)
            rgb_frame = bgr_to_rgb(mirrored)
            h, w, _ = mirrored.shape

            # Process full resolution frame for accuracy
            tracked_hands = tracker.process(rgb_frame)

            # Decay pad highlight active timers
            for pad in layout.pads:
                if pad.active_timer > 0:
                    pad.active_timer -= dt
                    if pad.active_timer <= 0:
                        pad.is_active = False

            # Collision and velocity strike detection
            for hand in tracked_hands:
                tip = hand.index_tip
                hit_pad = layout.check_collisions(tip.pixel_x, tip.pixel_y, w, h)

                strike = motion_tracker.update_and_detect_strike(
                    hand_label=hand.label,
                    pixel_x=tip.pixel_x,
                    pixel_y=tip.pixel_y,
                    timestamp=curr_time,
                    current_pad_id=hit_pad.id if hit_pad else None,
                )

                if strike and hit_pad:
                    hit_pad.is_active = True
                    hit_pad.active_timer = 0.15
                    audio.play_sound(strike.pad_id, velocity=strike.velocity)

            annotated_frame = layout.draw(mirrored)
            annotated_frame = tracker.draw_landmarks(annotated_frame, tracked_hands)

            mode_label = tracker.mode.upper()
            cv2.putText(
                annotated_frame,
                f"FPS: {fps_smoothed:.1f} | MODE: {mode_label} (Press 'm' to toggle)",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("Air Drum Kit - Main Application", annotated_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("m"):
                tracker.mode = "stick" if tracker.mode == "hand" else "hand"
                logging.info("Switched mode to: %s", tracker.mode.upper())

    finally:
        audio.close()
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()