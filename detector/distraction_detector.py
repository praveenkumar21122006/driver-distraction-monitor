from utils.constants import DISTRACTION_FRAMES


class DistractionDetector:

    def __init__(self):
        self.distraction_frames = 0

    def analyze(self, landmarks):

        nose = landmarks[1]

        left_face = landmarks[234]
        right_face = landmarks[454]

        face_width = right_face.x - left_face.x

        if face_width == 0:
            return {
                "direction": "UNKNOWN",
                "distracted": False
            }

        relative_x = (nose.x - left_face.x) / face_width

        if relative_x < 0.35:
            direction = "LEFT"
        elif relative_x > 0.65:
            direction = "RIGHT"
        else:
            direction = "FORWARD"

        if direction == "FORWARD":
            self.distraction_frames = 0
        else:
            self.distraction_frames += 1

        distracted = (
            self.distraction_frames >= DISTRACTION_FRAMES
        )

        return {
            "direction": direction,
            "distracted": distracted
        }