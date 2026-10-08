import cv2
import numpy as np
from airdrum.camera import Camera
from airdrum.config import CameraConfig


def nothing(x):
    pass


def main():
    camera = Camera(CameraConfig(width=1280, height=720))
    cv2.namedWindow("HSV Calibration")

    # Create trackbars for color change
    cv2.createTrackbar("LH", "HSV Calibration", 35, 179, nothing)
    cv2.createTrackbar("LS", "HSV Calibration", 100, 255, nothing)
    cv2.createTrackbar("LV", "HSV Calibration", 100, 255, nothing)
    cv2.createTrackbar("UH", "HSV Calibration", 85, 179, nothing)
    cv2.createTrackbar("US", "HSV Calibration", 255, 255, nothing)
    cv2.createTrackbar("UV", "HSV Calibration", 255, 255, nothing)

    print("Hold your colored drumstick tip in front of the camera and adjust trackbars.")
    print("Press 'q' to print final HSV values and exit.")

    try:
        while True:
            ret, frame = camera.read()
            if not ret or frame is None:
                continue

            frame = cv2.flip(frame, 1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            lh = cv2.getTrackbarPos("LH", "HSV Calibration")
            ls = cv2.getTrackbarPos("LS", "HSV Calibration")
            lv = cv2.getTrackbarPos("LV", "HSV Calibration")
            uh = cv2.getTrackbarPos("UH", "HSV Calibration")
            us = cv2.getTrackbarPos("US", "HSV Calibration")
            uv = cv2.getTrackbarPos("UV", "HSV Calibration")

            lower = np.array([lh, ls, lv])
            upper = np.array([uh, us, uv])

            mask = cv2.inRange(hsv, lower, upper)
            result = cv2.bitwise_and(frame, frame, mask=mask)

            combined = np.hstack((frame, result))
            cv2.imshow("HSV Calibration", combined)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print(f"\nFinal HSV Bounds:\nLower: ({lh}, {ls}, {lv})\nUpper: ({uh}, {us}, {uv})")
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()