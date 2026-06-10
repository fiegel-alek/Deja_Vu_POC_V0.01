from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


UNSAFE_TERMS = {
    "aggressive",
    "criminal",
    "dangerous_person",
    "hostile",
    "hostle",
    "intent",
    "suspect",
    "suspicious",
    "target",
    "terrorist",
    "threat",
}


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


class ConfigValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__("\n".join(f"{issue.path}: {issue.message}" for issue in issues))


def load_config(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_detection_config(config: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    classes = config.get("classes")
    if not isinstance(classes, list) or not classes:
        return [ValidationIssue("classes", "must be a non-empty list")]

    seen_labels: set[str] = set()
    for index, item in enumerate(classes):
        path = f"classes[{index}]"
        if not isinstance(item, dict):
            issues.append(ValidationIssue(path, "must be an object"))
            continue

        label = item.get("label")
        spoken_name = item.get("spoken_name")
        threshold = item.get("threshold")
        severity = item.get("severity")

        if not isinstance(label, str) or not label:
            issues.append(ValidationIssue(f"{path}.label", "must be a non-empty string"))
        else:
            if label in seen_labels:
                issues.append(ValidationIssue(f"{path}.label", "must be unique"))
            seen_labels.add(label)
            issues.extend(_validate_safe_text(f"{path}.label", label))

        if not isinstance(spoken_name, str) or not spoken_name:
            issues.append(ValidationIssue(f"{path}.spoken_name", "must be a non-empty string"))
        else:
            issues.extend(_validate_safe_text(f"{path}.spoken_name", spoken_name))

        if not isinstance(threshold, (int, float)) or not 0 <= float(threshold) <= 1:
            issues.append(ValidationIssue(f"{path}.threshold", "must be between 0 and 1"))

        if not isinstance(severity, int) or severity < 1:
            issues.append(ValidationIssue(f"{path}.severity", "must be a positive integer"))

    cooldown = config.get("default_cooldown_ms", 5000)
    if not isinstance(cooldown, int) or cooldown < 0:
        issues.append(ValidationIssue("default_cooldown_ms", "must be a non-negative integer"))

    max_alerts = config.get("max_alerts_per_frame", 1)
    if not isinstance(max_alerts, int) or max_alerts < 1:
        issues.append(ValidationIssue("max_alerts_per_frame", "must be a positive integer"))

    return issues


def validate_detection_config_file(path: str | Path) -> None:
    issues = validate_detection_config(load_config(path))
    if issues:
        raise ConfigValidationError(issues)


def _validate_safe_text(path: str, value: str) -> list[ValidationIssue]:
    normalized = value.lower().replace("-", "_").replace(" ", "_")
    return [
        ValidationIssue(path, f"must not infer intent or identity using '{term}'")
        for term in sorted(UNSAFE_TERMS)
        if term in normalized
    ]
