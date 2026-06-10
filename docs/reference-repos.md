# Reference Repos

These repos are useful local references while integrating Meta glasses access and Android object detection. They should be cloned locally into `third_party_refs/` and not committed into this repository.

## Meta Wearables DAT Android

Primary hardware and SDK reference:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/facebook/meta-wearables-dat-android.git third_party_refs/meta-wearables-dat-android
cd third_party_refs/meta-wearables-dat-android
git sparse-checkout set --skip-checks README.md CHANGELOG.md AGENTS.md samples plugins/mwdat-android
```

Useful local paths:

- `third_party_refs/meta-wearables-dat-android/README.md`
- `third_party_refs/meta-wearables-dat-android/samples/CameraAccess`
- `third_party_refs/meta-wearables-dat-android/plugins/mwdat-android/skills`

## MediaPipe Android Object Detection

Recommended first model/inference reference:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/google-ai-edge/mediapipe-samples.git third_party_refs/mediapipe-samples
cd third_party_refs/mediapipe-samples
git sparse-checkout set examples/object_detection/android
```

Useful local path:

- `third_party_refs/mediapipe-samples/examples/object_detection/android`

## TensorFlow Lite Android Object Detection

Backup detector reference:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/tensorflow/examples.git third_party_refs/tensorflow-examples
cd third_party_refs/tensorflow-examples
git sparse-checkout set lite/examples/object_detection/android
```

Useful local path:

- `third_party_refs/tensorflow-examples/lite/examples/object_detection/android`

## Why These Are Not Vendored

The app should depend on published SDK/model artifacts and our own integration code. These repos are reference material for implementation patterns, sample code, and setup details. Keeping them out of git avoids license churn, nested repository confusion, and a much larger project history.
