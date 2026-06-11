#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dataset_validation import validate_dataset_manifest_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Create local raw/processed folders for a capture session.")
    parser.add_argument("name", help="Short capture session name, such as basement_replica_set.")
    parser.add_argument(
        "--date",
        default=date.today().strftime("%Y%m%d"),
        help="Capture date in YYYYMMDD format.",
    )
    args = parser.parse_args()

    session_slug = _slugify(f"capture_{args.date}_{args.name}")
    raw_dir = ROOT / "data" / "raw" / session_slug
    processed_dir = ROOT / "data" / "processed" / session_slug
    image_dir = raw_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = processed_dir / "manifest.json"
    if not manifest_path.exists():
        manifest = {
            "version": 1,
            "name": session_slug,
            "description": "Controlled capture session manifest.",
            "license": "internal-controlled-capture",
            "source": f"data/raw/{session_slug}",
            "splits": {
                "train": [],
                "validation": [],
                "test": [],
            },
            "images": [],
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    validate_dataset_manifest_file(manifest_path, ROOT / "data" / "labels.json")
    print(f"Created capture session: {session_slug}")
    print(f"Raw images: {image_dir}")
    print(f"Manifest: {manifest_path}")
    return 0


def _slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower()).strip("_")


if __name__ == "__main__":
    raise SystemExit(main())
