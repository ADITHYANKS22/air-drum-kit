
# 🥁 Air Drum Kit

A real-time, velocity-sensitive virtual air drum kit powered by **OpenCV**, **MediaPipe**, and **Pygame**. Play virtual drums in real time using either bare hand gesture tracking or physical drumsticks/colored markers.

---

## ✨ Features

- **Dual Tracking Modes**:
  - **Hand Mode**: Full 21-point hand landmark tracking using MediaPipe Hand Landmarker with dynamic index finger tip detection.
  - **Stick Mode**: High-FPS HSV color tracking with motion persistence and spatial assignment for drumsticks or colored markers.
- **Dynamic Drum Kit Layouts**: Configurable visual hit zones for High Tom, Low Tom, Snare, Hi-Hat, and Crash cymbals.
- **Velocity-Sensitive Audio**: Low-latency audio trigger engine built on Pygame Mixer with velocity detection.
- **HSV Calibration Utility**: Included interactive calibration script to adjust color thresholds for your environment.
- **Layout Editor**: Interactive GUI tool to reposition and re-scale drum pads.

---

## 📁 Repository Structure

```text
air-drum-kit/
├── assets/                  # Drum sound samples and kit layouts
│   └── layouts/default.json # Pad positions and trigger thresholds
├── scripts/
│   ├── demo_hsv_calibration.py # Interactive HSV color calibration tool
│   └── demo_layout_editor.py    # Custom drum pad layout editor
├── src/
│   └── airdrum/
│       ├── audio_engine.py  # Pygame sound triggering logic
│       ├── config.py        # Application configuration settings
│       ├── hand_tracker.py  # MediaPipe & OpenCV tracking engine
│       ├── stick_detector.py# Dedicated marker detection
│       └── main.py          # Main application loop
├── tests/                   # Pytest suite
│   └── test_stick_detector.py
├── pyproject.toml           # Project metadata & dependencies
└── requirements.txt         # Pip dependency locks

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

```

---

### Step-by-Step Commands to Commit & Push

Run these commands in your terminal to update the README on GitHub:

```bash
git add README.md
git commit -m "docs: overhaul README with quickstart, controls, utilities, and repo structure"
git push origin main

```
