from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable, Mapping, Optional


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    timestamp_ms: int
    direction: Optional[str] = None


@dataclass(frozen=True)
class DetectionClass:
    label: str
    spoken_name: str
    threshold: float
    severity: int


@dataclass(frozen=True)
class Alert:
    label: str
    confidence: float
    timestamp_ms: int
    message: str
    severity: int


class AlertEngine:
    def __init__(
        self,
        classes: Mapping[str, DetectionClass],
        default_cooldown_ms: int = 5000,
        max_alerts_per_frame: int = 1,
    ) -> None:
        self._classes = dict(classes)
        self._default_cooldown_ms = default_cooldown_ms
        self._max_alerts_per_frame = max_alerts_per_frame
        self._last_alert_by_label: dict[str, int] = {}

    @classmethod
    def from_config(cls, path: str | Path) -> "AlertEngine":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        classes = {
            item["label"]: DetectionClass(
                label=item["label"],
                spoken_name=item["spoken_name"],
                threshold=float(item["threshold"]),
                severity=int(item["severity"]),
            )
            for item in payload["classes"]
        }
        return cls(
            classes=classes,
            default_cooldown_ms=int(payload.get("default_cooldown_ms", 5000)),
            max_alerts_per_frame=int(payload.get("max_alerts_per_frame", 1)),
        )

    def evaluate(self, detections: Iterable[Detection]) -> list[Alert]:
        candidates = []

        for detection in detections:
            detection_class = self._classes.get(detection.label)
            if detection_class is None:
                continue

            if detection.confidence < detection_class.threshold:
                continue

            last_alert_ms = self._last_alert_by_label.get(detection.label)
            if (
                last_alert_ms is not None
                and detection.timestamp_ms - last_alert_ms < self._default_cooldown_ms
            ):
                continue

            candidates.append(self._to_alert(detection, detection_class))

        candidates.sort(key=lambda alert: (alert.severity, alert.confidence), reverse=True)
        alerts = candidates[: self._max_alerts_per_frame]

        for alert in alerts:
            self._last_alert_by_label[alert.label] = alert.timestamp_ms

        return alerts

    def _to_alert(
        self,
        detection: Detection,
        detection_class: DetectionClass,
    ) -> Alert:
        confidence_percent = round(detection.confidence * 100)
        direction = f" {detection.direction}" if detection.direction else ""
        message = f"{detection_class.spoken_name}{direction}, {confidence_percent} percent."

        return Alert(
            label=detection.label,
            confidence=detection.confidence,
            timestamp_ms=detection.timestamp_ms,
            message=message,
            severity=detection_class.severity,
        )
