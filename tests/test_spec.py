"""The technical specification stays true to the shipped code (see tools/spec_check.py)."""
import sys, unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import spec_check  # noqa: E402


class SpecTests(unittest.TestCase):
    def test_every_excerpt_is_shipped_code_and_no_review_notes_remain(self):
        bad, words = spec_check.check(str(ROOT / "core" / "TECHNICAL_SPECIFICATION.md"))
        self.assertEqual((bad, words), (0, 0))


if __name__ == "__main__":
    unittest.main()
