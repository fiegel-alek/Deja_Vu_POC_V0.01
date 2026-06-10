from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from src.config_validation import UNSAFE_TERMS, ValidationIssue


ALLOWED_REVIEW_STATUSES = {"pending", "reviewed", "rejected"}
REQUIRED_SPLITS = {"train", "validation", "test"}


@dataclass(frozen=True)
class LabelSet:
    names: set[str]
    trainable_names: set[str]


class DatasetValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__("\n".join(f"{issue.path}: {issue.message}" for issue in issues))


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_label_set(path: str | Path) -> LabelSet:
    payload = load_json(path)
    labels = payload.get("labels", [])
    return LabelSet(
        names={label["name"] for label in labels if isinstance(label, dict) and "name" in label},
        trainable_names={
            label["name"]
            for label in labels
            if isinstance(label, dict) and label.get("trainable", True) and "name" in label
        },
    )


def validate_label_file(path: str | Path) -> list[ValidationIssue]:
    payload = load_json(path)
    issues: list[ValidationIssue] = []
    labels = payload.get("labels")

    if not isinstance(labels, list) or not labels:
        return [ValidationIssue("labels", "must be a non-empty list")]

    seen_ids: set[int] = set()
    seen_names: set[str] = set()

    for index, label in enumerate(labels):
        item_path = f"labels[{index}]"
        if not isinstance(label, dict):
            issues.append(ValidationIssue(item_path, "must be an object"))
            continue

        label_id = label.get("id")
        name = label.get("name")
        parent = label.get("parent")
        trainable = label.get("trainable")

        if not isinstance(label_id, int) or label_id < 1:
            issues.append(ValidationIssue(f"{item_path}.id", "must be a positive integer"))
        elif label_id in seen_ids:
            issues.append(ValidationIssue(f"{item_path}.id", "must be unique"))
        else:
            seen_ids.add(label_id)

        if not isinstance(name, str) or not name:
            issues.append(ValidationIssue(f"{item_path}.name", "must be a non-empty string"))
        elif name in seen_names:
            issues.append(ValidationIssue(f"{item_path}.name", "must be unique"))
        else:
            seen_names.add(name)
            issues.extend(_validate_safe_text(f"{item_path}.name", name))

        if parent is not None and not isinstance(parent, str):
            issues.append(ValidationIssue(f"{item_path}.parent", "must be null or a label name"))

        if not isinstance(trainable, bool):
            issues.append(ValidationIssue(f"{item_path}.trainable", "must be a boolean"))

    for index, label in enumerate(labels):
        if isinstance(label, dict) and label.get("parent") is not None and label.get("parent") not in seen_names:
            issues.append(ValidationIssue(f"labels[{index}].parent", "must reference an existing label"))

    return issues


def validate_dataset_manifest(manifest: dict[str, Any], label_set: LabelSet) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    images = manifest.get("images")
    if not isinstance(images, list):
        return [ValidationIssue("images", "must be a list")]

    split_issues, split_membership = _validate_splits(manifest.get("splits"))
    issues.extend(split_issues)

    seen_image_ids: set[str] = set()
    seen_annotation_ids: set[str] = set()

    for image_index, image in enumerate(images):
        image_path = f"images[{image_index}]"
        if not isinstance(image, dict):
            issues.append(ValidationIssue(image_path, "must be an object"))
            continue

        image_id = image.get("id")
        width = image.get("width")
        height = image.get("height")
        annotations = image.get("annotations", [])

        if not isinstance(image_id, str) or not image_id:
            issues.append(ValidationIssue(f"{image_path}.id", "must be a non-empty string"))
        elif image_id in seen_image_ids:
            issues.append(ValidationIssue(f"{image_path}.id", "must be unique"))
        else:
            seen_image_ids.add(image_id)
            if split_membership and image_id not in split_membership:
                issues.append(ValidationIssue(f"{image_path}.id", "must appear in exactly one split"))

        if not isinstance(image.get("file_name"), str) or not image.get("file_name"):
            issues.append(ValidationIssue(f"{image_path}.file_name", "must be a non-empty string"))

        if not isinstance(width, int) or width <= 0:
            issues.append(ValidationIssue(f"{image_path}.width", "must be a positive integer"))
        if not isinstance(height, int) or height <= 0:
            issues.append(ValidationIssue(f"{image_path}.height", "must be a positive integer"))

        if not isinstance(annotations, list):
            issues.append(ValidationIssue(f"{image_path}.annotations", "must be a list"))
            continue

        if isinstance(width, int) and isinstance(height, int):
            for annotation_index, annotation in enumerate(annotations):
                issues.extend(
                    _validate_annotation(
                        annotation=annotation,
                        path=f"{image_path}.annotations[{annotation_index}]",
                        image_width=width,
                        image_height=height,
                        label_set=label_set,
                        seen_annotation_ids=seen_annotation_ids,
                    )
                )

    if split_membership:
        missing_image_ids = sorted(set(split_membership) - seen_image_ids)
        for image_id in missing_image_ids:
            issues.append(ValidationIssue("splits", f"references unknown image id '{image_id}'"))

    return issues


