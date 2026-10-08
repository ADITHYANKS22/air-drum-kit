# 🥁 Computer Vision Air Drum Kit

An interactive, computer-vision-powered virtual air drum kit using OpenCV, MediaPipe, Pygame, and NumPy.

## Features
- **Low-Latency Camera Pipeline**: Threaded frame reader for smooth performance.
- **3D Hand Tracking**: Uses MediaPipe Tasks API (`HandLandmarker`) for hand tracking.
- **Velocity-Sensitive Strikes**: Triggers sounds based on downward fingertip acceleration ($v_y$) and scales audio volume.
- **Polyphonic Audio Engine**: Low-buffer (256 samples) sound playback using `pygame.mixer`.
- **Configurable Layouts**: Customizable drum kit positions via JSON configuration.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/air-drum-kit.git](https://github.com/YOUR_USERNAME/air-drum-kit.git)
   cd air-drum-kit