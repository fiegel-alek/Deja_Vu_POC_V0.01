# Android DAT Integration Plan

This project now has an Android app shell that keeps the Meta Wearables Device Access Toolkit behind a `GlassesGateway` interface. The checked-in implementation is a `DemoGlassesGateway` so the alert flow can be developed without hardware. `MetaDatGlassesGateway` is intentionally present as the DAT integration target, but it does not call undocumented SDK types yet.

## Files To Replace First

- `app/src/main/java/com/metatroop/situationalawareness/device/GlassesGateway.kt`
- `app/src/main/java/com/metatroop/situationalawareness/device/DemoGlassesGateway.kt`
- `app/src/main/java/com/metatroop/situationalawareness/display/DisplayGateway.kt`
- `app/src/main/java/com/metatroop/situationalawareness/display/MetaDatDisplayGateway.kt`

Create a `MetaDatGlassesGateway` beside the demo gateway once you have:

- A Wearables Developer Center application id.
- A Wearables Developer Center client token for Display/DAM flows.
- Developer mode enabled for the glasses.
- A GitHub token that can read GitHub Packages.
- Physical glasses or the Mock Device Kit configured.

## Current Local Pipeline

The app now processes sensor data through this path:

```text
GlassesGateway.frames
    -> FrameSampler
    -> HazardDetector
    -> AlertEngine
    -> AlertLogRepository
    -> GlassesGateway.speak()
```

The sampler defaults to one accepted frame every 500 ms. That keeps the first implementation closer to a low-power awareness loop than a full video analytics pipeline.

## App Configuration

Create `local.properties` locally:

```properties
github_token=YOUR_GITHUB_PACKAGES_TOKEN
META_DAT_APPLICATION_ID=YOUR_META_DAT_APP_ID
META_DAT_CLIENT_TOKEN=YOUR_META_DAT_CLIENT_TOKEN
```

The GitHub token is required because the public DAT setup uses GitHub Packages for the Android artifacts.

## First Hardware Milestone

1. Build the app with the DAT dependencies resolving.
2. Start a DAT session from `MetaDatGlassesGateway.startSession()`.
3. Map DAT session lifecycle events to `DeviceSessionState`.
4. Subscribe to camera frames and emit `CameraFrame` values from `GlassesGateway.frames`.
5. Add pixel payload or model input handles to `CameraFrame`.
6. Convert sampled frames into detector input.
7. Route `GlassesGateway.speak()` to the DAT audio or device-supported speech path.

## Display HUD Milestone

For Meta Ray-Ban Display or future display-capable devices:

1. Filter or select devices with `device.isDisplayCapable()`.
2. Keep `NoOpDisplayGateway` for older audio-only glasses.
3. Start the DAT session.
4. Attach Display only after the device session is started.
5. Wait until Display state is started.
6. Render one compact `HudCard` per selected alert.
7. Clear or detach the display when monitoring stops.

The HUD should show visible evidence and confidence only. It should not show identity, intent, or instructions to act against a person.

## Detector Milestone

Start with a narrow detector:

- `weapon_visible`
- `vehicle_approaching`
- `fire_or_smoke`
- `obstacle`
- `person_close`
- `low_light`

Keep all model output as observable detections. The alert engine intentionally rejects unknown labels, including `hostile_person`.
