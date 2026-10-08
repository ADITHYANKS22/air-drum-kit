# 🥁 Computer Vision Air Drum Kit

An interactive, computer-vision-powered virtual air drum kit using OpenCV, MediaPipe, Pygame, and NumPy.

## Features
- **Low-Latency Camera Pipeline**: Threaded frame reader for smooth performance.
- **3D Hand Tracking**: Uses MediaPipe Tasks API (`HandLandmarker`) for hand tracking.
- **Velocity-Sensitive Strikes**: Triggers sounds based on downward fingertip acceleration ($v_y$) and scales audio volume.
- **Polyphonic Audio Engine**: Low-buffer (256 samples) sound playback using `pygame.mixer`.
- **Configurable Layouts**: Customizable drum kit positions via JSON configuration.

## Setup Instructions

1. **Python Version**:
   > **Note**: MediaPipe requires Python 3.10–3.12. If Python 3.14+ is your default, use Python 3.12 with the Python Launcher: `py -3.12`.

2. **Create and Activate a Virtual Environment**:
   ```powershell
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .
   ```

4. **(Optional) Generate Audio Assets**:
   If synthetic drum sounds need to be generated:
   ```powershell
   python scripts/generate_sounds.py
   ```

## Running the Application

### Main Application
Run the complete air drum kit with live camera tracking and sound synthesis:
```powershell
python -m airdrum
# or
python src/airdrum/main.py
```
> Press **`q`** inside the camera window to quit.

### Interactive Phase Demos
You can also run any of the modular demo scripts to test individual subsystems:

- **Camera Feed & Preprocessing**:
  ```powershell
  python scripts/demo_camera.py
  ```
- **Hand Tracking (MediaPipe)**:
  ```powershell
  python scripts/demo_hand_tracking.py
  ```
- **Virtual Drum Layout & Collision**:
  ```powershell
  python scripts/demo_drum_layout.py
  ```
- **Low-Latency Audio Engine**:
  ```powershell
  python scripts/demo_audio.py
  ```

## Running Tests
Execute the unit test suite:
```powershell
pytest
```