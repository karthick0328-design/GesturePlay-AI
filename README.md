# GesturePlay AI — Real-Time Hand Gesture Game Controller & Web Lab

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-brightgreen.svg)](https://developers.google.com/mediapipe)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9+-red.svg)](https://opencv.org/)
[![Vercel Ready](https://img.shields.io/badge/deploy-Vercel-black.svg?logo=vercel)](https://vercel.com)
[![GitHub](https://img.shields.io/badge/author-karthick0328--design-purple.svg?logo=github)](https://github.com/karthick0328-design)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Touchless gaming powered by computer vision.** Control native PC games and in-browser titles with intuitive hand gestures captured by any standard webcam — zero specialized hardware required.

---

## 🌟 Live Web Demo on Vercel
Experience GesturePlay AI directly inside your browser without installing anything:
- 🎮 **Interactive Cyber Racer Game**: Drive, steer, shield, and jump using live webcam gestures.
- 🖐️ **MediaPipe 3D Landmark Visualizer**: Real-time 21-joint skeletal tracking at 60 FPS.
- 📊 **Live Telemetry**: Real-time FPS, hand rotation angles, and active keycaps.

---

## 1. Project Overview
GesturePlay AI is a dual-mode touchless interaction system:
1. **In-Browser Web Lab (Vercel)**: Instant zero-install web application running MediaPipe Hands JS client-side with an interactive canvas runner game.
2. **Native PC Desktop Controller (Python)**: Low-latency Python engine utilizing OpenCV, MediaPipe, and hardware-level scan code automation (`pydirectinput`) to control any PC game (DirectX, Steam, emulators).

---

## 2. Key Features
- **Real-Time 3D Hand Tracking**: Powered by Google MediaPipe for millimeter-accurate joint detection.
- **Rule-Based Geometric Heuristics**: Deterministic Euclidean distance ratios and vector angles — no black-box inference delays.
- **Temporal Stabilization (Debouncing)**: FIFO buffer prevents key fluttering and accidental repeated inputs.
- **Game Profiles**: Ready-to-play configurations for Racing (`WASD + Space`) and Platformers (`Arrow Keys + Space`).
- **Hardware-Level Automation**: Direct input simulation compatible with DirectX games (e.g., Asphalt, Need for Speed, Trackmania).
- **Fail-Safe Key Release**: Automatically lifts all keys whenever a hand exits the camera frame.

---

## 3. Gestures & Key Mapping

| Gesture | Finger State / Angle | Racing Action | Key Simulated |
| :--- | :--- | :--- | :---: |
| 🖐️ **Open Palm** | All 5 fingers extended | Accelerate / Gas | `W` |
| ✊ **Closed Fist** | All fingers curled into palm | Brake / Reverse / Shield | `S` |
| 👈 **Tilt Left** | Palm angled left ($> 120^\circ$) | Steer Left | `A` |
| 👉 **Tilt Right** | Palm angled right ($-60^\circ$ to $60^\circ$) | Steer Right | `D` |
| ✌️ **Two Fingers** | Index and middle finger raised | Nitro Boost / Jump | `SPACE` |
| 🛡️ **No Hand** | Hand drops out of frame | Safe key release | `None` |

---

## 4. Architecture & Pipeline

```text
Webcam Video Feed
       │
       ▼
OpenCV Frame Capture & RGB Preprocessing
       │
       ▼
MediaPipe 3D Hand Mesh (21 Landmark Coordinates)
       │
       ▼
LandmarkProcessor (Euclidean Distances & Atan2 Vector Angles)
       │
       ▼
GestureDetector (Geometric Rule Classification)
       │
       ▼
Temporal Stabilization (4-Frame Debounce Queue)
       │
       ▼
ActionMapper & KeyboardController (PyDirectInput / PyAutoGUI)
       │
       ▼
Simulated Hardware Scan Code into DirectX PC Game
```

---

## 5. Local Setup & Execution Guide (Python Desktop App)

### Prerequisites
- Python 3.11+
- Standard Webcam (Built-in or USB)

### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/karthick0328-design/GesturePlay-AI.git
cd GesturePlay-AI

# 2. Install dependencies
pip install -r app/requirements.txt

# 3. Launch controller
python app/main.py
```

### Running Automated Pipeline Tests
```bash
pytest -v
# or
python validate_pipeline.py
```

---

## 6. Project Structure

```text
GesturePlay-AI/
├── index.html              # Modern Web Lab & Cyber Racer Mini-Game (Vercel entrypoint)
├── vercel.json             # Vercel static deployment configuration
├── .vercelignore           # Excludes desktop Python backend from Vercel
├── css/
│   └── style.css           # Cyber-glassmorphism dark UI styling
├── js/
│   ├── gesture-tracker.js  # MediaPipe Hands client-side tracking & debouncing
│   └── game.js             # 60 FPS HTML5 Canvas Cyber Racer game
├── app/
│   ├── main.py             # Desktop controller entry point
│   ├── requirements.txt    # Python desktop dependencies
│   ├── camera/             # Video capture & frame preprocessing
│   ├── vision/             # MediaPipe tracking & gesture classification
│   ├── control/            # PyDirectInput keyboard automation
│   ├── profiles/           # Racing & Platformer key mappings
│   ├── calibration/        # Distance & scale sensitivity tuner
│   └── ui/                 # OpenCV dashboard overlay & settings window
├── validate_pipeline.py    # Offline unit and integration test suite
└── README.md
```

---

## 7. How to Deploy on Vercel

1. Push your repository to GitHub:
   ```bash
   git push -u origin main
   ```
2. Go to [vercel.com](https://vercel.com) and log in with your GitHub account (`karthick0328-design`).
3. Click **"Add New Project"** &rarr; select **`GesturePlay-AI`**.
4. Leave all build settings as default (static site).
5. Click **Deploy** &mdash; your live web lab will be available globally on an `https://*.vercel.app` URL!

---

## 8. Author & Credits
- **Author**: [A karthick](https://github.com/karthick0328-design)
- **GitHub**: [@karthick0328-design](https://github.com/karthick0328-design)
- **License**: MIT