def validate_dataset_manifest_file(manifest_path: str | Path, labels_path: str | Path) -> None:
    label_issues = validate_label_file(labels_path)
    if label_issues:
        raise DatasetValidationError(label_issues)

    issues = validate_dataset_manifest(load_json(manifest_path), load_label_set(labels_path))
    if issues:
        raise DatasetValidationError(issues)


def _validate_splits(splits: Any) -> tuple[list[ValidationIssue], dict[str, str]]:
    issues: list[ValidationIssue] = []
    membership: dict[str, str] = {}

    if not isinstance(splits, dict):
        return [ValidationIssue("splits", "must be an object")], membership

    missing = REQUIRED_SPLITS - set(splits)
    for split in sorted(missing):
        issues.append(ValidationIssue("splits", f"missing required split '{split}'"))

    for split_name, image_ids in splits.items():
        if split_name not in REQUIRED_SPLITS:
            issues.append(ValidationIssue(f"splits.{split_name}", "is not a supported split"))
            continue

        if not isinstance(image_ids, list):
            issues.append(ValidationIssue(f"splits.{split_name}", "must be a list"))
            continue

        for image_id in image_ids:
            if not isinstance(image_id, str) or not image_id:
                issues.append(ValidationIssue(f"splits.{split_name}", "contains an invalid image id"))
                continue
            if image_id in membership:
                issues.append(
                    ValidationIssue(
                        f"splits.{split_name}",
                        f"image id '{image_id}' also appears in split '{membership[image_id]}'",
                    )
                )
            else:
                membership[image_id] = split_name

    return issues, membership


def _validate_annotation(
    annotation: Any,
    path: str,
    image_width: int,
    image_height: int,
    label_set: LabelSet,
    seen_annotation_ids: set[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not isinstance(annotation, dict):
        return [ValidationIssue(path, "must be an object")]

    annotation_id = annotation.get("id")
    label = annotation.get("label")
    bbox = annotation.get("bbox_xywh")
    review_status = annotation.get("review_status")

    if not isinstance(annotation_id, str) or not annotation_id:
        issues.append(ValidationIssue(f"{path}.id", "must be a non-empty string"))
    elif annotation_id in seen_annotation_ids:
        issues.append(ValidationIssue(f"{path}.id", "must be unique"))
    else:
        seen_annotation_ids.add(annotation_id)

    if not isinstance(label, str) or not label:
        issues.append(ValidationIssue(f"{path}.label", "must be a non-empty string"))
    elif label not in label_set.names:
        issues.append(ValidationIssue(f"{path}.label", "must exist in data/labels.json"))
    else:
        issues.extend(_validate_safe_text(f"{path}.label", label))

    if not _is_valid_bbox(bbox):
        issues.append(ValidationIssue(f"{path}.bbox_xywh", "must be [x, y, width, height] numbers"))
    else:
        x, y, width, height = [float(value) for value in bbox]
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            issues.append(ValidationIssue(f"{path}.bbox_xywh", "must have positive size inside image bounds"))
        if x + width > image_width or y + height > image_height:
            issues.append(ValidationIssue(f"{path}.bbox_xywh", "must fit inside image bounds"))

    if review_status not in ALLOWED_REVIEW_STATUSES:
        issues.append(
            ValidationIssue(
                f"{path}.review_status",
                f"must be one of {sorted(ALLOWED_REVIEW_STATUSES)}",
            )
        )

    return issues


def _is_valid_bbox(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(item, (int, float)) for item in value)
    )


def _validate_safe_text(path: str, value: str) -> list[ValidationIssue]:
    normalized = value.lower().replace("-", "_").replace(" ", "_")
    return [
        ValidationIssue(path, f"must not infer intent or identity using '{term}'")
        for term in sorted(UNSAFE_TERMS)
        if term in normalized
    ]
