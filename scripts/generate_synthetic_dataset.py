#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dataset_validation import DatasetValidationError, validate_dataset_manifest_file
from src.synthetic_dataset import SyntheticConfig, generate_synthetic_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a synthetic object-detection dataset seed.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "processed" / "synthetic_seed",
        help="Directory for generated images and manifest.",
    )
    parser.add_argument("--count", type=int, default=30, help="Number of images to generate.")
    parser.add_argument("--width", type=int, default=320, help="Generated image width.")
    parser.add_argument("--height", type=int, default=180, help="Generated image height.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed.")
    parser.add_argument("--name", default="synthetic_seed", help="Dataset manifest name.")
    parser.add_argument(
        "--labels",
        type=Path,
        default=ROOT / "data" / "labels.json",
        help="Path to labels JSON for validation.",
    )
    args = parser.parse_args()

    if args.count < 1:
        print("--count must be at least 1")
        return 1

    manifest_path = generate_synthetic_dataset(
        SyntheticConfig(
            output_dir=args.output_dir,
            image_count=args.count,
            width=args.width,
            height=args.height,
            seed=args.seed,
            name=args.name,
        )
    )

    try:
        validate_dataset_manifest_file(manifest_path, args.labels)
    except DatasetValidationError as error:
        print("Generated dataset failed validation:")
        for issue in error.issues:
            print(f"- {issue.path}: {issue.message}")
        return 1

    print(f"Generated synthetic dataset: {manifest_path}")
    print(f"Images: {args.count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
