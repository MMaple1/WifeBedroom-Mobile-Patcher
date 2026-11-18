"""The converters and the patcher each carry a copy of wbconv.py; they must stay identical.
If this fails: edit only WB_Converters/Modded_to_WB_1.5/core/wbconv.py, then run `python tools/sync_wbconv.py`."""
import sys, unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import sync_wbconv  # noqa: E402


class WbconvSyncTests(unittest.TestCase):
    def test_copies_are_identical(self):
        diff = sync_wbconv.differing()
        if diff is None:
            self.skipTest("WB_Converters repo not next to the patcher")
        self.assertEqual(diff, [], "wbconv.py copies differ; run tools/sync_wbconv.py")


if __name__ == "__main__":
    unittest.main()
