# Static Image Processing

Static image processing is the first detector milestone because it is deterministic and easy to debug. It lets us validate the model contract, alert thresholds, cooldowns, and audit output before adding live camera complexity.

## Why Static First

- Repeatable test inputs.
- Easy false-positive review.
- Works without glasses hardware.
- Works before Android/DAT build issues are resolved.
- Produces the same `Detection` objects the live camera path will produce later.

## Flow

```text
image or frame
    -> model/detector output JSON
    -> static batch validator
    -> AlertEngine
    -> spoken callouts and audit events
```

## Run The Example

```bash
python3 scripts/process_static_images.py data/static-image-batch.example.json
```

The example intentionally includes an unknown-but-observable `umbrella_visible` detector output. The alert engine suppresses unknown labels until they are added to the approved detection config. Real model producers must never emit unsafe intent labels such as `hostile_person`.

## Live Camera Later

Live camera should reuse the same downstream contract:

```text
CameraFrame
    -> HazardDetector
    -> Detection
    -> AlertEngine
```

Once static image processing is solid, live camera is mostly an input timing and performance problem.
