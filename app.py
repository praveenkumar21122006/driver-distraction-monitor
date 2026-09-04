import cv2

from detector.face_detector import FaceDetector
from detector.fatigue_detector import FatigueDetector
from detector.distraction_detector import DistractionDetector
from utils.alert import AlertSystem
from utils.constants import CAMERA_WIDTH, CAMERA_HEIGHT


def draw_status(frame, fatigue, distraction, score):

    height, width = frame.shape[:2]
    warning_active = (
        fatigue.get("drowsy", False)
        or fatigue.get("yawning", False)
        or distraction.get("distracted", False)
    )

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (width, 155),
        (0, 0, 0),
        -1
    )

    frame = cv2.addWeighted(
        overlay,
        0.65,
        frame,
        0.35,
        0
    )

    cv2.putText(
        frame,
        "DRIVER FATIGUE & DISTRACTION MONITOR",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2
    )

    eye_status = "CLOSED" if fatigue["eyes_closed"] else "OPEN"

    cv2.putText(
        frame,
        f"Eyes: {eye_status}",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"EAR: {fatigue['ear']:.2f}",
        (220, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Attention: {distraction['direction']}",
        (20, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Risk Score: {score}",
        (300, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    if fatigue.get("drowsy"):

        status = "DROWSINESS DETECTED"

    elif distraction.get("distracted"):

        status = "DISTRACTION DETECTED"

    elif fatigue.get("yawning"):

        status = "YAWNING DETECTED"

    else:

        status = "NORMAL"

    cv2.putText(
        frame,
        f"STATUS: {status}",
        (20, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    if warning_active:
        warning_overlay = frame.copy()
        cv2.rectangle(
            warning_overlay,
            (0, 175),
            (width, 245),
            (0, 0, 180),
            -1
        )
        frame = cv2.addWeighted(
            warning_overlay,
            0.8,
            frame,
            0.2,
            0
        )
        cv2.putText(
            frame,
            "WARNING: CHECK DRIVER STATE",
            (20, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            3
        )

        if fatigue.get("drowsy"):
            cv2.putText(
                frame,
                "EMERGENCY: OPEN YOUR EYES",
                (20, 260),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

    return frame


def main():

    print("Starting Driver Fatigue Monitor...")
    print("Press Q to quit.")

    camera = cv2.VideoCapture(0)

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    if not camera.isOpened():

        print("ERROR: Camera could not be opened.")

        return

    face_detector = FaceDetector()
    fatigue_detector = FatigueDetector()
    distraction_detector = DistractionDetector()
    alert = AlertSystem()

    while True:

        success, frame = camera.read()

        if not success:

            print("Could not read camera frame.")

            break

        frame = cv2.flip(frame, 1)

        landmarks = face_detector.detect(frame)

        score = 0

        if landmarks:

            fatigue = fatigue_detector.analyze(landmarks)

            distraction = distraction_detector.analyze(landmarks)

            if fatigue["drowsy"]:
                score += 3

            if fatigue["yawning"]:
                score += 1

            if distraction["distracted"]:
                score += 3

            if fatigue["drowsy"]:

                alert.beep()

            else:

                alert.stop()

            frame = draw_status(
                frame,
                fatigue,
                distraction,
                score
            )

        else:

            alert.stop()

            cv2.putText(
                frame,
                "NO FACE DETECTED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )

        cv2.imshow(
            "Driver Fatigue Monitor",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):

            break

    alert.stop()

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()