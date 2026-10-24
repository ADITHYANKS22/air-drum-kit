# System Diagrams & Architecture Specifications
**Project:** Computer Vision & AI-Powered Virtual Air Drum Kit  
**Repository:** [air-drum-kit](file:///e:/Code%20Stuffs/AntiGravity%20Projects/Airdrum/air-drum-kit)  
**Date:** October 2026  

---

## 1. System Pipeline Flowchart (Main Runtime Loop)
This flowchart models the end-to-end execution path from hardware webcam frame polling to audio output and visual glassmorphism rendering.

```mermaid
flowchart TD
    Start([Application Start: python -m airdrum]) --> Init[Initialize Camera, Tracker, AudioEngine, DrumLayout]
    Init --> AudioInit[Pygame Mixer Buffer = 256 samples, 16 Channels]
    AudioInit --> LoadLayout[Load Layout JSON: assets/layouts/default.json]
    LoadLayout --> CamLoop[/Camera Capture Thread reads Frame/]
    
    CamLoop --> Preproc[Preprocessing: Mirror Frame cv2.flip & Convert BGR to RGB]
    Preproc --> ModeCheck{Tracking Mode?}
    
    ModeCheck -- Hand Mode --> MediaPipe[MediaPipe HandLandmarker Task]
    MediaPipe --> ExtractLandmarks[Extract 21 Landmarks -> Landmark 8 Index Fingertip]
    
    ModeCheck -- Stick Mode --> HSVFilter[HSV Thresholding cv2.inRange & Contours]
    HSVFilter --> Centroid[Calculate Minimum Enclosing Circle Centroid]
    
    ExtractLandmarks --> EMAFilter[Apply Exponential Moving Average Smoothing alpha=0.1]
    Centroid --> EMAFilter
    
    EMAFilter --> PadCollision{Coordinate inside Pad ROI?}
    PadCollision -- No --> RenderIdle[Render Idle Glassmorphic Pad 30% Opacity]
    
    PadCollision -- Yes --> VelocityCheck{Downward Velocity vy >= 180 px/s?}
    VelocityCheck -- No --> RenderIdle
    
    VelocityCheck -- Yes --> CooldownCheck{Cooldown Timer >= 150ms Elapsed?}
    CooldownCheck -- No / Blocked --> RenderIdle
    
    CooldownCheck -- Yes / Passed --> TriggerEvent[Generate StrikeEvent]
    
    TriggerEvent --> AudioPlay[AudioEngine: Playback WAV Sample via Pygame Mixer]
    TriggerEvent --> ResetCooldown[Reset Pad Cooldown Timer & Set Active Highlight]
    
    AudioPlay --> Overlay[Alpha Blend Glassmorphism UI cv2.addWeighted 65% Opacity]
    RenderIdle --> Overlay
    ResetCooldown --> Overlay
    
    Overlay --> Display[/Display Frame in OpenCV Window/]
    Display --> ExitCheck{Key Pressed == 'q'?}
    ExitCheck -- No --> CamLoop
    ExitCheck -- Yes --> Cleanup[Release Camera, Stop Mixer, Close Windows]
    Cleanup --> Stop([End Application])
```

---

## 2. Entity-Relationship (ER) / Data Model Diagram
Although this application uses an in-memory runtime object architecture and JSON persistence rather than a relational database, the data entities, attributes, and relationships map as follows:

```mermaid
erDiagram
    CONFIG ||--|| CAMERA_CONFIG : defines
    CONFIG ||--|| TRACKING_CONFIG : defines
    CONFIG ||--|| AUDIO_CONFIG : defines

    CONFIG {
        string app_name
        string layout_file
        string hsv_file
        boolean debug_mode
    }

    CAMERA_CONFIG {
        int width
        int height
        int target_fps
        int backend_api
    }

    TRACKING_CONFIG {
        string mode
        int max_hands
        float min_detection_confidence
        float min_tracking_confidence
        float smoothing_alpha
    }

    AUDIO_CONFIG {
        int sample_rate
        int buffer_size
        int channels
        int bit_depth
    }

    DRUM_LAYOUT ||--|{ DRUM_PAD : contains
    DRUM_LAYOUT {
        string layout_name
        int total_pads
        string source_json_path
    }

    DRUM_PAD ||--o| AUDIO_SAMPLE : plays
    DRUM_PAD {
        string id PK
        string name
        float x_rel
        float y_rel
        float width_rel
        float height_rel
        int rgb_color
        float cooldown_ms
        float active_timer
        boolean is_active
    }

    AUDIO_SAMPLE {
        string file_name PK
        string sound_type
        int duration_ms
        binary pcm_data
    }

    TRACKED_POINT ||--o{ STRIKE_EVENT : causes
    TRACKED_POINT {
        string pointer_id PK
        int x_px
        int y_px
        float timestamp_ms
        float confidence
        float velocity_y
    }

    STRIKE_EVENT }|--|| DRUM_PAD : targets
    STRIKE_EVENT {
        string event_id PK
        string pad_id FK
        string pointer_id FK
        float velocity
        float volume_scale
        float timestamp_ms
    }
```

---

## 3. High-Level Modular System Architecture Diagram
Illustrates the separation of concerns across physical capture, machine perception, kinematic state analysis, audio synthesis, and visual rendering.

```mermaid
flowchart LR
    subgraph Hardware ["Hardware Layer"]
        CAM["Laptop / USB Webcam"]
        SPK["Speakers / Headphones"]
    end

    subgraph Perception ["Perception & Tracking Pipeline"]
        direction TB
        CAP["Camera Module\n(Threaded Buffer Reader)"]
        PRE["Preprocessor\n(Mirror + BGR/RGB/HSV)"]
        MP["MediaPipe HandLandmarker\n(21 3D Joint Extraction)"]
        HSV["HSV Contour Tracker\n(Colored Marker Mode)"]
        EMA["EMA Smoothing Filter\n(Jitter Reduction)"]
    end

    subgraph Kinematics ["Kinematic Strike Detection Engine"]
        direction TB
        ROI["ROI Spatial Collision\n(2D Normalized Coordinates)"]
        VEL["Kinematic Velocity Gate\n(dy / dt >= 180 px/s)"]
        COOL["Cooldown State Machine\n(150 ms Debounce)"]
    end

    subgraph Presentation ["Audio & UI Presentation Layer"]
        direction TB
        MIXER["Pygame Mixer Engine\n(256 Samples, 16 Channels)"]
        UI["Glassmorphic UI Overlay\n(cv2.addWeighted Alpha Blend)"]
        DISP["OpenCV HighGUI Window"]
    end

    CAM --> CAP
    CAP --> PRE
    PRE --> MP
    PRE --> HSV
    MP --> EMA
    HSV --> EMA
    EMA --> ROI
    ROI --> VEL
    VEL --> COOL
    COOL -->|Strike Validated| MIXER
    COOL -->|Visual State Update| UI
    PRE --> UI
    MIXER --> SPK
    UI --> DISP
```

---

## 4. Strike Detector State Machine Diagram
Depicts the state transitions for each virtual drum pad to ensure false strikes (resting hands or micro-rebound oscillations) are rejected.

```mermaid
stateDiagram-v2
    [*] --> Idle : System Initialized

    Idle --> Hovering : Pointer enters Pad ROI (Left <= X <= Right, Top <= Y <= Bottom)
    Hovering --> Idle : Pointer leaves Pad ROI

    Hovering --> Strike_Detected : Downward Velocity (vy >= 180 px/s)
    
    state Strike_Detected {
        [*] --> CheckCooldown
        CheckCooldown --> Rejected_InCooldown : Timer < 150 ms
        CheckCooldown --> Accepted : Timer >= 150 ms
    }

    Rejected_InCooldown --> Hovering : Ignore hit / No audio
    
    Accepted --> Active_Audio : Play WAV (Pygame Mixer) & Set Pad Active (65% Opacity)
    Active_Audio --> Cooldown_Recovery : Reset Cooldown Timer (150 ms) & Decay Timer (100 ms)
    
    Cooldown_Recovery --> Hovering : Cooldown Expired (Pointer still inside ROI)
    Cooldown_Recovery --> Idle : Cooldown Expired (Pointer exited ROI)
```

---

## 5. Sequence Diagram: Frame Processing & Hit Handling
Chronological interaction across software classes during a live drumming strike.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Cam as Camera Thread
    participant Main as Main Loop
    participant Tracker as HandTracker / StickTracker
    participant Layout as DrumLayout
    participant Motion as MotionTracker
    participant Audio as AudioEngine
    participant Screen as OpenCV Display

    User->>Cam: Physical hand stroke downward
    Cam->>Main: Yield latest frame (1280x720)
    Main->>Tracker: process(rgb_frame)
    Tracker-->>Main: return TrackedPoint (x, y, timestamp)
    
    Main->>Layout: check_collisions(x, y, w, h)
    Layout-->>Main: return DrumPad (snare)
    
    Main->>Motion: register_point_and_check_strike(pointer_id, x, y, timestamp)
    Note over Motion: Compute dy/dt & verify cooldown
    Motion-->>Main: return is_strike (True, velocity=240.0)
    
    par Trigger Audio
        Main->>Audio: play("snare.wav", volume=0.85)
        Audio-->>User: Low-latency sound playback (~5.8 ms buffer)
    and Update UI State
        Main->>Layout: activate_pad("snare", duration=0.10s)
    end

    Main->>Layout: draw(frame)
    Layout-->>Screen: cv2.imshow("Air Drum Kit", blended_frame)
    Screen-->>User: Visual feedback (highlighted pad)
```

---

## 6. Component Class Diagram (UML)
Shows the object-oriented structure and module dependencies.

```mermaid
classDiagram
    class Camera {
        -CameraConfig config
        -VideoCapture cap
        -Thread capture_thread
        -Lock lock
        -ndarray latest_frame
        +read() tuple[bool, ndarray]
        +release() void
    }

    class HandTracker {
        -TrackingConfig config
        -HandLandmarker landmarker
        -str mode
        +process(ndarray frame) list[TrackedHand]
    }

    class MotionTracker {
        -float min_strike_velocity
        -float cooldown_seconds
        -dict last_strike_times
        -dict trajectory_history
        +update(TrackedPoint point) tuple[bool, float]
    }

    class DrumPad {
        +str id
        +str name
        +float x
        +float y
        +float width
        +float height
        +tuple color
        +str sound_file
        +bool is_active
        +float active_timer
        +contains_point(int px, int py, int fw, int fh) bool
    }

    class DrumLayout {
        +str layout_path
        +list~DrumPad~ pads
        +load_layout(str path) void
        +check_collisions(int px, int py, int fw, int fh) DrumPad
        +draw(ndarray frame) ndarray
    }

    class AudioEngine {
        -AudioConfig config
        -dict sound_cache
        +load_sound(str pad_id, str filepath) void
        +play_sound(str pad_id, float volume) void
        +stop() void
    }

    Camera --> HandTracker : supplies frames
    HandTracker --> MotionTracker : passes coordinates
    DrumLayout *-- DrumPad : contains 1..*
    MotionTracker ..> DrumLayout : checks pad boundary
    MotionTracker ..> AudioEngine : triggers playback on strike
```
