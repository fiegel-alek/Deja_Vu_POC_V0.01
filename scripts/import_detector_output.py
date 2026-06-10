#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.alert_engine import AlertEngine
from src.config_validation import validate_detection_config_file
from src.detector_output_importer import (
    DetectorOutputValidationError,
    detector_output_to_static_batch,
    load_category_map,
    load_detector_output,
    process_detector_output,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import detector output and run the alert pipeline.")
    parser.add_argument("detector_output", type=Path, help="Path to detector output JSON.")
    parser.add_argument(
        "--category-map",
        type=Path,
        default=ROOT / "configs" / "detector_category_map.example.json",
        help="Path to category mapping JSON.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "detection_classes.json",
        help="Path to alert detection class config.",
    )
    args = parser.parse_args()

    try:
        validate_detection_config_file(args.config)
        category_map = load_category_map(args.category_map)
        detector_output = load_detector_output(args.detector_output)
    except DetectorOutputValidationError as error:
        print("Detector import validation failed:")
        for issue in error.issues:
            print(f"- {issue.path}: {issue.message}")
        return 1

    engine = AlertEngine.from_config(args.config)
    static_batch = detector_output_to_static_batch(detector_output, category_map)
    result = process_detector_output(engine, detector_output, category_map)

    print(f"Detector output: {detector_output['name']}")
    print(f"Images: {len(static_batch.frames)}")
    print()

    for observation in result.observations:
        frame = static_batch.frames[observation.frame_index]
        print(f"{frame.image_id} @ {observation.timestamp_ms} ms")
        print(f"  mapped detections: {len(frame.detections)}")
        for event in observation.events:
            print(
                f"  - {event.label} {event.confidence:.2f}: "
                f"{event.status} ({event.reason})"
            )
        for alert in observation.alerts:
            print(f"  SPEAK: {alert.message}")

    print()
    print(f"Spoken callouts: {len(result.spoken_messages)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
