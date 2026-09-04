import threading

import cv2
import streamlit as st
from streamlit_webrtc import WebRtcMode, VideoProcessorBase, webrtc_streamer

from detector.distraction_detector import DistractionDetector
from detector.face_detector import FaceDetector
from detector.fatigue_detector import FatigueDetector


st.set_page_config(page_title="Driver Safety Monitor", page_icon="D", layout="wide", initial_sidebar_state="expanded")


def draw_status(frame, fatigue, distraction, score):
    height, width = frame.shape[:2]
    warning = fatigue.get("drowsy", False) or fatigue.get("yawning", False) or distraction.get("distracted", False)
    cv2.rectangle(frame, (0, 0), (width, 96), (15, 27, 35), -1)
    cv2.putText(frame, "DRIVER SAFETY MONITOR", (24, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (245, 250, 247), 2)
    cv2.putText(frame, f"EYES: {'CLOSED' if fatigue['eyes_closed'] else 'OPEN'}", (24, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (180, 220, 207), 2)
    cv2.putText(frame, f"ATTENTION: {distraction['direction']}", (230, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (180, 220, 207), 2)
    cv2.putText(frame, f"RISK: {score}/7", (width - 165, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (90, 210, 150) if not warning else (80, 100, 255), 2)
    if warning:
        cv2.rectangle(frame, (0, height - 66), (width, height), (35, 45, 155), -1)
        cv2.putText(frame, "WARNING - CHECK DRIVER STATE", (24, height - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return frame


class MonitorProcessor(VideoProcessorBase):
    def __init__(self):
        self.face_detector = FaceDetector()
        self.fatigue_detector = FatigueDetector()
        self.distraction_detector = DistractionDetector()
        self.lock = threading.Lock()
        self.metrics = {"face": False, "eyes": "Waiting", "direction": "Waiting", "status": "Camera ready", "score": 0}

    def recv(self, frame):
        image = cv2.flip(frame.to_ndarray(format="bgr24"), 1)
        landmarks = self.face_detector.detect(image)

        if landmarks:
            fatigue = self.fatigue_detector.analyze(landmarks)
            distraction = self.distraction_detector.analyze(landmarks)
            score = (3 if fatigue["drowsy"] else 0) + (1 if fatigue["yawning"] else 0) + (3 if distraction["distracted"] else 0)
            warning = fatigue["drowsy"] or fatigue["yawning"] or distraction["distracted"]
            if fatigue["drowsy"]:
                status = "DROWSINESS DETECTED"
            elif distraction["distracted"]:
                status = "DISTRACTION DETECTED"
            elif fatigue["yawning"]:
                status = "YAWNING DETECTED"
            else:
                status = "NORMAL"
            self._update_metrics({"face": True, "eyes": "Closed" if fatigue["eyes_closed"] else "Open", "direction": distraction["direction"].title(), "status": status, "score": score})
            self._draw_dashboard(image, fatigue, distraction, score, warning)
        else:
            self._update_metrics({"face": False, "eyes": "No face", "direction": "Unknown", "status": "No face detected", "score": 0})
            cv2.putText(image, "NO FACE DETECTED", (24, 44), cv2.FONT_HERSHEY_SIMPLEX, 1, (80, 210, 255), 2)

        return frame.from_ndarray(image, format="bgr24")

    def _update_metrics(self, values):
        with self.lock:
            self.metrics = values

    def get_metrics(self):
        with self.lock:
            return self.metrics.copy()

    def _draw_dashboard(self, image, fatigue, distraction, score, warning):
        draw_status(image, fatigue, distraction, score)


def render_metrics(processor):
    metrics = processor.get_metrics() if processor else {"face": False, "eyes": "Waiting", "direction": "Waiting", "status": "Camera is off", "score": 0}
    st.markdown(f"""
    <div class="metrics-grid">
      <div class="metric"><span>RISK SCORE</span><strong>{metrics['score']}<small> / 7</small></strong></div>
      <div class="metric"><span>FACE</span><strong>{'FOUND' if metrics['face'] else 'WAITING'}</strong></div>
      <div class="metric"><span>EYES</span><strong>{metrics['eyes'].upper()}</strong></div>
      <div class="metric"><span>ATTENTION</span><strong>{metrics['direction'].upper()}</strong></div>
    </div>
    <div class="status-line"><span class="status-dot"></span>{metrics['status']}</div>
    """, unsafe_allow_html=True)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { --ink:#17242d; --muted:#63756f; --mint:#61d095; --paper:#f4f7f3; }
.stApp { background:var(--paper); color:var(--ink); }
[data-testid="stHeader"] { background:transparent; }
h1,h2,h3,p,span,div { font-family:'Space Grotesk', sans-serif; }
.hero { padding:2.8rem 0 1.6rem; border-bottom:1px solid #d7e1da; margin-bottom:1.5rem; }
.eyebrow { color:#428e68; font:500 .72rem 'DM Mono', monospace; letter-spacing:.08em; }
.hero h1 { font-size:clamp(2rem,4vw,4.25rem); line-height:1; margin:.55rem 0 .8rem; letter-spacing:0; }
.hero p { color:var(--muted); max-width:44rem; font-size:1.05rem; }
.metrics-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:.7rem; margin:1.1rem 0 .8rem; }
.metric { background:#fff; border:1px solid #d7e1da; padding:1rem; min-height:92px; }
.metric span { display:block; color:var(--muted); font:500 .68rem 'DM Mono',monospace; }
.metric strong { display:block; margin-top:.55rem; font-size:1.25rem; }
.metric small { color:var(--muted); font-size:.8rem; }
.status-line { color:var(--muted); font:500 .8rem 'DM Mono',monospace; padding:.55rem 0 1rem; }
.status-dot { display:inline-block; width:8px; height:8px; background:var(--mint); border-radius:50%; margin-right:.45rem; }
section[data-testid="stSidebar"] { background:#17242d; }
section[data-testid="stSidebar"] * { color:#edf5f0; }
@media (min-width: 900px) { .metrics-grid { grid-template-columns:repeat(2,1fr); } }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">LIVE VISION / LOCAL PROCESSING</div>
  <h1>Driver Safety Monitor</h1>
  <p>Real-time visual signals for fatigue and distraction, processed directly from your browser camera.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Monitor controls")
    st.markdown("Start the camera below to begin analysis. Keep your face visible and centered in the frame.")
    st.divider()
    st.markdown("**Signals**")
    st.markdown("Eye closure  ·  Yawning  ·  Face direction")
    st.divider()
    st.caption("Prototype only. Never use this as the sole safety system while driving.")

left, right = st.columns([1.55, 1], gap="large")
with left:
    st.markdown("### Camera feed")
    context = webrtc_streamer(key="driver-safety-monitor", mode=WebRtcMode.SENDRECV, video_processor_factory=MonitorProcessor, media_stream_constraints={"video": True, "audio": False}, async_processing=True)
with right:
    st.markdown("### Live signals")
    render_metrics(context.video_processor if context and context.video_processor else None)
    st.info("Allow camera access in your browser, then press START in the video panel.")

st.markdown("### How to read the monitor")
st.markdown("The feed overlay marks the current state. A warning appears after sustained eye closure, yawning, or a turned-away face. Lighting and camera position affect accuracy.")
