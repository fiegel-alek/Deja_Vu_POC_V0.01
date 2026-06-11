from pathlib import Path
import unittest

from src.dataset_inventory import build_inventory, format_inventory, load_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "dataset.example.json"


class DatasetInventoryTest(unittest.TestCase):
    def test_reports_counts_by_label_and_split(self) -> None:
        inventory = build_inventory(load_manifest(MANIFEST_PATH))

        self.assertEqual(inventory.image_count, 3)
        self.assertEqual(inventory.annotation_count, 2)
        self.assertEqual(inventory.negative_image_count, 1)
        self.assertEqual(inventory.images_by_split["train"], 1)
        self.assertEqual(inventory.annotations_by_label["handgun_visible"], 1)
        self.assertEqual(inventory.annotations_by_label["fire_or_smoke"], 1)

    def test_formats_inventory_report(self) -> None:
        report = format_inventory(build_inventory(load_manifest(MANIFEST_PATH)))

        self.assertIn("Images: 3", report)
        self.assertIn("handgun_visible: 1", report)


if __name__ == "__main__":
    unittest.main()
