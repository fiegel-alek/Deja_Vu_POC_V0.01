# Android DAT Integration Plan

This project now has an Android app shell that keeps the Meta Wearables Device Access Toolkit behind a `GlassesGateway` interface. The checked-in implementation is a `DemoGlassesGateway` so the alert flow can be developed without hardware.

## Files To Replace First

- `app/src/main/java/com/metatroop/situationalawareness/device/GlassesGateway.kt`
- `app/src/main/java/com/metatroop/situationalawareness/device/DemoGlassesGateway.kt`

Create a `MetaDatGlassesGateway` beside the demo gateway once you have:

- A Wearables Developer Center application id.
- Developer mode enabled for the glasses.
- A GitHub token that can read GitHub Packages.
- Physical glasses or the Mock Device Kit configured.

## App Configuration

Create `local.properties` locally:

```properties
github_token=YOUR_GITHUB_PACKAGES_TOKEN
META_DAT_APPLICATION_ID=YOUR_META_DAT_APP_ID
```

The GitHub token is required because the public DAT setup uses GitHub Packages for the Android artifacts.

## First Hardware Milestone

1. Build the app with the DAT dependencies resolving.
2. Start a DAT session from `MetaDatGlassesGateway.startSession()`.
3. Subscribe to camera frames.
4. Convert sampled frames into detector input.
5. Return `Detection` objects into `GlassesGateway.detections`.
6. Route `GlassesGateway.speak()` to the DAT audio or device-supported speech path.

## Detector Milestone

Start with a narrow detector:

- `weapon_visible`
- `vehicle_approaching`
- `fire_or_smoke`
- `obstacle`
- `person_close`
- `low_light`

Keep all model output as observable detections. The alert engine intentionally rejects unknown labels, including `hostile_person`.
