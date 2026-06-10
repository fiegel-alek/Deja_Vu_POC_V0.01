# Model Contract

The app accepts detections as observable sensor outputs. Any local or cloud model must produce this shape:

```json
{
  "label": "weapon_visible",
  "confidence": 0.82,
  "timestamp_ms": 1000,
  "direction": "ahead"
}
```

## Required Fields

- `label`: Must match `configs/detection_classes.json`.
- `confidence`: Floating point value from `0.0` to `1.0`.
- `timestamp_ms`: Frame or inference timestamp.

## Optional Fields

- `direction`: Short spatial phrase such as `ahead`, `left`, `right`, or `behind`.

## Rejected Outputs

Models must not emit labels that infer identity, intent, criminality, or moral status. Examples:

- `hostile_person`
- `suspicious_person`
- `criminal`
- `terrorist`
- `threat_confirmed`

The alert engine suppresses unknown labels, and the config validator rejects unsafe configured labels.
