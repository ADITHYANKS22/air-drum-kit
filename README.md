# AI-Powered Virtual Air Drum Kit

This project turns a normal laptop webcam into a virtual musical instrument. You can play drums in the air without buying an expensive physical or electronic drum kit.

This README shows how the project works, explains every important design choice, and details the alternatives we considered and why we rejected them.

**Team:** Adithyan K S (Fezul), Ajaykrishna N, Alfred Davies, Akarsh K Bijoy

**Guide:** Dr.Anil Antony, Associate Professor, Department of CSE

**Institution:** Sahrdaya College of Engineering & Technology, Autonomous, Kodakara, Thrissur, Kerala

**Status:** Core pipeline, dual tracking modes, glassmorphism UI, and low-latency audio are fully complete and operational.

---

## How to read this document

We use technical words in this project. To make it easy to understand for everyone, we use this simple rule:

* We explain the idea first in plain words.
* Then we put the technical term and its plain meaning in square brackets.
*Example:* "We smooth out the hand movement to stop jitter `[Exponential Moving Average: a mathematical filter that blends past positions with current positions to remove sudden jumps]`."

---

## Contents

1. [What this project does](https://www.google.com/search?q=%231-what-this-project-does)
2. [Basic ideas you need first](https://www.google.com/search?q=%232-basic-ideas-you-need-first)
3. [System pipeline overview](https://www.google.com/search?q=%233-system-pipeline-overview)
4. [Core modules in detail](https://www.google.com/search?q=%234-core-modules-in-detail)
5. [Decision log (Architectural choices)](https://www.google.com/search?q=%235-decision-log-architectural-choices)
6. [Known limits](https://www.google.com/search?q=%236-known-limits)
7. [Future work](https://www.google.com/search?q=%237-future-work)
8. [How to run and reproduce](https://www.google.com/search?q=%238-how-to-run-and-reproduce)
9. [Glossary](https://www.google.com/search?q=%239-glossary)

---

## 1. What this project does

**Input:** Live video frames from a standard laptop webcam (running at 720p resolution and up to 60 frames per second).

**Output:** Semi-transparent visual drum pads on your screen and real-time audio playback (Snare, Hi-Hat, Crash, Toms) when you strike them.

The project does **not** require special gloves, infrared sensors, or hardware drumsticks. It runs entirely on software using standard computer vision and audio libraries.

---

## 2. Basic ideas you need first

* **Webcam Capture `[Video Stream Input: using software to grab live images frame by frame from the computer camera]`:** The eyes of our program. It reads video frames continuously so it can track your hand or stick movements in real time.
* **Hand Landmarker `[MediaPipe Hands: a pre-trained machine learning model that locates 21 3D joints on a human hand]`:** This tool detects your fingers and wrist coordinates instantly from the video feed.
* **Color Segmentation `[HSV Color Masking: separating objects in an image based on Hue (color type), Saturation (vividness), and Value (brightness)]`:** A computer vision technique used in our stick-tracking mode to isolate specific colored tips (like blue or red tape) from the background.
* **Hit Testing `[Region of Interest (ROI) Collision Detection: checking if a moving coordinate point overlaps with a specific box area on the screen]`:** The logic that decides whether your hand is touching a virtual drum pad.
* **Low-Latency Audio Buffer `[Pygame Mixer: an optimized sound-playing engine configured with a small buffer size to eliminate delay]`:** Ensures that the moment your hand hits a pad, the drum sound plays instantly without noticeable lag.

---

## 3. System pipeline overview

```
Webcam Capture (30-60 FPS)  -->  Preprocessing (OpenCV BGR/RGB/HSV)  -->  Tracking Engine (MediaPipe / HSV Contours)
                                                                                       │
                                                                                       ▼
Audio Synthesis (Pygame Mixer)  <--  Strike Validation (ROI + Velocity + Cooldown)  <--  UI Overlay & Layout (`default.json`)

```

Data flows in a single direction. Each phase passes its cleaned data to the next module. Configuration files (`default.json` for layout, `hsv.json` for color bounds) load dynamically on startup.

---

## 4. Core modules in detail

1. **Camera Module (`camera.py`)**: Manages webcam initialization at 1280x720 resolution, handles frame mirroring for natural user interaction, and ensures safe resource release[cite: 27].
2. **Tracking Module (`hand_tracker.py`)**: Supports two modes[cite: 27]:
* *Bare-hand mode:* Uses MediaPipe to track 21 hand joints[cite: 20, 27, 29].
* *Stick mode:* Uses dynamic HSV color thresholds (`cv2.inRange`) to track colored stick tips[cite: 20, 27]. It includes an `[Exponential Moving Average: a math filter that smooths out cursor jitter]` to keep tracking smooth[cite: 34].


3. **Layout & UI Module (`drum_layout.py` & `default.json`)**: Loads drum pad boundaries dynamically from JSON. It renders a modern [Glassmorphism: a user interface design style featuring semi-transparent frosted-glass visual effects] overlay using OpenCV alpha blending (`cv2.addWeighted`).
4. **Strike Detector (`strike_detector.py`)**: Prevents false hits by checking three strict rules:
* Is the hand/stick inside the pad boundary[cite: 26, 29]?
* Is the downward speed greater than our threshold `[Downward Velocity Check: measuring vertical position change over time (dy/dt) to ensure a deliberate downward strike]`[cite: 21, 27, 30]?
* Has the `[Cooldown State Machine: a timer that blocks rapid double-triggers]` allowed a new hit yet[cite: 21, 27, 30]?


5. **Audio Engine**: Preloads WAV samples into memory using Pygame Mixer with a 256-sample buffer size to guarantee near-zero audio delay[cite: 25, 31].

---

## 5. Decision log (Architectural choices)

### D1. Use a normal laptop webcam instead of physical electronic drums.

* **Decision:** Rely completely on software and a standard webcam.
* **Why:** Physical drum kits are bulky, expensive, and loud. A webcam setup provides an accessible, portable, zero-cost alternative for practice in hostels and compact rooms[cite: 9, 11].
* **Rejected options:** Buying electronic drum hardware or hardware sensors (too costly and not portable).

### D2. Choose OpenCV and MediaPipe over custom deep learning models (like YOLO).

* **Decision:** Use Google MediaPipe and OpenCV HSV filtering.
* **Why:** Heavy deep learning object detection models introduce inference lag, dropping frame rates and creating audio delay. OpenCV and MediaPipe run close to real-time, easily maintaining a smooth **60 FPS** needed for rhythm games[cite: 27].
* **Rejected options:** Training a custom YOLO object detector (too slow for real-time local webcam audio response without a high-end GPU).

### D3. Implement JSON-driven configuration persistence.

* **Decision:** Store layout settings in `assets/layouts/default.json` and color profiles in `assets/layouts/hsv.json`.
* **Why:** Decouples hardcoded variables from source code. Users can recalibrate colors using `demo_hsv_calibration.py` and persist them instantly without rewriting Python code.
* **Rejected options:** Hardcoding coordinates and color ranges inside script files (inflexible and difficult to modify for different room lighting).

### D4. Require velocity and cooldown checks for strike validation.

* **Decision:** Do not trigger sound based on position alone; require downward motion and a time gap between hits.
* **Why:** If position alone triggers sounds, resting or hovering your hand inside a drum box causes continuous accidental noise[cite: 21]. Velocity and cooldown filters eliminate false triggers[cite: 21, 27, 30].
* **Rejected options:** Simple static boundary intersection (leads to messy, unintended sound triggers while hovering).

---

## 6. Known limits

* **Lighting Sensitivity:** In uncontrolled room lighting, HSV color tracking for stick mode may require quick recalibration using the calibration script.
* **No Separate Test Dataset:** Performance metrics are evaluated on validation sessions; real-world varied user trials are ongoing.
* **Single Camera Angle:** Occlusion (when one hand blocks the other from the webcam view) can momentarily affect tracking.

---

## 7. Future work

1. **Multi-Instrument Expansion:** Add virtual cymbals or keyboard layouts.
2. **MIDI File Export:** Record drum sessions directly into standard MIDI formats for music production software.
3. **AI Rhythm Coach:** Introduce automated timing analysis to score the user's rhythm performance.

---

## 8. How to run and reproduce

**Environment Setup:** Python 3.14, OpenCV, MediaPipe, Pygame-CE, NumPy.

1. **Clone and install dependencies:**
```bash
git clone https://github.com/ADITHYANKS22/air-drum-kit.git
cd air-drum-kit
pip install -r requirements.txt

```


2. **Calibrate Stick Colors (Optional):**
```bash
PYTHONPATH=src python3 scripts/demo_hsv_calibration.py

```


*(Adjust trackbars for your colored stick tip and press `q` to save to `assets/layouts/hsv.json`)*
3. **Run the Main Application:**
```bash
PYTHONPATH=src python3 -m airdrum.main

```



---

## 9. Glossary

| Technical Term | Plain Meaning & Explanation |
| --- | --- |
| **Alpha Blending (`cv2.addWeighted`)** | Combining two images (like the camera frame and a semi-transparent colored box) to create a frosted glass visual effect. |
| **Bounding Box (`ROI`)** | A defined rectangular area on the screen representing a virtual drum pad (e.g., Snare, Hi-Hat). |
| **Cooldown State Machine** | A short time delay timer that blocks a single drumstroke from triggering multiple accidental sounds. |
| **Exponential Moving Average (`EMA`)** | A mathematical smoothing filter that averages current coordinates with past frames to eliminate pixel jitter. |
| **Glassmorphism** | A user interface style featuring semi-transparent elements with blurred backgrounds. |
| **HSV Color Segmentation (`cv2.inRange`)** | Filtering video pixels based on Hue (color), Saturation (purity), and Value (brightness) to isolate specific objects. |
| **MediaPipe Hand Landmarker** | A pre-trained Google machine learning model that extracts 3D joints from a human hand. |
| **Polyphonic Audio Playback** | Playing multiple sound samples at the same time without clipping or lagging. |
| **Pygame Mixer** | A fast, low-level audio management library used to load and play WAV sound samples instantly. |
| **Velocity Threshold (`dy/dt`)** | Measuring how fast a coordinate moves downward across frames to confirm a deliberate drum strike. |
