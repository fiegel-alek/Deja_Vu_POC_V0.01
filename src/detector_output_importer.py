from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Optional

from src.config_validation import UNSAFE_TERMS, ValidationIssue
from src.static_image_processor import (
    StaticImageBatch,
    StaticImageDetection,
    StaticImageFrame,
    process_static_image_batch,
)
from src.alert_engine import AlertEngine
from src.scenario_runner import ScenarioRun


@dataclass(frozen=True)
class CategoryRule:
    label: str
    min_confidence: float


@dataclass(frozen=True)
class CategoryMap:
    categories: dict[str, CategoryRule]
    ignored_categories: set[str]


class DetectorOutputValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__("\n".join(f"{issue.path}: {issue.message}" for issue in issues))


def load_category_map(path: str | Path) -> CategoryMap:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    issues = validate_category_map(payload)
    if issues:
        raise DetectorOutputValidationError(issues)

    return CategoryMap(
        categories={
            name: CategoryRule(
                label=rule["label"],
                min_confidence=float(rule.get("min_confidence", 0.0)),
            )
            for name, rule in payload.get("categories", {}).items()
        },
        ignored_categories=set(payload.get("ignored_categories", [])),
    )


def validate_category_map(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    categories = payload.get("categories")

    if not isinstance(categories, dict) or not categories:
        issues.append(ValidationIssue("categories", "must be a non-empty object"))
        return issues

    for name, rule in categories.items():
        path = f"categories.{name}"
        if not isinstance(name, str) or not name:
            issues.append(ValidationIssue("categories", "contains an invalid category name"))
        elif _contains_unsafe_term(name):
            issues.append(ValidationIssue(path, "must not infer intent or identity"))

        if not isinstance(rule, dict):
            issues.append(ValidationIssue(path, "must be an object"))
            continue

        label = rule.get("label")
        min_confidence = rule.get("min_confidence", 0.0)

        if not isinstance(label, str) or not label:
            issues.append(ValidationIssue(f"{path}.label", "must be a non-empty string"))
        elif _contains_unsafe_term(label):
            issues.append(ValidationIssue(f"{path}.label", "must not infer intent or identity"))

        if not isinstance(min_confidence, (int, float)) or not 0 <= float(min_confidence) <= 1:
            issues.append(ValidationIssue(f"{path}.min_confidence", "must be between 0 and 1"))

    ignored = payload.get("ignored_categories", [])
    if not isinstance(ignored, list) or not all(isinstance(item, str) for item in ignored):
        issues.append(ValidationIssue("ignored_categories", "must be a list of strings"))

    return issues


def load_detector_output(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    issues = validate_detector_output(payload)
    if issues:
        raise DetectorOutputValidationError(issues)
    return payload


def validate_detector_output(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    images = payload.get("images")

    if not isinstance(images, list) or not images:
        return [ValidationIssue("images", "must be a non-empty list")]

    seen_ids: set[str] = set()
    previous_timestamp_ms: Optional[int] = None

    for image_index, image in enumerate(images):
        path = f"images[{image_index}]"
        if not isinstance(image, dict):
            issues.append(ValidationIssue(path, "must be an object"))
            continue

        image_id = image.get("id")
        timestamp_ms = image.get("timestamp_ms")
        width = image.get("width")
        height = image.get("height")
        detections = image.get("detections")

        if not isinstance(image_id, str) or not image_id:
            issues.append(ValidationIssue(f"{path}.id", "must be a non-empty string"))
        elif image_id in seen_ids:
            issues.append(ValidationIssue(f"{path}.id", "must be unique"))
        else:
            seen_ids.add(image_id)

        if not isinstance(image.get("file_name"), str) or not image.get("file_name"):
            issues.append(ValidationIssue(f"{path}.file_name", "must be a non-empty string"))

        if not isinstance(timestamp_ms, int) or timestamp_ms < 0:
            issues.append(ValidationIssue(f"{path}.timestamp_ms", "must be a non-negative integer"))
        elif previous_timestamp_ms is not None and timestamp_ms < previous_timestamp_ms:
            issues.append(ValidationIssue(f"{path}.timestamp_ms", "must not go backward"))
        else:
            previous_timestamp_ms = timestamp_ms

        if not isinstance(width, int) or width <= 0:
            issues.append(ValidationIssue(f"{path}.width", "must be a positive integer"))
        if not isinstance(height, int) or height <= 0:
            issues.append(ValidationIssue(f"{path}.height", "must be a positive integer"))

        if not isinstance(detections, list):
            issues.append(ValidationIssue(f"{path}.detections", "must be a list"))
            continue

        if isinstance(width, int) and isinstance(height, int):
            for detection_index, detection in enumerate(detections):
                issues.extend(
                    _validate_detection(
                        detection=detection,
                        path=f"{path}.detections[{detection_index}]",
                        image_width=width,
                        image_height=height,
                    )
                )

    return issues


def detector_output_to_static_batch(
    detector_output: dict[str, Any],
    category_map: CategoryMap,
) -> StaticImageBatch:
    frames = []

    for image in detector_output["images"]:
        mapped_detections = []
        for detection in image.get("detections", []):
            category = detection["category"]
            if category in category_map.ignored_categories:
                continue

            rule = category_map.categories.get(category)
            if rule is None:
                continue

            score = float(detection["score"])
            if score < rule.min_confidence:
                continue

            mapped_detections.append(
                StaticImageDetection(
                    label=rule.label,
                    confidence=score,
                    bbox_xywh=[float(value) for value in detection["bbox_xywh"]]
                    if "bbox_xywh" in detection
                    else None,
                    direction=detection.get("direction"),
                )
            )

        frames.append(
            StaticImageFrame(
                image_id=image["id"],
                file_name=image["file_name"],
                timestamp_ms=int(image["timestamp_ms"]),
                width=int(image["width"]),
                height=int(image["height"]),
                detections=mapped_detections,
            )
        )

    return StaticImageBatch(
        name=detector_output["name"],
        description=detector_output.get("description", ""),
        frames=frames,
    )


def process_detector_output(
    engine: AlertEngine,
    detector_output: dict[str, Any],
    category_map: CategoryMap,
) -> ScenarioRun:
    return process_static_image_batch(engine, detector_output_to_static_batch(detector_output, category_map))


def _validate_detection(
    detection: Any,
    path: str,
    image_width: int,
    image_height: int,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not isinstance(detection, dict):
        return [ValidationIssue(path, "must be an object")]

    category = detection.get("category")
    score = detection.get("score")
    bbox = detection.get("bbox_xywh")
    direction = detection.get("direction")

    if not isinstance(category, str) or not category:
        issues.append(ValidationIssue(f"{path}.category", "must be a non-empty string"))
    elif _contains_unsafe_term(category):
        issues.append(ValidationIssue(f"{path}.category", "must not infer intent or identity"))

    if not isinstance(score, (int, float)) or not 0 <= float(score) <= 1:
        issues.append(ValidationIssue(f"{path}.score", "must be between 0 and 1"))

    if bbox is not None:
        if not _is_valid_bbox(bbox):
            issues.append(ValidationIssue(f"{path}.bbox_xywh", "must be [x, y, width, height] numbers"))
        else:
            x, y, width, height = [float(value) for value in bbox]
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                issues.append(ValidationIssue(f"{path}.bbox_xywh", "must have positive size inside image bounds"))
            if x + width > image_width or y + height > image_height:
                issues.append(ValidationIssue(f"{path}.bbox_xywh", "must fit inside image bounds"))

    if direction is not None and not isinstance(direction, str):
        issues.append(ValidationIssue(f"{path}.direction", "must be a string when present"))

    return issues


def _is_valid_bbox(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(item, (int, float)) for item in value)
    )


def _contains_unsafe_term(value: str) -> bool:
    normalized = value.lower().replace("-", "_").replace(" ", "_")
    return any(term in normalized for term in UNSAFE_TERMS)
