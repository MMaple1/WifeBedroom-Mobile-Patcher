"""Static checks on the Deeproom bundle source for mistakes that compile but break the game."""
import re
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "core" / "bundle_src"


class BundleLintTests(unittest.TestCase):
    def test_no_instance_check_on_globals(self):
        # variable_instance_exists(id, "global.x") is never true: the guarded reset then runs every frame
        # (this reset global.mob_touching_menu each frame, so overlay menu buttons stopped responding).
        hits = [f"{p.name}:{i}" for p in SRC.glob("*.gml")
                for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
                if re.search(r'variable_instance_exists\(\s*id\s*,\s*"global\.', line)]
        self.assertEqual(hits, [])

    def test_overlay_menu_click_on_release(self):
        draw = (SRC / "gml_Object_oFutaMatingPress_Draw_0.gml").read_text(encoding="utf-8")
        self.assertIn('if (!variable_global_exists("mob_touching_menu"))', draw)
        self.assertIn("// a very quick tap: pressed and released in the same frame", draw)


if __name__ == "__main__":
    unittest.main()
