import { FaceLandmarker, FilesetResolver } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/vision_bundle.mjs";

const WASM_URL = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.0.1/wasm";
const MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";
const EAR_THRESHOLD = 0.21;
const MAR_THRESHOLD = 0.65;
const YAWN_FRAMES = 15;
const DISTRACTION_FRAMES = 25;
const EYE_CLOSED_MS = 5000;

const video = document.querySelector("#camera");
const canvas = document.querySelector("#overlay");
const context = canvas.getContext("2d");
const startButton = document.querySelector("#startButton");
const stopButton = document.querySelector("#stopButton");
const cameraMessage = document.querySelector("#cameraMessage");
const connectionState = document.querySelector("#connectionState");
const soundToggle = document.querySelector("#soundToggle");
const scoreElement = document.querySelector("#score");
const faceElement = document.querySelector("#face");
const eyesElement = document.querySelector("#eyes");
const attentionElement = document.querySelector("#attention");
const statusElement = document.querySelector("#status");

let landmarker;
let stream;
let animationFrame;
let lastVideoTime = -1;
let closedSince = null;
let yawnFrames = 0;
let distractionFrames = 0;
let audioContext;

const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
const ratio = (landmarks, points) => {
  const horizontal = distance(landmarks[points[0]], landmarks[points[3]]);
  return horizontal ? (distance(landmarks[points[1]], landmarks[points[5]]) + distance(landmarks[points[2]], landmarks[points[4]])) / (2 * horizontal) : 0;
};
const mouthRatio = (landmarks) => distance(landmarks[13], landmarks[14]) / (distance(landmarks[78], landmarks[308]) || 1);

function setMetrics({ score = 0, face = "WAITING", eyes = "WAITING", attention = "WAITING", status = "Camera is off", warning = false }) {
  scoreElement.innerHTML = `${score}<small> / 7</small>`;
  faceElement.textContent = face;
  eyesElement.textContent = eyes;
  attentionElement.textContent = attention;
  statusElement.innerHTML = `<span class="status-dot${warning ? " warning" : ""}"></span>${status}`;
  statusElement.classList.toggle("warning-text", warning);
}

function beep() {
  if (!soundToggle.checked || !audioContext) return;
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  oscillator.frequency.value = 740;
  gain.gain.setValueAtTime(0.0001, audioContext.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.12, audioContext.currentTime + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.22);
  oscillator.connect(gain).connect(audioContext.destination);
  oscillator.start();
  oscillator.stop(audioContext.currentTime + 0.24);
}

function drawLandmarks(landmarks) {
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "rgba(97, 208, 149, .7)";
  for (const point of landmarks) context.fillRect(point.x * canvas.width - 1, point.y * canvas.height - 1, 2, 2);
}

function analyze(landmarks, now) {
  const ear = (ratio(landmarks, [33, 160, 158, 133, 153, 144]) + ratio(landmarks, [362, 385, 387, 263, 373, 380])) / 2;
  const eyesClosed = ear < EAR_THRESHOLD;
  if (eyesClosed && closedSince === null) closedSince = now;
  if (!eyesClosed) closedSince = null;
  const drowsy = closedSince !== null && now - closedSince >= EYE_CLOSED_MS;

  const yawningNow = mouthRatio(landmarks) > MAR_THRESHOLD;
  yawnFrames = yawningNow ? yawnFrames + 1 : 0;
  const yawning = yawnFrames >= YAWN_FRAMES;

  const faceWidth = landmarks[454].x - landmarks[234].x;
  const relativeNose = faceWidth ? (landmarks[1].x - landmarks[234].x) / faceWidth : 0.5;
  const direction = relativeNose < 0.35 ? "LEFT" : relativeNose > 0.65 ? "RIGHT" : "FORWARD";
  distractionFrames = direction === "FORWARD" ? 0 : distractionFrames + 1;
  const distracted = distractionFrames >= DISTRACTION_FRAMES;

  const warning = drowsy || yawning || distracted;
  const score = (drowsy ? 3 : 0) + (yawning ? 1 : 0) + (distracted ? 3 : 0);
  const status = drowsy ? "DROWSINESS DETECTED" : distracted ? "DISTRACTION DETECTED" : yawning ? "YAWNING DETECTED" : "NORMAL";
  setMetrics({ score, face: "FOUND", eyes: eyesClosed ? "CLOSED" : "OPEN", attention: direction, status, warning });
  if (warning && !analyze.lastWarning) beep();
  analyze.lastWarning = warning;
}

function render() {
  if (!stream || video.readyState < 2) return;
  if (video.currentTime !== lastVideoTime) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    let result;
    try {
      result = landmarker.detectForVideo(video, performance.now());
    } catch (error) {
      console.error(error);
      stop("Face analysis stopped unexpectedly.");
      return;
    }
    if (result.faceLandmarks.length) {
      drawLandmarks(result.faceLandmarks[0]);
      analyze(result.faceLandmarks[0], performance.now());
      cameraMessage.hidden = true;
    } else {
      context.clearRect(0, 0, canvas.width, canvas.height);
      setMetrics({ face: "NOT FOUND", eyes: "NO FACE", attention: "UNKNOWN", status: "No face detected" });
    }
    lastVideoTime = video.currentTime;
  }
  animationFrame = requestAnimationFrame(render);
}

async function start() {
  startButton.disabled = true;
  cameraMessage.textContent = "Loading face model...";
  try {
    closedSince = null;
    yawnFrames = 0;
    distractionFrames = 0;
    analyze.lastWarning = false;
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const vision = await FilesetResolver.forVisionTasks(WASM_URL);
    const options = { baseOptions: { modelAssetPath: MODEL_URL }, runningMode: "VIDEO", numFaces: 1, minFaceDetectionConfidence: 0.5, minFacePresenceConfidence: 0.5, minTrackingConfidence: 0.5 };
    try {
      landmarker = await FaceLandmarker.createFromOptions(vision, { ...options, baseOptions: { ...options.baseOptions, delegate: "GPU" } });
    } catch {
      landmarker = await FaceLandmarker.createFromOptions(vision, options);
    }
    if (!navigator.mediaDevices?.getUserMedia) throw new Error("Camera access is unavailable in this browser.");
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
    video.srcObject = stream;
    await video.play();
    connectionState.textContent = "Live";
    connectionState.classList.add("live");
    cameraMessage.hidden = true;
    stopButton.disabled = false;
    render();
  } catch (error) {
    console.error(error);
    cameraMessage.hidden = false;
    cameraMessage.textContent = error.name === "NotAllowedError" ? "Camera permission was denied." : error.message || "Could not start the camera or face model.";
    setMetrics({ status: "Camera unavailable" });
    startButton.disabled = false;
  }
}

function stop(message = "Press start and allow camera access.") {
  cancelAnimationFrame(animationFrame);
  stream?.getTracks().forEach((track) => track.stop());
  stream = null;
  video.srcObject = null;
  closedSince = null;
  yawnFrames = 0;
  distractionFrames = 0;
  analyze.lastWarning = false;
  connectionState.textContent = "Offline";
  connectionState.classList.remove("live");
  cameraMessage.hidden = false;
  cameraMessage.textContent = message;
  startButton.disabled = false;
  stopButton.disabled = true;
  setMetrics({ status: "Camera is off" });
}

startButton.addEventListener("click", start);
stopButton.addEventListener("click", stop);
