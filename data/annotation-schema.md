# Annotation Schema

Dataset manifests are JSON files that describe images and bounding-box annotations. The schema is intentionally simple so it can be produced from COCO, Open Images, CVAT, Label Studio, or a custom capture tool.

## Manifest Shape

```json
{
  "version": 1,
  "name": "demo_seed",
  "description": "Short dataset description.",
  "license": "dataset license or internal policy",
  "source": "where this dataset came from",
  "splits": {
    "train": ["image_id"],
    "validation": ["image_id"],
    "test": ["image_id"]
  },
  "images": [
    {
      "id": "image_id",
      "file_name": "data/raw/path/image.jpg",
      "width": 1280,
      "height": 720,
      "annotations": [
        {
          "id": "annotation_id",
          "label": "handgun_visible",
          "bbox_xywh": [560, 330, 120, 70],
          "annotator": "reviewer name or tool",
          "review_status": "reviewed"
        }
      ]
    }
  ]
}
```

## Bounding Boxes

Use `[x, y, width, height]` in image pixel coordinates:

- `x`: left edge.
- `y`: top edge.
- `width`: box width.
- `height`: box height.

Boxes must be inside the image bounds and must have positive width and height.

## Splits

Use three splits:

- `train`: model training images.
- `validation`: tuning and threshold checks.
- `test`: final holdout only.

An image id can appear in exactly one split.

## Review Status

Allowed statuses:

- `pending`
- `reviewed`
- `rejected`

Training exports should only use `reviewed` annotations.
