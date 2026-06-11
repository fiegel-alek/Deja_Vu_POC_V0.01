# Demo Foundation Sprint

Sprint date: June 11, 2026.

## Goal

Make the repository runnable as a phone-side demo pipeline before Meta camera integration.

## Added In This Sprint

- Gradle wrapper files so Android builds can start with `./gradlew`.
- MediaPipe Tasks Vision dependency entry for the Android detector path.
- `local.properties.example` for DAT/GitHub Packages setup.
- `scripts/preflight.py` for local readiness checks.
- `scripts/dataset_inventory.py` for data collection progress reports.
- `scripts/run_demo_pipeline.py` for a complete non-Android demo pass.
- `scripts/init_capture_session.py` for real-world capture session setup.
- `data/capture-session.template.json` for controlled capture sessions.

## Demo Command Set

```bash
python3 scripts/preflight.py
python3 scripts/run_demo_pipeline.py
python3 scripts/init_capture_session.py basement_replica_set
python3 scripts/dataset_inventory.py data/dataset.example.json
python3 scripts/import_detector_output.py data/detector-output.example.json
python3 scripts/generate_synthetic_dataset.py --output-dir /tmp/deja_vu_synthetic --count 12
```

## Remaining External Blockers

- Meta DAT credentials in `local.properties`.
- GitHub Packages token with package read access.
- Android SDK/JDK 17 local setup.
- Physical Meta glasses or Mock Device Kit.
- Real MediaPipe model asset and Android detector adapter.
