#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dataset_inventory import build_inventory, format_inventory, load_manifest
from src.dataset_validation import DatasetValidationError, validate_dataset_manifest_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Report dataset image and annotation counts.")
    parser.add_argument("manifest", type=Path, help="Path to dataset manifest JSON.")
    parser.add_argument(
        "--labels",
        type=Path,
        default=ROOT / "data" / "labels.json",
        help="Path to labels JSON.",
    )
    args = parser.parse_args()

    try:
        validate_dataset_manifest_file(args.manifest, args.labels)
    except DatasetValidationError as error:
        print("Dataset validation failed:")
        for issue in error.issues:
            print(f"- {issue.path}: {issue.message}")
        return 1

    print(format_inventory(build_inventory(load_manifest(args.manifest))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
