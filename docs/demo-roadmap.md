# Demo Roadmap

The near-term demo should prove the full loop without requiring a perfect custom model.

## Demo 1: Phone-Only Brain Bench

- Run scenario fixtures.
- Show spoken callouts from synthetic detections.
- Show suppression reasons and audit output.
- Validate detection config and dataset manifest.

## Demo 2: Android Mock Device

- Run the Android app with `DemoGlassesGateway`.
- Simulate frames and visible detections.
- Show telemetry counters and alert log.
- Confirm short callouts and cooldowns.

## Demo 3: Phone Camera Detector

- Add MediaPipe object detector to Android.
- Use phone camera or static test images before DAT frames.
- Map detector categories into `Detection` values.
- Apply the existing alert engine and spoken output.

## Demo 4: Meta Glasses Camera

- Replace demo frames with DAT camera frames.
- Keep model inference on the phone.
- Route callouts through the glasses speaker or paired audio output.
- Measure latency from frame capture to spoken callout.

## Demo 5: Custom Dataset Evaluation

- Validate collected manifests.
- Train or fine-tune a small object detector.
- Export to Android-compatible model format.
- Compare false positives and missed detections against held-out data.
