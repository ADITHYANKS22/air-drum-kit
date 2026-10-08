import logging
import time

import cv2

from airdrum.camera import Camera
from airdrum.config import CameraConfig, TrackingConfig
from airdrum.drum_layout import DrumLayout
from airdrum.hand_tracker import HandTracker
from airdrum.preprocess import bgr_to_rgb, mirror_frame

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    cam_config = CameraConfig(width=1280, height=720, fps=60)
    tracker_config = TrackingConfig(max_hands=2)

    camera = Camera(cam_config)
    tracker = HandTracker(tracker_config)
    layout = DrumLayout("assets/layouts/default.json")

    prev_time = time.perf_counter()
    fps_smoothed = 0.0

    logging.info("Starting Phase 3 Drum Layout Demo. Press 'q' to exit.")

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

            # Reset pad states
            for pad in layout.pads:
                pad.is_active = False

            # Perform collision detection for all detected index finger tips
            active_pad_names = []
            for hand in tracked_hands:
                tip = hand.index_tip
                hit_pad = layout.check_collisions(tip.pixel_x, tip.pixel_y, w, h)
                if hit_pad:
                    hit_pad.is_active = True
                    active_pad_names.append(hit_pad.name)

            # Render drum layout and hand landmark overlays
            annotated_frame = layout.draw(mirrored)
            annotated_frame = tracker.draw_landmarks(annotated_frame, tracked_hands)

            # Render HUD
            status = f"Active Pads: {', '.join(active_pad_names)}" if active_pad_names else "Active Pads: None"
            cv2.putText(
                annotated_frame,
                f"FPS: {fps_smoothed:.1f} | {status}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("Air Drum Kit - Phase 3 Virtual Drum Layout", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()