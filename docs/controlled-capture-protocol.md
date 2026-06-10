# Controlled Capture Protocol

Use this protocol when collecting real images or video with replica objects. The goal is to create useful object-detection data without teaching the model to infer intent or identity.

## Labels To Capture

- `handgun_visible`
- `long_gun_visible`
- `knife_visible`
- `fire_or_smoke`
- `obstacle`
- `person_close`

## Hard Negatives

Capture benign objects that can look similar to target classes:

- Phones.
- Flashlights.
- Tools.
- Umbrellas.
- Tripods.
- Remote controls.
- Toy objects that should not be labeled as a visible weapon.

## Capture Matrix

For each object, collect variations across:

- Distance: close, medium, far.
- Angle: front, side, diagonal, partially turned away.
- Lighting: bright, indoor, dim, backlit.
- Motion: still, mild hand motion, walking speed.
- Occlusion: unobstructed, hand partially covering, object partly behind clothing or furniture.
- Background: plain wall, cluttered room, outdoor ground, vehicle interior if relevant.

## Safety And Review Rules

- Use legal replica/training objects only in controlled environments.
- Do not collect or label real people as hostile, suspicious, criminal, or safe.
- Do not collect face-identification data for this project.
- Label visible objects and conditions only.
- Use a second review pass before training.

## File Organization

Keep raw captures out of git:

```text
data/raw/capture_YYYYMMDD/
  images/
  notes.md
```

Export reviewed manifests into:

```text
data/processed/capture_YYYYMMDD/manifest.json
```

`data/raw/` and `data/processed/` are ignored by git.

## Minimum Demo Target

For a credible early demo, collect:

- 50-100 images per target object class.
- 100+ hard-negative images.
- At least 20 low-light examples.
- At least 20 motion-blur examples.

Use the dataset validator before training:

```bash
python3 scripts/validate_dataset.py data/processed/capture_YYYYMMDD/manifest.json
```
