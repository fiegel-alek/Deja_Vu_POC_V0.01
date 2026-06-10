# MediaPipe Static Detector Integration

The next real detector path is MediaPipe Tasks Object Detection in image mode. The local reference sample uses:

```text
com.google.mediapipe:tasks-vision:0.10.29
ObjectDetector.detect(mpImage)
RunningMode.IMAGE
```

Reference paths:

- `third_party_refs/mediapipe-samples/examples/object_detection/android/README.md`
- `third_party_refs/mediapipe-samples/examples/object_detection/android/app/src/main/java/com/google/mediapipe/examples/objectdetection/ObjectDetectorHelper.kt`

## Current Bridge

This repo now has a detector-output importer:

```bash
python3 scripts/import_detector_output.py data/detector-output.example.json
```

It accepts generic detector categories and maps them into approved app labels through:

```text
configs/detector_category_map.example.json
```

Example:

```json
{
  "knife": {
    "label": "knife_visible",
    "min_confidence": 0.55
  }
}
```

Ignored categories such as `cell phone` and `umbrella` are dropped before the alert engine.

## Expected Detector Output

```json
{
  "id": "mp_frame_0001",
  "file_name": "data/raw/mediapipe/mp_frame_0001.jpg",
  "timestamp_ms": 1000,
  "width": 1280,
  "height": 720,
  "detections": [
    {
      "category": "knife",
      "score": 0.81,
      "bbox_xywh": [490, 310, 110, 62],
      "direction": "ahead"
    }
  ]
}
```

## Android Mapping

MediaPipe returns detections with categories and bounding boxes. The Android adapter should map:

- `category.categoryName()` -> `category`
- `category.score()` -> `score`
- `detection.boundingBox()` -> `bbox_xywh`
- image metadata -> `id`, `file_name`, `timestamp_ms`, `width`, `height`

Then use the same category map and alert policy concepts already tested in Python.

## Limitation

The standard MediaPipe sample models are generic detectors. They can help prove the pipeline with common objects such as `person`, `car`, and `knife`, but they will not reliably detect replica weapons until we train or fine-tune a custom model.
