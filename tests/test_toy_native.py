"""The toy patches the patcher applies itself (formerly GamePatcher.exe): anchors and idempotence."""
import sys, unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wbp import toy_native as T  # noqa: E402

CREATE = "a = 1;\nthrust_time = 0;\nb = 2;\n"
DRAW = "var x = 1;\nthrust_prev = thrust;\nfoo();\nmouse_y_prev = mouse_y;\n\nenum E\n{\n    A\n}\n"


class ToyNativeTests(unittest.TestCase):
    def test_create_gets_each_feature_after_the_anchor_once(self):
        once = T.patch_text(T.PRESS + "Create_0", CREATE, {"direct", "udp", "hmv"})
        self.assertIn("tb_scene_at = -100000;", once)
        self.assertIn("hmv_socket = network_create_socket_ext(1, 45736);", once)
        self.assertTrue(once.startswith("a = 1;\nthrust_time = 0;\n") and once.endswith("b = 2;\n"))
        self.assertEqual(T.patch_text(T.PRESS + "Create_0", once, {"direct", "udp", "hmv"}), once)

    def test_draw_direct_top_anchor_and_end_before_the_enum(self):
        out = T.patch_text(T.PRESS + "Draw_0", DRAW, {"direct", "hmv"})
        self.assertTrue(out.startswith("if (tb_enabled)"))
        self.assertLess(out.index("mouse_y_prev = mouse_y;"), out.index("var _hmv_s = hmv_speaker_size;"))
        self.assertLess(out.index("var _hmv_s = hmv_speaker_size;"), out.index("enum E"))
        self.assertLess(out.index("if (tb_enabled && title == true)"), out.index("var _hmv_s = hmv_speaker_size;"))  # direct before hmv

    def test_missing_anchor_is_recorded_not_raised(self):
        before = len(T.PATCH_MISSES)
        self.assertEqual(T.patch_text(T.PRESS + "Create_0", "nothing here\n", {"direct"}), "nothing here\n")
        self.assertEqual(len(T.PATCH_MISSES), before + 1)

    def test_background_tint_replaces_white_arguments(self):
        out = T.patch_text(T.BACKGROUND_DRAW, "draw_sprite_ext(background_sprite, 0, x, y, 1, 1, 0, c_white, 1);\n", {"hmv"})
        self.assertIn(T.HMV_COLOR, out)
        self.assertNotIn("c_white", out)

    def test_direct_client_applies_the_latency_lead(self):
        create = T._snip("direct_create")
        draw = T._snip("direct_draw_top")
        self.assertIn('tb_lead = clamp(floor(ini_read_real("toy", "lead", tb_lead)), 0, 500);', create)
        self.assertIn("working_directory + \"toy_direct.ini\"", create)   # the packaged defaults are read as well as the save folder
        self.assertIn("if (tb_lead > 0)", draw)
        self.assertIn("var _tb_pos = _tb_lo + (_tb_pos_src * (_tb_hi - _tb_lo));", draw)

    def test_networking_event_holds_both_handlers(self):
        both = T.other_68_text({"direct", "hmv"})
        self.assertIn("tb_sock", both)
        self.assertIn("hmv_socket", both)
        self.assertEqual(T.other_68_text(set()), "")

    def test_bundle_code_takes_the_udp_blocks_once(self):
        core = Path(__file__).resolve().parent.parent / "core" / "bundle_src"
        misses = len(T.PATCH_MISSES)
        for ent in ("Create_0", "Draw_0"):
            text = (core / (T.PRESS + ent + ".gml")).read_text(encoding="utf-8")
            once = T.patch_text(T.PRESS + ent, text, {"udp", "direct"})
            self.assertNotEqual(once, text)
            self.assertEqual(T.patch_text(T.PRESS + ent, once, {"udp", "direct"}), once)
        self.assertEqual(len(T.PATCH_MISSES), misses)


if __name__ == "__main__":
    unittest.main()
