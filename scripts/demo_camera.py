import logging
import time

import cv2

from airdrum.camera import Camera
from airdrum.config import CameraConfig
from airdrum.preprocess import bgr_to_hsv, bgr_to_rgb, gaussian_blur, mirror_frame

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    config = CameraConfig(width=1280, height=720, fps=60)
    camera = Camera(config)

    prev_time = time.perf_counter()
    fps_smoothed = 0.0

    logging.info("Starting live camera feed preview. Press 'q' to quit.")

    try:
        while True:
            ret, frame = camera.read()
            if not ret or frame is None:
                logging.warning("Failed to retrieve frame from camera thread.")
                continue

            # Compute smoothed FPS using exponential moving average
            curr_time = time.perf_counter()
            dt = curr_time - prev_time
            prev_time = curr_time
            if dt > 0:
                instant_fps = 1.0 / dt
                fps_smoothed = (0.9 * fps_smoothed) + (0.1 * instant_fps) if fps_smoothed > 0 else instant_fps

            # Apply Phase 1 Preprocessing steps
            mirrored = mirror_frame(frame)
            blurred = gaussian_blur(mirrored)

            # Draw FPS overlay
            cv2.putText(
                blurred,
                f"FPS: {fps_smoothed:.1f}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("Air Drum Kit - Phase 1 Camera Feed", blurred)

            # Exit when 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()