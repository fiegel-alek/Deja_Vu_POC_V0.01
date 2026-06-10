#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.alert_engine import AlertEngine
from src.config_validation import validate_detection_config_file
from src.static_image_processor import (
    StaticImageBatchValidationError,
    load_static_image_batch,
    process_static_image_batch,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Process static image detections through the alert pipeline.")
    parser.add_argument("batch", type=Path, help="Path to static image batch JSON.")
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "detection_classes.json",
        help="Path to detection class config.",
    )
    args = parser.parse_args()

    validate_detection_config_file(args.config)
    engine = AlertEngine.from_config(args.config)

    try:
        batch = load_static_image_batch(args.batch)
    except StaticImageBatchValidationError as error:
        print("Static image batch validation failed:")
        for issue in error.issues:
            print(f"- {issue.path}: {issue.message}")
        return 1

    result = process_static_image_batch(engine, batch)

    print(f"Batch: {batch.name}")
    if batch.description:
        print(f"Description: {batch.description}")
    print()

    for observation in result.observations:
        frame = batch.frames[observation.frame_index]
        print(f"{frame.image_id} @ {observation.timestamp_ms} ms")
        print(f"  file: {frame.file_name}")
        for event in observation.events:
            print(
                f"  - {event.label} {event.confidence:.2f}: "
                f"{event.status} ({event.reason})"
            )
        for alert in observation.alerts:
            print(f"  SPEAK: {alert.message}")

    print()
    print(f"Images processed: {len(batch.frames)}")
    print(f"Spoken callouts: {len(result.spoken_messages)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
