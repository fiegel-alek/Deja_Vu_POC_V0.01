# Meta Glasses Situational Awareness Starter

This repository is a starter scaffold for a Meta smart glasses companion app that uses the glasses camera as a sensor, runs pattern recognition on the paired phone, and speaks short safety alerts through the glasses.

The safe design target is visible hazard and object recognition, not judging whether a person is "hostile." The app should report observable evidence such as "possible weapon visible" or "vehicle approaching" with a confidence score. It should not identify people, rank people as threats, infer intent from appearance, or support targeting decisions.

## First Build Target

Build a paired mobile app:

1. Connect to Ray-Ban Meta / Meta AI glasses with Meta Wearables Device Access Toolkit.
2. Request an active device session.
3. Stream camera frames to the phone.
4. Run an object/hazard detector on-device when possible.
5. Convert high-confidence detections into short spoken alerts.
6. Rate-limit repeated alerts so the user is informed without being overloaded.

## Initial Repo Contents

- `docs/architecture.md`: System architecture and data flow.
- `docs/meta-dat-notes.md`: Current Meta Wearables DAT notes and links.
- `docs/safety-boundaries.md`: What the system should and should not classify.
- `configs/detection_classes.json`: Initial observable classes and alert thresholds.
- `src/alert_engine.py`: Dependency-free alert policy engine.
- `tests/test_alert_engine.py`: Unit tests for thresholds, cooldowns, and wording.

## Run The Local Tests

```bash
python3 -m unittest discover -s tests
```

## Next Implementation Step

Pick Android or iOS as the first mobile platform, then wire the Meta Wearables DAT camera stream into `AlertEngine`. Android is usually the fastest first target if you want to lean on the public DAT Android samples and Kotlin.
