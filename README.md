# Driver Fatigue & Distraction Monitor

A simple computer vision based mini project that monitors a driver's face using a webcam.

## Features

- Face detection
- Eye closure detection
- Drowsiness detection
- Yawning detection
- Basic distraction detection
- Risk score
- Audio warning
- Real-time webcam dashboard

## Technologies

- Python
- OpenCV
- MediaPipe
- NumPy
- Pygame

## Project Structure

driver-fatigue-monitor/

├── app.py
├── requirements.txt
├── README.md
│
├── detector/
│   ├── __init__.py
│   ├── face_detector.py
│   ├── fatigue_detector.py
│   └── distraction_detector.py
│
├── utils/
│   ├── __init__.py
│   ├── alert.py
│   └── constants.py
│
└── assets/
    └── alarm.wav

## Installation

Create a virtual environment:

python -m venv venv

Windows:

venv\Scripts\activate

Linux/Mac:

source venv/bin/activate

Install packages:

pip install -r requirements.txt

## Run

python app.py

Press Q to close the application.

## Detection

The system monitors:

1. Eye closure
2. Yawning
3. Face direction
4. Risk score

## Disclaimer

This is an educational computer-vision prototype and is not a certified automotive safety system.