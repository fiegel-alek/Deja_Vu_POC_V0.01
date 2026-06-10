from pathlib import Path
import tempfile
import unittest

from src.dataset_validation import validate_dataset_manifest_file
from src.synthetic_dataset import SyntheticConfig, generate_synthetic_dataset


ROOT = Path(__file__).resolve().parents[1]
LABELS_PATH = ROOT / "data" / "labels.json"


class SyntheticDatasetTest(unittest.TestCase):
    def test_generates_valid_manifest_and_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "synthetic"

            manifest_path = generate_synthetic_dataset(
                SyntheticConfig(
                    output_dir=output_dir,
                    image_count=12,
                    width=160,
                    height=90,
                    seed=11,
                    name="test_synthetic",
                )
            )

            validate_dataset_manifest_file(manifest_path, LABELS_PATH)
            image_files = sorted((output_dir / "images").glob("*.ppm"))

            self.assertEqual(len(image_files), 12)
            self.assertTrue(manifest_path.exists())

    def test_generation_is_deterministic_for_seed(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first_manifest = generate_synthetic_dataset(
                SyntheticConfig(
                    output_dir=Path(first_dir),
                    image_count=5,
                    seed=99,
                    name="seed_check",
                )
            )
            second_manifest = generate_synthetic_dataset(
                SyntheticConfig(
                    output_dir=Path(second_dir),
                    image_count=5,
                    seed=99,
                    name="seed_check",
                )
            )

            self.assertEqual(first_manifest.read_text(), second_manifest.read_text())


if __name__ == "__main__":
    unittest.main()
