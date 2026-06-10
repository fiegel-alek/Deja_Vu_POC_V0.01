#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dataset_validation import load_label_set


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a COCO annotation file to project manifest format.")
    parser.add_argument("coco_json", type=Path, help="Path to COCO annotations JSON.")
    parser.add_argument("output", type=Path, help="Path for output manifest JSON.")
    parser.add_argument(
        "--labels",
        type=Path,
        default=ROOT / "data" / "labels.json",
        help="Path to project labels JSON.",
    )
    parser.add_argument(
        "--category-map",
        type=Path,
        required=True,
        help="JSON object mapping COCO category names to project labels.",
    )
    parser.add_argument("--split", choices=["train", "validation", "test"], default="train")
    args = parser.parse_args()

    label_set = load_label_set(args.labels)
    category_map = json.loads(args.category_map.read_text(encoding="utf-8"))
    unknown_labels = sorted(set(category_map.values()) - label_set.names)
    if unknown_labels:
        print(f"Category map references unknown project labels: {unknown_labels}")
        return 1

    coco = json.loads(args.coco_json.read_text(encoding="utf-8"))
    categories_by_id = {category["id"]: category["name"] for category in coco.get("categories", [])}
    images_by_id = {
        image["id"]: {
            "id": str(image["id"]),
            "file_name": image["file_name"],
            "width": image["width"],
            "height": image["height"],
            "annotations": [],
        }
        for image in coco.get("images", [])
    }

    for annotation in coco.get("annotations", []):
        category_name = categories_by_id.get(annotation.get("category_id"))
        project_label = category_map.get(category_name)
        image = images_by_id.get(annotation.get("image_id"))
        if project_label is None or image is None:
            continue

        image["annotations"].append(
            {
                "id": str(annotation["id"]),
                "label": project_label,
                "bbox_xywh": annotation["bbox"],
                "annotator": "coco_import",
                "review_status": "pending",
            }
        )

    images = list(images_by_id.values())
    manifest = {
        "version": 1,
        "name": args.coco_json.stem,
        "description": "Converted from COCO annotations.",
        "license": "source-dataset-license",
        "source": str(args.coco_json),
        "splits": {
            "train": [],
            "validation": [],
            "test": [],
        },
        "images": images,
    }
    manifest["splits"][args.split] = [image["id"] for image in images]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
