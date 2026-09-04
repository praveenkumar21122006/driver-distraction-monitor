# Driver Fatigue & Distraction Monitor

A local computer-vision prototype that uses a webcam to watch for visual signs of driver fatigue and distraction. It displays the camera feed, face landmarks, detection state, and risk score in real time, then plays an audio warning when configured thresholds are reached.

![Dashboard preview](assets/monitor-dashboard.svg)

> This project is for education and experimentation. It is not a certified automotive safety system and must not be used as the sole safety mechanism in a vehicle.

## What It Detects

- Face presence and facial landmarks
- Prolonged eye closure and drowsiness
- Yawning
- Basic face direction and distraction signals
- A combined risk score
- Audio warnings through `assets/alarm.wav`

![Detection flow](assets/detection-flow.svg)

## Requirements

- Python 3.9 or newer
- A working webcam
- A desktop environment with an available audio output
- MediaPipe's face landmarker model at `assets/face_landmarker.task`

The application currently targets desktop Python environments. Camera and audio permissions may need to be granted by the operating system.

## Installation

### Linux and macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

The included setup script can be used on Linux or macOS:

```bash
chmod +x setup.sh
./setup.sh
```

## Run

Activate the virtual environment and start the monitor:

```bash
python app.py
```

The webcam window opens once the camera is available. Press `Q` to stop the monitor and close the window.

## Project Layout

```text
driver-fatigue-monitor/
├── app.py                         # Application loop and dashboard
├── requirements.txt               # Python dependencies
├── setup.sh                       # Environment setup helper
├── assets/
│   ├── alarm.wav                  # Warning sound
│   ├── detection-flow.svg         # README workflow illustration
│   ├── face_landmarker.task       # MediaPipe model
│   └── monitor-dashboard.svg      # README dashboard illustration
├── detector/
│   ├── distraction_detector.py    # Face direction checks
│   ├── face_detector.py           # Face landmark extraction
│   └── fatigue_detector.py        # Eye and mouth signal checks
├── tests/
│   └── test_warning_system.py     # Warning behavior tests
└── utils/
    ├── alert.py                   # Audio alert handling
    └── constants.py               # Shared thresholds and settings
```

## How It Works

1. OpenCV reads frames from the default webcam.
2. MediaPipe extracts face landmarks using the bundled task model.
3. Detector modules measure eye closure, mouth opening, and face direction.
4. The application combines those signals into a risk score.
5. The alert utility plays the warning sound when the risk state requires it.

The thresholds are centralized in `utils/constants.py`, so experiments can be made without changing the main application loop. Lighting, camera position, glasses, facial pose, and camera quality can affect results.

## Tests

Install the dependencies, then run:

```bash
python -m pytest
```

The tests cover the warning-system behavior. Hardware-dependent camera and audio behavior should also be checked on the target machine.

## Troubleshooting

**The camera does not open**

- Confirm that no other application is using the webcam.
- Check operating-system camera permissions.
- Try a different camera index in `app.py` if the default device is not index `0`.

**The model cannot be loaded**

- Confirm that `assets/face_landmarker.task` exists and is readable.
- Run the command from the project root so relative asset paths resolve correctly.

**No warning sound is heard**

- Check the system volume and selected audio output.
- Confirm that `assets/alarm.wav` exists.
- Verify that the desktop audio backend required by the installed Pygame version is available.

## License and Safety

No production safety, medical, legal, or fitness-for-purpose claims are made by this prototype. Do not drive while testing or adjusting the application. Add an appropriate license before redistributing the project.