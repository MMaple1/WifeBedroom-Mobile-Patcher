"""Structural checks on the ModRoom GML patch files (they are compiled by UndertaleModCli at build time;
these catch an unbalanced edit early, without needing the game)."""
import sys, unittest
from pathlib import Path

sys.dont_write_bytecode = True
PATCHES = Path(__file__).resolve().parent.parent / "core" / "gml_patches" / "patch_mr33_engine_bytecode"


class MR33PatchFiles(unittest.TestCase):
    def test_new_gml_is_balanced(self):
        # complete code only: new_bg_pick / new_wife_port / new_wife_mp are fragments that the game's own code finishes
        fragments = {"new_bg_pick.gml", "new_wife_port.gml", "new_wife_mp.gml"}
        files = [f for f in sorted(PATCHES.glob("new_*.gml")) if f.name not in fragments] + [PATCHES / "streaming_logic.gml", PATCHES / "safe_draw.gml"]
        self.assertTrue(files)
        for f in files:
            text = f.read_text(encoding="utf-8")
            code = "".join(c for c in text if c in "{}()[]")
            for a, b in ("{}", "()", "[]"):
                self.assertEqual(code.count(a), code.count(b), f"{f.name}: unbalanced {a}{b}")

    def test_touch_patches_keep_their_contract(self):
        scroll = (PATCHES / "new_menu_scroll_update.gml").read_text(encoding="utf-8")
        self.assertTrue(scroll.startswith("function menu_scroll_update(arg0, arg1, arg2)"))
        for needed in ("touch_armed", "touch_moved", "touch_drag_accum", "mouse_wheel_up"):
            self.assertIn(needed, scroll)
        pill = (PATCHES / "new_pill_menu.gml").read_text(encoding="utf-8")
        self.assertIn("{{PILL_DATA}}", pill)
        self.assertIn("pill_rows_per_col", pill)
        self.assertIn("blockage_pill", pill)  # ModRoom's own click rule is kept
        bg = (PATCHES / "new_bg_pick.gml").read_text(encoding="utf-8")
        self.assertIn('variable_struct_exists(bg_menu, "touch_armed")', bg)  # the field may not exist before the first Step

    def test_bedroom_names_are_filled_by_the_game_check(self):
        loop = (PATCHES / "new_bg_loop.gml").read_text(encoding="utf-8")
        self.assertIn("func_check_custom_background(", loop)  # it fills custom_background_name_array
        self.assertIn("custom_background_name_array = [];", loop)


if __name__ == "__main__":
    unittest.main()
