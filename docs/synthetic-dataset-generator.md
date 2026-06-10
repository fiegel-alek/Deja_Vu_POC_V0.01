# Synthetic Dataset Generator

The synthetic generator creates a small object-detection dataset seed without external dependencies. It is meant for pipeline testing, bootstrapping, and model pretraining experiments, not as a replacement for real captured imagery.

## Generate A Dataset

```bash
python3 scripts/generate_synthetic_dataset.py --count 60
```

Default output:

```text
data/processed/synthetic_seed/
  images/
  manifest.json
```

`data/processed/` is ignored by git because generated images can grow quickly.

## Included Classes

The generator currently creates reviewed annotations for:

- `handgun_visible`
- `long_gun_visible`
- `knife_visible`
- `fire_or_smoke`
- `obstacle`
- `person_close`

It also creates hard-negative images with objects such as phones, flashlights, tools, and umbrellas.

## Why This Helps

Synthetic data lets us test:

- Dataset manifest validation.
- Bounding-box handling.
- Train/validation/test split flow.
- Model training scripts once they exist.
- Detection pipeline plumbing before real collection is ready.

## What It Cannot Replace

Synthetic data will not fully represent real camera conditions. We still need controlled real-world captures with replica objects, varied lighting, motion blur, occlusion, distance changes, camera compression, and benign lookalikes.

Use the synthetic generator as:

```text
pipeline seed -> synthetic pretraining -> real capture fine-tuning -> field validation
```
