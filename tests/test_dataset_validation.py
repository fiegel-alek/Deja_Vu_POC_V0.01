from pathlib import Path
import unittest

from src.dataset_validation import load_label_set, validate_dataset_manifest, validate_dataset_manifest_file, validate_label_file


ROOT = Path(__file__).resolve().parents[1]
LABELS_PATH = ROOT / "data" / "labels.json"
MANIFEST_PATH = ROOT / "data" / "dataset.example.json"


class DatasetValidationTest(unittest.TestCase):
    def test_label_file_is_valid(self) -> None:
        self.assertEqual(validate_label_file(LABELS_PATH), [])

    def test_example_manifest_is_valid(self) -> None:
        validate_dataset_manifest_file(MANIFEST_PATH, LABELS_PATH)

    def test_rejects_unknown_label(self) -> None:
        manifest = {
            "splits": {"train": ["image_1"], "validation": [], "test": []},
            "images": [
                {
                    "id": "image_1",
                    "file_name": "data/raw/image_1.jpg",
                    "width": 100,
                    "height": 100,
                    "annotations": [
                        {
                            "id": "ann_1",
                            "label": "hostile_person",
                            "bbox_xywh": [1, 1, 10, 10],
                            "review_status": "reviewed",
                        }
                    ],
                }
            ],
        }

        issues = validate_dataset_manifest(manifest, load_label_set(LABELS_PATH))

        self.assertTrue(any(issue.path.endswith(".label") for issue in issues))

    def test_rejects_bbox_outside_image(self) -> None:
        manifest = {
            "splits": {"train": ["image_1"], "validation": [], "test": []},
            "images": [
                {
                    "id": "image_1",
                    "file_name": "data/raw/image_1.jpg",
                    "width": 100,
                    "height": 100,
                    "annotations": [
                        {
                            "id": "ann_1",
                            "label": "knife_visible",
                            "bbox_xywh": [90, 90, 30, 30],
                            "review_status": "reviewed",
                        }
                    ],
                }
            ],
        }

        issues = validate_dataset_manifest(manifest, load_label_set(LABELS_PATH))

        self.assertTrue(any("image bounds" in issue.message for issue in issues))

    def test_rejects_image_in_multiple_splits(self) -> None:
        manifest = {
            "splits": {"train": ["image_1"], "validation": ["image_1"], "test": []},
            "images": [
                {
                    "id": "image_1",
                    "file_name": "data/raw/image_1.jpg",
                    "width": 100,
                    "height": 100,
                    "annotations": [],
                }
            ],
        }

        issues = validate_dataset_manifest(manifest, load_label_set(LABELS_PATH))
        self.assertTrue(any("also appears" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
