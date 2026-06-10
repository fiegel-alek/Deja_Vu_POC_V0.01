from pathlib import Path
import unittest

from src.alert_engine import AlertEngine, Detection


CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "detection_classes.json"


class AlertEngineTest(unittest.TestCase):
    def test_alerts_when_detection_exceeds_threshold(self) -> None:
        engine = AlertEngine.from_config(CONFIG_PATH)

        alerts = engine.evaluate(
            [Detection("weapon_visible", confidence=0.82, timestamp_ms=1000, direction="ahead")]
        )

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].label, "weapon_visible")
        self.assertEqual(alerts[0].message, "possible weapon visible ahead, 82 percent.")

    def test_ignores_detection_below_threshold(self) -> None:
        engine = AlertEngine.from_config(CONFIG_PATH)

        alerts = engine.evaluate(
            [Detection("weapon_visible", confidence=0.5, timestamp_ms=1000, direction="ahead")]
        )

        self.assertEqual(alerts, [])

    def test_applies_cooldown_by_label(self) -> None:
        engine = AlertEngine.from_config(CONFIG_PATH)

        first = engine.evaluate(
            [Detection("weapon_visible", confidence=0.82, timestamp_ms=1000, direction="ahead")]
        )
        second = engine.evaluate(
            [Detection("weapon_visible", confidence=0.9, timestamp_ms=2000, direction="ahead")]
        )
        third = engine.evaluate(
            [Detection("weapon_visible", confidence=0.9, timestamp_ms=7000, direction="ahead")]
        )

        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])
        self.assertEqual(len(third), 1)

    def test_prioritizes_highest_severity(self) -> None:
        engine = AlertEngine.from_config(CONFIG_PATH)

        alerts = engine.evaluate(
            [
                Detection("person_close", confidence=0.99, timestamp_ms=1000, direction="left"),
                Detection("weapon_visible", confidence=0.76, timestamp_ms=1000, direction="ahead"),
            ]
        )

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].label, "weapon_visible")

    def test_ignores_unknown_labels(self) -> None:
        engine = AlertEngine.from_config(CONFIG_PATH)

        alerts = engine.evaluate(
            [Detection("hostile_person", confidence=0.99, timestamp_ms=1000, direction="ahead")]
        )

        self.assertEqual(alerts, [])


if __name__ == "__main__":
    unittest.main()
