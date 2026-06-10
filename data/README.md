# Data Workspace

This folder defines the dataset contract for model training and evaluation. It tracks schemas, labels, and tiny examples only.

Do not commit raw images, video, large annotation exports, or trained model artifacts. Keep those under ignored local folders such as:

- `data/raw/`
- `data/processed/`
- `datasets/`

## Demo Data Goal

For the first demo, target a narrow and observable detector:

- `weapon_visible`
- `handgun_visible`
- `long_gun_visible`
- `knife_visible`
- `fire_or_smoke`
- `vehicle_approaching`
- `obstacle`
- `person_close`
- `low_light`

The model should learn visible objects and environmental conditions. It should not learn identity, intent, criminality, or whether a person is hostile.

## Dataset Flow

```text
raw images/video
    -> reviewed frames
    -> bounding-box annotations
    -> dataset manifest
    -> validation
    -> train/validation/test split
    -> model export
    -> Android asset
```

## Minimum Demo Milestone

Before training a custom model, collect or source:

- 200-500 reviewed examples for each high-priority visible class.
- Negative/background images with no target objects.
- Indoor, outdoor, low-light, motion-blur, and partial-occlusion examples.
- A held-out test split that is never used for training.
