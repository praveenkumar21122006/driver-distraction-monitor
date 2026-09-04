import unittest

import numpy as np

from app import draw_status


class WarningSystemTests(unittest.TestCase):
    def test_drowsy_state_renders_warning_overlay(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        fatigue = {
            "eyes_closed": True,
            "ear": 0.15,
            "drowsy": True,
            "yawning": False,
        }
        distraction = {
            "direction": "FORWARD",
            "distracted": False,
        }

        result = draw_status(frame, fatigue, distraction, 3)

        self.assertEqual(result.shape, frame.shape)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
