from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetInventory:
    image_count: int
    annotation_count: int
    negative_image_count: int
    images_by_split: dict[str, int]
    annotations_by_label: dict[str, int]
    annotations_by_review_status: dict[str, int]
    annotations_by_split_and_label: dict[str, dict[str, int]]


def load_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_inventory(manifest: dict[str, Any]) -> DatasetInventory:
    split_by_image_id = {
        image_id: split
        for split, image_ids in manifest.get("splits", {}).items()
        for image_id in image_ids
    }
    images_by_split = Counter(split_by_image_id.values())
    annotations_by_label: Counter[str] = Counter()
    annotations_by_review_status: Counter[str] = Counter()
    annotations_by_split_and_label: dict[str, Counter[str]] = defaultdict(Counter)
    negative_image_count = 0
    annotation_count = 0

    for image in manifest.get("images", []):
        annotations = image.get("annotations", [])
        if not annotations:
            negative_image_count += 1

        split = split_by_image_id.get(image.get("id"), "unsplit")
        for annotation in annotations:
            label = annotation.get("label", "unknown")
            review_status = annotation.get("review_status", "unknown")
            annotation_count += 1
            annotations_by_label[label] += 1
            annotations_by_review_status[review_status] += 1
            annotations_by_split_and_label[split][label] += 1

    return DatasetInventory(
        image_count=len(manifest.get("images", [])),
        annotation_count=annotation_count,
        negative_image_count=negative_image_count,
        images_by_split=dict(sorted(images_by_split.items())),
        annotations_by_label=dict(sorted(annotations_by_label.items())),
        annotations_by_review_status=dict(sorted(annotations_by_review_status.items())),
        annotations_by_split_and_label={
            split: dict(sorted(counts.items()))
            for split, counts in sorted(annotations_by_split_and_label.items())
        },
    )


def format_inventory(inventory: DatasetInventory) -> str:
    lines = [
        f"Images: {inventory.image_count}",
        f"Annotations: {inventory.annotation_count}",
        f"Negative images: {inventory.negative_image_count}",
        "",
        "Images by split:",
    ]
    lines.extend(f"- {split}: {count}" for split, count in inventory.images_by_split.items())
    lines.append("")
    lines.append("Annotations by label:")
    if inventory.annotations_by_label:
        lines.extend(f"- {label}: {count}" for label, count in inventory.annotations_by_label.items())
    else:
        lines.append("- none: 0")
    lines.append("")
    lines.append("Annotations by review status:")
    if inventory.annotations_by_review_status:
        lines.extend(
            f"- {status}: {count}"
            for status, count in inventory.annotations_by_review_status.items()
        )
    else:
        lines.append("- none: 0")
    lines.append("")
    lines.append("Annotations by split and label:")
    if inventory.annotations_by_split_and_label:
        for split, counts in inventory.annotations_by_split_and_label.items():
            lines.append(f"- {split}:")
            lines.extend(f"  - {label}: {count}" for label, count in counts.items())
    else:
        lines.append("- none: 0")
    return "\n".join(lines)
