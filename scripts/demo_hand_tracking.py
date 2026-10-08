import logging
import time

import cv2

from airdrum.camera import Camera
from airdrum.config import CameraConfig, TrackingConfig
from airdrum.hand_tracker import HandTracker
from airdrum.preprocess import bgr_to_rgb, mirror_frame

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    cam_config = CameraConfig(width=1280, height=720, fps=60)
    tracker_config = TrackingConfig(max_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    camera = Camera(cam_config)
    tracker = HandTracker(tracker_config)

    prev_time = time.perf_counter()
    fps_smoothed = 0.0

    logging.info("Starting Phase 2 Hand Tracking Demo. Press 'q' to exit.")

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

            tracked_hands = tracker.process(rgb_frame)
            annotated_frame = tracker.draw_landmarks(mirrored, tracked_hands)

            cv2.putText(
                annotated_frame,
                f"FPS: {fps_smoothed:.1f} | Hands Detected: {len(tracked_hands)}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("Air Drum Kit - Phase 2 Hand Tracking", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()