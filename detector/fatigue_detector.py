import math
import time

from utils.constants import (
    EAR_THRESHOLD,
    EYE_CLOSED_SECONDS,
    MAR_THRESHOLD,
    YAWN_FRAMES
)


class FatigueDetector:

    def __init__(self):
        self.closed_since = None
        self.yawn_frames = 0

    def distance(self, p1, p2):

        return math.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2
        )

    def eye_aspect_ratio(self, landmarks, points):

        p1 = landmarks[points[0]]
        p2 = landmarks[points[1]]
        p3 = landmarks[points[2]]
        p4 = landmarks[points[3]]
        p5 = landmarks[points[4]]
        p6 = landmarks[points[5]]

        vertical1 = self.distance(p2, p6)
        vertical2 = self.distance(p3, p5)

        horizontal = self.distance(p1, p4)

        if horizontal == 0:
            return 0

        return (vertical1 + vertical2) / (2.0 * horizontal)

    def mouth_aspect_ratio(self, landmarks):

        top = landmarks[13]
        bottom = landmarks[14]

        left = landmarks[78]
        right = landmarks[308]

        vertical = self.distance(top, bottom)
        horizontal = self.distance(left, right)

        if horizontal == 0:
            return 0

        return vertical / horizontal

    def analyze(self, landmarks):

        left_eye = [33, 160, 158, 133, 153, 144]
        right_eye = [362, 385, 387, 263, 373, 380]

        left_ear = self.eye_aspect_ratio(
            landmarks,
            left_eye
        )

        right_ear = self.eye_aspect_ratio(
            landmarks,
            right_eye
        )

        ear = (left_ear + right_ear) / 2

        eyes_closed = ear < EAR_THRESHOLD

        if eyes_closed:
            if self.closed_since is None:
                self.closed_since = time.monotonic()
        else:
            self.closed_since = None

        closed_duration = (
            time.monotonic() - self.closed_since
            if self.closed_since is not None
            else 0.0
        )

        drowsy = closed_duration >= EYE_CLOSED_SECONDS

        mar = self.mouth_aspect_ratio(landmarks)

        if mar > MAR_THRESHOLD:
            self.yawn_frames += 1
        else:
            self.yawn_frames = 0

        yawning = self.yawn_frames >= YAWN_FRAMES

        return {
            "ear": ear,
            "mar": mar,
            "eyes_closed": eyes_closed,
            "closed_duration": closed_duration,
            "drowsy": drowsy,
            "yawning": yawning
        }