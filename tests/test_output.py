"""Tests for the output-file handling (a locked previous APK must not stop a build)."""
import os, sys, tempfile, unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wbp.common import unlink_with_retry  # noqa: E402


class UnlinkTests(unittest.TestCase):
    def test_missing_file_counts_as_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(unlink_with_retry(Path(tmp) / "none.apk", tries=1, delay=0))

    def test_plain_file_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "a.apk"
            p.write_bytes(b"x")
            self.assertTrue(unlink_with_retry(p, tries=1, delay=0))
            self.assertFalse(p.exists())

    @unittest.skipUnless(os.name == "nt", "Windows refuses to delete an open file; other systems do not")
    def test_locked_file_returns_false_instead_of_raising(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "locked.apk"
            p.write_bytes(b"x")
            with open(p, "rb"):
                self.assertFalse(unlink_with_retry(p, tries=2, delay=0))
            self.assertTrue(unlink_with_retry(p, tries=1, delay=0))


if __name__ == "__main__":
    unittest.main()
