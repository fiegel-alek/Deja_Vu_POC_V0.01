#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.alert_engine import AlertEngine
from src.config_validation import validate_detection_config_file
from src.scenario_runner import load_scenario, run_scenario



def main() -> int:
    parser = argparse.ArgumentParser(description="Run a situational-awareness scenario.")
    parser.add_argument("scenario", type=Path, help="Path to a scenario JSON file.")
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "detection_classes.json",
        help="Path to detection class config.",
    )
    args = parser.parse_args()

    validate_detection_config_file(args.config)
    engine = AlertEngine.from_config(args.config)
    scenario = load_scenario(args.scenario)
    scenario_run = run_scenario(engine, scenario)

    print(f"Scenario: {scenario.name}")
    if scenario.description:
        print(f"Description: {scenario.description}")
    print()

    for observation in scenario_run.observations:
        print(
            f"Frame {observation.frame_index} @ {observation.timestamp_ms} ms: "
            f"{observation.detections_seen} detections"
        )
        for event in observation.events:
            print(
                f"  - {event.label} {event.confidence:.2f}: "
                f"{event.status} ({event.reason})"
            )
        for alert in observation.alerts:
            print(f"  SPEAK: {alert.message}")

    print()
    print(f"Spoken callouts: {len(scenario_run.spoken_messages)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
