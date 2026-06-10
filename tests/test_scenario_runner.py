from pathlib import Path
import unittest

from src.alert_engine import AlertEngine
from src.scenario_runner import load_scenario, run_scenario


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "detection_classes.json"
SCENARIOS_PATH = ROOT / "scenarios"


class ScenarioRunnerTest(unittest.TestCase):
    def test_weapon_cooldown_speaks_before_and_after_cooldown(self) -> None:
        scenario_run = run_scenario(
            AlertEngine.from_config(CONFIG_PATH),
            load_scenario(SCENARIOS_PATH / "weapon_cooldown.json"),
        )

        self.assertEqual(
            scenario_run.spoken_messages,
            [
                "possible weapon visible ahead, 82 percent.",
                "possible weapon visible ahead, 90 percent.",
            ],
        )
        self.assertEqual(scenario_run.observations[1].events[0].reason, "cooldown")

    def test_multiple_hazards_uses_highest_severity(self) -> None:
        scenario_run = run_scenario(
            AlertEngine.from_config(CONFIG_PATH),
            load_scenario(SCENARIOS_PATH / "multiple_hazards.json"),
        )

        self.assertEqual(
            scenario_run.spoken_messages,
            ["possible weapon visible right, 76 percent."],
        )
        suppressed_reasons = [
            event.reason
            for observation in scenario_run.observations
            for event in observation.events
            if event.status == "suppressed"
        ]
        self.assertIn("lower_priority", suppressed_reasons)

    def test_unknown_label_is_suppressed(self) -> None:
        scenario_run = run_scenario(
            AlertEngine.from_config(CONFIG_PATH),
            load_scenario(SCENARIOS_PATH / "low_light_unknown_label.json"),
        )

        self.assertEqual(
            scenario_run.spoken_messages,
            ["low light, detection confidence reduced, 72 percent."],
        )
        self.assertTrue(
            any(
                event.label == "hostile_person" and event.reason == "unknown_label"
                for observation in scenario_run.observations
                for event in observation.events
            )
        )


if __name__ == "__main__":
    unittest.main()
