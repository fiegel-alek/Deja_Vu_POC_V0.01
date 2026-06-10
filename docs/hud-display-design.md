# Optional HUD Display Design

The app supports two operating modes:

- Audio-only mode for Ray-Ban Meta glasses without a lens display.
- Audio + HUD mode for Meta Ray-Ban Display or any future display-capable DAT device.

The display is optional. If no display-capable device is connected, the `DisplayGateway` reports `HudCapability.UNAVAILABLE`, the HUD toggle is disabled, and all alerts continue through speaker callouts.

## HUD Principles

- Keep content glanceable.
- Show observable evidence, not intent.
- Never block the user's view with long text.
- Never replace audio; HUD is a supplement.
- Avoid instructions to confront, pursue, aim, or harm.

## HUD Card Shape

```text
Title: Possible weapon visible ahead
Detail: Visible hazard observation
Confidence: 82 percent
Severity: 5
```

The app currently maps `Alert` to `HudCard` with `AlertHudMapper`.

## Android Interfaces

- `DisplayGateway`: optional display output contract.
- `NoOpDisplayGateway`: audio-only fallback.
- `DemoDisplayGateway`: local/demo behavior.
- `MetaDatDisplayGateway`: integration target for DAT Display calls.
- `HudStatus`: capability, enabled state, and latest rendered card.

## Meta DAT Display Path

The local Meta reference sample confirms the Display capability is separate from the camera/session capability:

1. Add `mwdat-display`.
2. Enable DAM metadata.
3. Select a display-capable connected device.
4. Start a DAT session.
5. Attach Display after the session starts.
6. Wait for Display state to be started.
7. Send one compact root view per update.
8. Detach Display when monitoring stops.

Useful local references:

- `third_party_refs/meta-wearables-dat-android/samples/DisplayAccess`
- `third_party_refs/meta-wearables-dat-android/plugins/mwdat-android/skills/display-access/SKILL.md`

## Fallback Behavior

Older glasses should use:

```kotlin
displayGateway = NoOpDisplayGateway()
```

Display-capable glasses should use:

```kotlin
displayGateway = MetaDatDisplayGateway()
```

The app should decide this from DAT device metadata once real device discovery is wired.
