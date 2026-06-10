# Branching Strategy

Use three long-lived branches:

- `dev`: active integration work. Feature branches merge here first.
- `test`: release-candidate branch for demo validation.
- `main`: stable branch that should be demo-ready.

## Flow

```text
feature/<short-name>
    -> dev
    -> test
    -> main
```

## Branch Rules

### dev

- Use for active build-out.
- Accepts incomplete but coherent slices.
- Must pass Python tests and dataset validation before merge.

### test

- Use for demo-candidate validation.
- Only merge from `dev`.
- Should be installable/runnable in the current available environment.
- Use this branch to validate Android builds, DAT credentials, hardware sessions, and model artifacts before promoting.

### main

- Stable, demo-ready history.
- Only merge from `test`.
- Should always preserve the last known working demo path.

## Feature Branches

Use short feature branches off `dev`:

- `feature/dat-session`
- `feature/hud-display`
- `feature/mediapipe-detector`
- `feature/dataset-import`

Delete feature branches after merge.

## Immediate Missing Work

- Add Gradle wrapper and confirm Android build.
- Resolve GitHub Packages auth for Meta DAT artifacts.
- Wire `MetaDatGlassesGateway` to real DAT camera/session APIs.
- Wire `MetaDatDisplayGateway` to real DAT Display APIs.
- Add phone camera or static-image detector using MediaPipe before glasses hardware.
- Add TTS/audio routing fallback.
- Build dataset inventory reports and start collecting reviewed manifests.
- Add model export/import path for Android assets.
