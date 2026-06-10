from pathlib import Path
import unittest

from src.alert_engine import AlertEngine
from src.static_image_processor import (
    load_static_image_batch,
    process_static_image_batch,
    validate_static_image_batch,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "detection_classes.json"
BATCH_PATH = ROOT / "data" / "static-image-batch.example.json"


class StaticImageProcessorTest(unittest.TestCase):
    def test_example_batch_processes_static_detections(self) -> None:
        batch = load_static_image_batch(BATCH_PATH)
        result = process_static_image_batch(AlertEngine.from_config(CONFIG_PATH), batch)

        self.assertEqual(
            result.spoken_messages,
            [
                "possible handgun visible ahead, 86 percent.",
                "low light, detection confidence reduced, 71 percent.",
                "fire or smoke visible right, 78 percent.",
            ],
        )
        self.assertTrue(
            any(
                event.label == "umbrella_visible" and event.reason == "unknown_label"
                for observation in result.observations
                for event in observation.events
            )
        )

    def test_rejects_bad_confidence(self) -> None:
        issues = validate_static_image_batch(
            {
                "name": "bad_confidence",
                "images": [
                    {
                        "id": "frame_1",
                        "file_name": "data/raw/frame_1.jpg",
                        "timestamp_ms": 1,
                        "width": 100,
                        "height": 100,
                        "detections": [
                            {
                                "label": "knife_visible",
                                "confidence": 1.2,
                                "bbox_xywh": [1, 1, 10, 10],
                            }
                        ],
                    }
                ],
            }
        )

        self.assertTrue(any(issue.path.endswith(".confidence") for issue in issues))

    def test_rejects_unsafe_label_in_static_batch(self) -> None:
        issues = validate_static_image_batch(
            {
                "name": "unsafe",
                "images": [
                    {
                        "id": "frame_1",
                        "file_name": "data/raw/frame_1.jpg",
                        "timestamp_ms": 1,
                        "width": 100,
                        "height": 100,
                        "detections": [
                            {
                                "label": "hostile_person",
                                "confidence": 0.9,
                                "bbox_xywh": [1, 1, 10, 10],
                            }
                        ],
                    }
                ],
            }
        )

        self.assertTrue(any("intent" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
