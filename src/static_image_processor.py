from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Optional

from src.alert_engine import AlertEngine, Detection
from src.config_validation import UNSAFE_TERMS, ValidationIssue
from src.scenario_runner import Scenario, ScenarioFrame, ScenarioRun, run_scenario


@dataclass(frozen=True)
class StaticImageDetection:
    label: str
    confidence: float
    bbox_xywh: Optional[list[float]]
    direction: Optional[str]


@dataclass(frozen=True)
class StaticImageFrame:
    image_id: str
    file_name: str
    timestamp_ms: int
    width: int
    height: int
    detections: list[StaticImageDetection]


@dataclass(frozen=True)
class StaticImageBatch:
    name: str
    description: str
    frames: list[StaticImageFrame]


class StaticImageBatchValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__("\n".join(f"{issue.path}: {issue.message}" for issue in issues))


def load_static_image_batch(path: str | Path) -> StaticImageBatch:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    issues = validate_static_image_batch(payload)
    if issues:
        raise StaticImageBatchValidationError(issues)
    return parse_static_image_batch(payload)


def validate_static_image_batch(batch: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    images = batch.get("images")

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
        detections = image.get("detections", [])

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
        elif isinstance(timestamp_ms, int):
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


def parse_static_image_batch(batch: dict[str, Any]) -> StaticImageBatch:
    return StaticImageBatch(
        name=batch["name"],
        description=batch.get("description", ""),
        frames=[
            StaticImageFrame(
                image_id=image["id"],
                file_name=image["file_name"],
                timestamp_ms=int(image["timestamp_ms"]),
                width=int(image["width"]),
                height=int(image["height"]),
                detections=[
                    StaticImageDetection(
                        label=detection["label"],
                        confidence=float(detection["confidence"]),
                        bbox_xywh=[
                            float(value)
                            for value in detection["bbox_xywh"]
                        ]
                        if "bbox_xywh" in detection
                        else None,
                        direction=detection.get("direction"),
                    )
                    for detection in image.get("detections", [])
                ],
            )
            for image in batch["images"]
        ],
    )


def static_batch_to_scenario(batch: StaticImageBatch) -> Scenario:
    return Scenario(
        name=batch.name,
        description=batch.description,
        frames=[
            ScenarioFrame(
                timestamp_ms=frame.timestamp_ms,
                detections=[
                    Detection(
                        label=detection.label,
                        confidence=detection.confidence,
                        timestamp_ms=frame.timestamp_ms,
                        direction=detection.direction,
                    )
                    for detection in frame.detections
                ],
            )
            for frame in batch.frames
        ],
    )


def process_static_image_batch(engine: AlertEngine, batch: StaticImageBatch) -> ScenarioRun:
    return run_scenario(engine, static_batch_to_scenario(batch))


def _validate_detection(
    detection: Any,
    path: str,
    image_width: int,
    image_height: int,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not isinstance(detection, dict):
        return [ValidationIssue(path, "must be an object")]

    label = detection.get("label")
    confidence = detection.get("confidence")
    bbox = detection.get("bbox_xywh")
    direction = detection.get("direction")

    if not isinstance(label, str) or not label:
        issues.append(ValidationIssue(f"{path}.label", "must be a non-empty string"))
    elif _contains_unsafe_term(label):
        issues.append(ValidationIssue(f"{path}.label", "must not infer intent or identity"))

    if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
        issues.append(ValidationIssue(f"{path}.confidence", "must be between 0 and 1"))

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
