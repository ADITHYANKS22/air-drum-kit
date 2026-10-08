import logging
import time

import cv2

from airdrum.audio_engine import AudioEngine
from airdrum.camera import Camera
from airdrum.config import AudioConfig, CameraConfig, TrackingConfig
from airdrum.drum_layout import DrumLayout
from airdrum.hand_tracker import HandTracker
from airdrum.preprocess import bgr_to_rgb, mirror_frame

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    cam_config = CameraConfig(width=1280, height=720, fps=60)
    tracker_config = TrackingConfig(max_hands=2)
    audio_config = AudioConfig(buffer_size=256)

    camera = Camera(cam_config)
    tracker = HandTracker(tracker_config)
    layout = DrumLayout("assets/layouts/default.json")
    audio = AudioEngine(audio_config)

    prev_time = time.perf_counter()
    fps_smoothed = 0.0

    # Track hit state per pad to avoid sound spamming on simple hover
    prev_active_pads = set()

    logging.info("Starting Phase 4 Low-Latency Audio Demo. Press 'q' to exit.")

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

            tracked_hands = tracker.process(rgb_frame)

            for pad in layout.pads:
                pad.is_active = False

            current_active_pads = set()
            for hand in tracked_hands:
                tip = hand.index_tip
                hit_pad = layout.check_collisions(tip.pixel_x, tip.pixel_y, w, h)
                if hit_pad:
                    hit_pad.is_active = True
                    current_active_pads.add(hit_pad.id)

                    # Trigger audio on edge detection (when finger newly enters pad area)
                    if hit_pad.id not in prev_active_pads:
                        audio.play_sound(hit_pad.id, velocity=0.9)

            prev_active_pads = current_active_pads

            annotated_frame = layout.draw(mirrored)
            annotated_frame = tracker.draw_landmarks(annotated_frame, tracked_hands)

            cv2.putText(
                annotated_frame,
                f"FPS: {fps_smoothed:.1f} | Pygame Audio Ready",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("Air Drum Kit - Phase 4 Audio Engine", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        audio.close()
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()