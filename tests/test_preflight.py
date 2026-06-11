from pathlib import Path
import tempfile
import unittest

from src.preflight import has_required_failures, load_local_properties, run_preflight


class PreflightTest(unittest.TestCase):
    def test_loads_local_properties(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "local.properties"
            path.write_text("github_token=abc\nMETA_DAT_APPLICATION_ID=app\n", encoding="utf-8")

            properties = load_local_properties(path)

            self.assertEqual(properties["github_token"], "abc")
            self.assertEqual(properties["META_DAT_APPLICATION_ID"], "app")

    def test_reports_required_failures_when_credentials_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "gradle" / "wrapper").mkdir(parents=True)
            (root / "gradlew").write_text("#!/bin/sh\n", encoding="utf-8")
            (root / "gradle" / "wrapper" / "gradle-wrapper.jar").write_bytes(b"jar")
            (root / "gradle" / "wrapper" / "gradle-wrapper.properties").write_text(
                "distributionUrl=https://example.com/gradle.zip\n",
                encoding="utf-8",
            )

            checks = run_preflight(root)

            self.assertTrue(has_required_failures(checks))
            self.assertTrue(any(check.name == "Java runtime / JDK" for check in checks))


if __name__ == "__main__":
    unittest.main()
