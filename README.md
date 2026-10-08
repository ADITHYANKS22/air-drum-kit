

# 🥁 Air Drum Kit

A real-time, velocity-sensitive virtual air drum kit powered by **OpenCV**, **MediaPipe**, and **Pygame**. Play virtual drums in real time using bare-hand gesture tracking or physical drumsticks/colored markers.

---

## ✨ Features

- **Dual Tracking Modes**:
  - **Hand Mode**: Full 21-point hand landmark tracking using MediaPipe Hand Landmarker with dynamic index finger tip detection.
  - **Stick Mode**: High-FPS HSV color tracking with motion persistence and spatial assignment for drumsticks or colored markers.
- **Dynamic Drum Kit Layouts**: Configurable visual hit zones for High Tom, Low Tom, Snare, Hi-Hat, and Crash cymbals.
- **Velocity-Sensitive Audio**: Low-latency audio trigger engine built on Pygame Mixer with velocity detection.
- **HSV Calibration Utility**: Included interactive calibration script to adjust color thresholds for your environment.
- **Layout Editor & Audio Tools**: Interactive tools to reposition pads and test sound triggering.

---

## 📁 Repository Structure

```text
air-drum-kit/
├── assets/                  # Audio samples and layout templates
│   ├── layouts/             # Saved drum kit JSON configurations
│   ├── models/              # MediaPipe landmark models
│   └── sounds/              # WAV drum audio files (crash, hihat, snare, toms)
├── data/                    # Dataset directory
│   └── raw/                 # Raw tracking / landmark recordings
├── docs/                    # Technical documentation & architecture guides
├── ml/                      # Machine learning model scripts & pipelines
├── scripts/                 # Utility & calibration scripts
│   ├── demo_audio.py        # Audio engine test script
│   ├── demo_camera.py       # Camera feed test script
│   ├── demo_drum_layout.py   # Drum layout renderer preview
│   ├── demo_hand_tracking.py # Standalone hand tracking demo
│   ├── demo_hsv_calibration.py # Interactive HSV color calibration tool
│   ├── demo_layout_editor.py # GUI tool to reposition & resize drum pads
│   └── generate_sounds.py   # Synthetic drum WAV generator
├── src/
│   └── airdrum/             # Main application package
│       ├── audio_engine.py  # Pygame sound triggering engine
│       ├── camera.py        # Webcam video capture wrapper
│       ├── config.py        # Application settings & tracking parameters
│       ├── drum_layout.py   # Pad boundary and collision math
│       ├── hand_tracker.py  # MediaPipe & OpenCV stick/hand tracking
│       ├── main.py          # Main application entry point
│       ├── ml_detector.py   # ML-based gesture detection
│       ├── preprocessor.py  # Frame scaling & HSV filtering utilities
│       ├── stick_detector.py# HSV stick marker tracker
│       ├── strike_detector.py # Z-velocity strike detection engine
│       └── utils.py         # Helper math and geometry functions
├── tests/                   # Pytest test suite
│   ├── test_audio_engine.py
│   ├── test_config_and_types.py
│   ├── test_drum_layout.py
│   ├── test_hand_tracker.py
│   ├── test_preprocessor.py
│   ├── test_stick_detector.py
│   └── test_strike_detector.py
├── .gitignore
├── AGENTS.md
├── LICENSE
├── pyproject.toml           # Project configuration & build settings
├── pytest.ini               # Pytest runtime configuration
├── requirements.txt         # Dependencies list
└── setup_project.py         # Directory bootstrap setup script

```

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone [https://github.com/ADITHYANKS22/air-drum-kit.git](https://github.com/ADITHYANKS22/air-drum-kit.git)
cd air-drum-kit

```

### 2. Set Up Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Run the Main Application

```bash
python -m src.airdrum.main

```

---

## 🎮 Controls & Shortcuts

| Key | Function |
| --- | --- |
| **`m`** | Toggle between **Hand Mode** and **Stick Mode** |
| **`q`** / **`Esc`** | Exit the application |

---

## 🛠️ Utility Scripts

### HSV Color Calibration

If you are using colored sticks/markers, run the calibration script under your ambient room lighting to fine-tune color thresholds:

```bash
python scripts/demo_hsv_calibration.py

```

### Drum Layout Editor

Reposition or resize your drum kit pads visually:

```bash
python scripts/demo_layout_editor.py

```

---

## 🧪 Running Tests

Execute the test suite using `pytest`:

```bash
pytest

```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.

