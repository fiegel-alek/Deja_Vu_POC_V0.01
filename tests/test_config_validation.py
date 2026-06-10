import unittest

from src.config_validation import validate_detection_config, validate_detection_config_file

from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "detection_classes.json"


class ConfigValidationTest(unittest.TestCase):
    def test_current_config_is_valid(self) -> None:
        validate_detection_config_file(CONFIG_PATH)

    def test_rejects_unsafe_intent_labels(self) -> None:
        issues = validate_detection_config(
            {
                "classes": [
                    {
                        "label": "hostile_person",
                        "spoken_name": "hostile person",
                        "threshold": 0.9,
                        "severity": 5,
                    }
                ]
            }
        )

        self.assertGreaterEqual(len(issues), 1)
        self.assertTrue(any("hostile" in issue.message for issue in issues))

    def test_rejects_duplicate_labels(self) -> None:
        issues = validate_detection_config(
            {
                "classes": [
                    {
                        "label": "obstacle",
                        "spoken_name": "obstacle ahead",
                        "threshold": 0.7,
                        "severity": 3,
                    },
                    {
                        "label": "obstacle",
                        "spoken_name": "obstacle ahead",
                        "threshold": 0.7,
                        "severity": 3,
                    },
                ]
            }
        )

        self.assertTrue(any(issue.message == "must be unique" for issue in issues))

    def test_rejects_bad_threshold(self) -> None:
        issues = validate_detection_config(
            {
                "classes": [
                    {
                        "label": "obstacle",
                        "spoken_name": "obstacle ahead",
                        "threshold": 1.2,
                        "severity": 3,
                    }
                ]
            }
        )

        self.assertTrue(any(issue.path.endswith("threshold") for issue in issues))


if __name__ == "__main__":
    unittest.main()
