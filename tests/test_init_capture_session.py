from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class InitCaptureSessionTest(unittest.TestCase):
    def test_slugify_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            script = Path(__file__).resolve().parents[1] / "scripts" / "init_capture_session.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "Basement Replica Set",
                    "--date",
                    "20260611",
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            # The script is rooted to the repo, so this smoke test only asserts CLI behavior.
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("capture_20260611_basement_replica_set", result.stdout)


if __name__ == "__main__":
    unittest.main()
