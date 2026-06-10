# Architecture

## Core Principle

The glasses are the sensor and audio output. The paired phone is the application host and inference device.

```text
Meta glasses camera
        |
        v
Meta Wearables DAT session
        |
        v
Mobile app frame pipeline
        |
        v
Vision model / detector
        |
        v
Alert policy engine
        |
        v
Text-to-speech / glasses speaker
```

## Components

### Device Connector

Owns Meta Wearables DAT setup, permissions, device session lifecycle, camera stream state, and speaker output.

### Frame Pipeline

Samples incoming frames at a controlled rate. A first version should process 1-3 frames per second instead of every frame to preserve battery and avoid repeated alerts.

### Detector

Produces structured detections:

```json
{
  "label": "weapon_visible",
  "confidence": 0.82,
  "timestamp_ms": 1000,
  "direction": "ahead"
}
```

Keep labels tied to observable objects or hazards. Avoid labels such as `hostile_person`, `suspicious_person`, or `aggressive_intent`.

The Android scaffold models this boundary with:

- `CameraFrame`: timestamped frame metadata and future pixel payload.
- `HazardDetector`: interface that turns frames into detections.
- `DemoHazardDetector`: local demo detector used until DAT frames and a real model are connected.

### Alert Policy Engine

Applies thresholds, severity ordering, cooldowns, and clear language. It is intentionally separate from the model so you can tune behavior without retraining.

### Audio Output

Speaks short messages:

- "Possible weapon visible ahead, 82 percent."
- "Vehicle approaching from left, 78 percent."
- "Low light. Detection confidence reduced."

## MVP Flow

1. User starts monitoring from the mobile app.
2. App requests a device session.
3. App receives frames from the glasses.
4. Detector returns zero or more visible-object detections.
5. Alert engine chooses whether to speak.
6. App sends the callout to the glasses speaker.

## Model Options

For an MVP, start with an on-device model that detects a narrow class list. Export to TensorFlow Lite, Core ML, or ONNX depending on the mobile platform.

For later versions, consider a hybrid model:

- On-device model for fast hazard detection.
- Cloud model for slower review-only analysis, if privacy policy and connectivity allow it.

## Important UX Behavior

- Use short phrases.
- Include uncertainty.
- Avoid moral or intent language.
- Repeat only when confidence changes materially or a cooldown expires.
- Provide a clear "monitoring on/off" state.
- Keep a log of alerts for debugging and auditability.
