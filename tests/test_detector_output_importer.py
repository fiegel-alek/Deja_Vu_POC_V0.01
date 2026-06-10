from pathlib import Path
import unittest

from src.alert_engine import AlertEngine
from src.detector_output_importer import (
    detector_output_to_static_batch,
    load_category_map,
    load_detector_output,
    process_detector_output,
    validate_category_map,
    validate_detector_output,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "detection_classes.json"
CATEGORY_MAP_PATH = ROOT / "configs" / "detector_category_map.example.json"
DETECTOR_OUTPUT_PATH = ROOT / "data" / "detector-output.example.json"


class DetectorOutputImporterTest(unittest.TestCase):
    def test_imports_detector_output_into_alert_pipeline(self) -> None:
        category_map = load_category_map(CATEGORY_MAP_PATH)
        detector_output = load_detector_output(DETECTOR_OUTPUT_PATH)
        result = process_detector_output(AlertEngine.from_config(CONFIG_PATH), detector_output, category_map)

        self.assertEqual(
            result.spoken_messages,
            [
                "possible knife visible ahead, 81 percent.",
                "person close right, 86 percent.",
                "vehicle approaching ahead, 72 percent.",
            ],
        )

    def test_maps_ignored_categories_out_of_static_batch(self) -> None:
        category_map = load_category_map(CATEGORY_MAP_PATH)
        detector_output = load_detector_output(DETECTOR_OUTPUT_PATH)
        static_batch = detector_output_to_static_batch(detector_output, category_map)

        self.assertEqual(len(static_batch.frames[1].detections), 1)
        self.assertEqual(static_batch.frames[1].detections[0].label, "person_close")

    def test_rejects_unsafe_detector_category(self) -> None:
        issues = validate_detector_output(
            {
                "name": "unsafe",
                "images": [
                    {
                        "id": "image_1",
                        "file_name": "data/raw/image_1.jpg",
                        "timestamp_ms": 1,
                        "width": 100,
                        "height": 100,
                        "detections": [
                            {
                                "category": "hostile_person",
                                "score": 0.9,
                                "bbox_xywh": [1, 1, 10, 10],
                            }
                        ],
                    }
                ],
            }
        )

        self.assertTrue(any("intent" in issue.message for issue in issues))

    def test_rejects_bad_category_map_confidence(self) -> None:
        issues = validate_category_map(
            {
                "categories": {
                    "knife": {
                        "label": "knife_visible",
                        "min_confidence": 2,
                    }
                },
                "ignored_categories": [],
            }
        )

        self.assertTrue(any(issue.path.endswith(".min_confidence") for issue in issues))


if __name__ == "__main__":
    unittest.main()
