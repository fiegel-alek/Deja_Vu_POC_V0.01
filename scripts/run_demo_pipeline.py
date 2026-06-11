#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.alert_engine import AlertEngine
from src.dataset_inventory import build_inventory, format_inventory, load_manifest
from src.detector_output_importer import load_category_map, load_detector_output, process_detector_output
from src.scenario_runner import load_scenario, run_scenario
from src.static_image_processor import load_static_image_batch, process_static_image_batch
from src.synthetic_dataset import SyntheticConfig, generate_synthetic_dataset


def main() -> int:
    print("Demo pipeline")
    print("=============")

    print("\nScenario bench")
    scenario_run = run_scenario(
        AlertEngine.from_config(ROOT / "configs" / "detection_classes.json"),
        load_scenario(ROOT / "scenarios" / "weapon_cooldown.json"),
    )
    print(f"- spoken callouts: {len(scenario_run.spoken_messages)}")

    print("\nStatic image batch")
    static_run = process_static_image_batch(
        AlertEngine.from_config(ROOT / "configs" / "detection_classes.json"),
        load_static_image_batch(ROOT / "data" / "static-image-batch.example.json"),
    )
    print(f"- spoken callouts: {len(static_run.spoken_messages)}")

    print("\nDetector output import")
    detector_run = process_detector_output(
        AlertEngine.from_config(ROOT / "configs" / "detection_classes.json"),
        load_detector_output(ROOT / "data" / "detector-output.example.json"),
        load_category_map(ROOT / "configs" / "detector_category_map.example.json"),
    )
    print(f"- spoken callouts: {len(detector_run.spoken_messages)}")

    print("\nSynthetic dataset")
    with tempfile.TemporaryDirectory() as temp_dir:
        manifest_path = generate_synthetic_dataset(
            SyntheticConfig(output_dir=Path(temp_dir), image_count=12, seed=17, name="demo_pipeline")
        )
        inventory = build_inventory(load_manifest(manifest_path))
        print(format_inventory(inventory))

    print("\nDemo pipeline complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
