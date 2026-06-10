from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from src.alert_engine import Alert, AlertEngine, Detection, EvaluationEvent


@dataclass(frozen=True)
class ScenarioFrame:
    timestamp_ms: int
    detections: list[Detection]


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    frames: list[ScenarioFrame]


@dataclass(frozen=True)
class ScenarioObservation:
    frame_index: int
    timestamp_ms: int
    detections_seen: int
    alerts: list[Alert]
    events: list[EvaluationEvent]


@dataclass(frozen=True)
class ScenarioRun:
    scenario: Scenario
    observations: list[ScenarioObservation]

    @property
    def spoken_messages(self) -> list[str]:
        return [
            alert.message
            for observation in self.observations
            for alert in observation.alerts
        ]


def load_scenario(path: str | Path) -> Scenario:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_scenario(payload)


def parse_scenario(payload: dict[str, Any]) -> Scenario:
    frames = [
        ScenarioFrame(
            timestamp_ms=int(frame["timestamp_ms"]),
            detections=[
                Detection(
                    label=detection["label"],
                    confidence=float(detection["confidence"]),
                    timestamp_ms=int(frame["timestamp_ms"]),
                    direction=detection.get("direction"),
                )
                for detection in frame.get("detections", [])
            ],
        )
        for frame in payload.get("frames", [])
    ]

    return Scenario(
        name=payload["name"],
        description=payload.get("description", ""),
        frames=frames,
    )


def run_scenario(engine: AlertEngine, scenario: Scenario) -> ScenarioRun:
    observations = []

    for index, frame in enumerate(scenario.frames):
        result = engine.evaluate_with_audit(frame.detections)
        observations.append(
            ScenarioObservation(
                frame_index=index,
                timestamp_ms=frame.timestamp_ms,
                detections_seen=len(frame.detections),
                alerts=result.alerts,
                events=result.events,
            )
        )

    return ScenarioRun(scenario=scenario, observations=observations)
