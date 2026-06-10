# Implementation Backlog

## P0: Repository And Build

- Publish this repository to GitHub.
- Add a Gradle wrapper from a machine with Gradle installed.
- Add the GitHub Packages token locally as `github_token` in `local.properties`.
- Add the Meta Wearables Developer Center app id locally as `META_DAT_APPLICATION_ID`.
- Confirm DAT `0.7.0` dependency resolution.
- Keep raw datasets out of git; validate manifests with `scripts/validate_dataset.py`.

## P1: Device Session

- Replace `DemoGlassesGateway` with `MetaDatGlassesGateway`.
- Implement DAT session start and stop.
- Expose session state through `GlassesGateway.sessionState`.
- Add Mock Device Kit support before relying on physical glasses.
- Add explicit UI states for disconnected, connecting, running, paused, and error.

## P1: Camera Stream

- Subscribe to DAT camera streaming.
- Sample frames at 1-3 frames per second.
- Track frame timestamp, resolution, and rotation.
- Drop frames when inference is already running.
- Add a low-light detector from frame brightness statistics.

## P1: Audio Callouts

- Route `GlassesGateway.speak()` through the DAT-supported audio path.
- Confirm whether device speaker output accepts direct text-to-speech or requires phone-side TTS routed to the glasses.
- Add an emergency mute toggle.
- Add a user-adjustable cooldown.

## P1: Optional HUD

- Keep `NoOpDisplayGateway` for glasses without a display.
- Wire `MetaDatDisplayGateway` to `mwdat-display`.
- Select only connected display-capable devices for HUD output.
- Add a HUD mute toggle that does not disable audio callouts.
- Render compact `HudCard` content for selected alerts.
- Clear HUD content when monitoring stops.

## P2: Vision Model

- Start with a narrow on-device detector.
- Export a TensorFlow Lite model for Android.
- Add confidence calibration tests using a holdout image set.
- Keep model labels aligned with `configs/detection_classes.json`.
- Reject labels that infer intent or identity.

## P2: Alert Audit Log

- Persist alert metadata locally.
- Store label, confidence, timestamp, direction, and spoken message.
- Avoid raw image/video retention by default.
- Add an export option for debugging.

## P3: Field Validation

- Test indoors, outdoors, day, night, moving, and stationary.
- Measure latency from frame capture to spoken alert.
- Measure false positives per minute.
- Tune thresholds and cooldowns with real-world data.
