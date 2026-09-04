# Driver Safety Monitor

A browser-based driver fatigue and distraction monitor. Camera frames are processed locally in the browser with MediaPipe Tasks; they are not uploaded to a backend.

> This project is for education and experimentation. It is not a certified automotive safety system and must not be used as the sole safety mechanism in a vehicle.

## Features

- Face landmarks and face presence detection
- Prolonged eye closure and drowsiness detection
- Yawning detection
- Basic face-direction distraction signals
- Combined risk score and warning state
- Optional browser warning tone

## Run locally

Serve the repository with any static web server. For example:

```bash
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000), press **Start camera**, and allow camera access. A static server is required because browsers restrict camera access from `file://` pages.

## Deploy on Vercel

1. Import this repository into Vercel.
2. Use the **Other** framework preset.
3. Leave the build command empty.
4. Deploy from the repository root.
5. Open the HTTPS deployment URL, allow camera access, and press **Start camera**.

`vercel.json` serves the static app. No Python runtime, build step, database, or server-side camera processing is required.

## Project layout

```text
driver-fatigue-monitor/
├── index.html          # App markup
├── app.js              # Camera capture and MediaPipe analysis
├── styles.css          # Responsive interface
├── vercel.json         # Vercel static hosting configuration
└── assets/
    ├── detection-flow.svg
    └── monitor-dashboard.svg
```

## Troubleshooting

**The camera does not start**

- Use the HTTPS deployment URL or `localhost`.
- Allow camera access when the browser asks.
- Check that another application is not using the camera.

**The model does not load**

- Check the browser console and network connection.
- MediaPipe Tasks and its model are loaded from public CDNs when the app starts.

**Warnings are silent**

- Enable **Enable warning sound**.
- Interact with the page before starting the camera so the browser permits audio playback.

Lighting, camera position, glasses, facial pose, and camera quality can affect accuracy. Do not drive while testing or adjusting the application.
