"""Every ini_read_* in the bundled engine scripts happens while an ini file is open (reading with none open is the
"Trying to read from undefined INI file" crash a partner pack with an X-ray strip used to cause)."""
import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SRC = Path(__file__).resolve().parent.parent / "core" / "bundle_src"
HELPERS = {"func_check_custom_dialogue"}   # called by code that has the file open


class BundleIniTests(unittest.TestCase):
    def test_no_ini_read_without_an_open_file(self):
        bad = []
        for f in sorted(SRC.glob("*.gml")):
            is_open, fn = False, ""
            for no, line in enumerate(f.read_text(encoding="utf-8").split(chr(10)), 1):
                m = re.match(r"function (\w+)", line)
                if m:
                    fn, is_open = m.group(1), False
                if "ini_open" in line:
                    is_open = True
                if "ini_close" in line:
                    is_open = False
                if fn and fn not in HELPERS and re.search(r"\bini_read_(real|string)\(", line) and not is_open:
                    bad.append(f"{f.name}:{no} in {fn}")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
