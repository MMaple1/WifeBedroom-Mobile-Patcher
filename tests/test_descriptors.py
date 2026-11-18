"""Unit tests for wbp.descriptors.   Run: python -m unittest discover -s tests"""
import sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wbp.descriptors import Ini, convert, convert_descriptors  # noqa: E402

SPOUSE = (b"[sprite]\r\norigin_x = 80\r\norigin_y = 84\r\n\r\n[mating_press]\r\norigin_x = 70\r\norigin_y = 71\r\n\r\n"
          b"[reverse_cowgirl]\r\norigin_x = 60\r\norigin_y = 61\r\n\r\n[xray]\r\norigin_x = 50\r\norigin_y = 51\r\n\r\n"
          b"[deepthroat]\r\norigin_x = 40\r\norigin_y = 41\r\n")
WIFE = b"[sprite]\norigin_x = 80\norigin_y = 84\nmating_press_origin_x = 7\nmating_press_origin_y = 8\ncowgirl_origin_x = 9\n\n[stats]\nbottom_boob_size = 1\n"


class IniTests(unittest.TestCase):
    def test_untouched_file_is_returned_as_is(self):
        data = b"[a]\nx=1\n"
        self.assertIs(convert(data, "spouse", "wife"), data)
        self.assertIs(convert(data, "futa", "v15_futa", ""), data)

    def test_add_keeps_existing_lines_and_line_endings(self):
        out = convert(SPOUSE, "spouse", "wife")
        self.assertIn(b"\r\n", out)
        self.assertNotIn(b"\n", out.replace(b"\r\n", b""))
        for line in SPOUSE.split(b"\r\n"):
            self.assertIn(line, out.split(b"\r\n"))

    def test_spouse_to_wife_derives_flat_keys(self):
        ini = Ini(convert(SPOUSE, "spouse", "wife"))
        self.assertEqual(ini.get("sprite", "mating_press_origin_x"), "70")
        self.assertEqual(ini.get("sprite", "mating_press_origin_y"), "71")
        self.assertEqual(ini.get("sprite", "cowgirl_origin_x"), "60")
        self.assertEqual(ini.get("sprite", "deepthroat_origin_y"), "41")
        self.assertEqual(ini.get("mating_press", "origin_x"), "70")  # source keys are kept

    def test_existing_keys_are_never_overwritten(self):
        data = SPOUSE.replace(b"[sprite]\r\n", b"[sprite]\r\nmating_press_origin_x = 5\r\n")
        self.assertEqual(Ini(convert(data, "spouse", "wife")).get("sprite", "mating_press_origin_x"), "5")

    def test_wife_to_v15_spouse(self):
        ini = Ini(convert(WIFE, "wife", "v15_spouse", "Ankha"))
        self.assertEqual(ini.get("mating_press", "origin_x"), "7")
        self.assertEqual(ini.get("reverse_cowgirl", "origin_x"), "9")
        self.assertEqual(ini.get("info", "name"), '"Ankha"')
        self.assertEqual(ini.get("stats", "bottom_boob_size"), "1")

    def test_spouse_to_v15_gets_xray_and_deepthroat_keys(self):
        ini = Ini(convert(SPOUSE, "spouse", "v15_spouse", "X"))
        self.assertEqual(ini.get("sprite", "xray_x"), "50")
        self.assertEqual(ini.get("sprite", "xray_y"), "51")
        self.assertEqual(ini.get("sprite", "deepthroat_origin_y"), '"111.000000"')  # Deeproom 41 + 70

    def test_info_name_not_added_when_present(self):
        data = b'[info]\nname="Real"\n[sprite]\norigin_x=1\n'
        self.assertEqual(Ini(convert(data, "futa", "v15_futa", "Folder")).get("info", "name"), '"Real"')

    def test_bom_and_case_insensitive_sections(self):
        data = b"\xef\xbb\xbf[Sprite]\nORIGIN_X = 3\n[Mating_Press]\nOrigin_X = 4\n"
        out = convert(data, "spouse", "wife")
        self.assertTrue(out.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(Ini(out).get("sprite", "mating_press_origin_x"), "4")


class AssetListTests(unittest.TestCase):
    def _pack(self, tmp, folder, files):
        d = Path(tmp) / folder
        d.mkdir(parents=True)
        for name, data in files.items():
            (d / name).write_bytes(data)
        return d

    def test_deeproom_is_untouched(self):
        assets = [("a", "assets/custom_stuff/custom_wives/x/custom_data.spouse")]
        out, gen = convert_descriptors(assets, "deeproom")
        self.assertIs(out, assets)
        self.assertEqual(gen, {})

    def test_modroom_spouse_pack_gets_one_wife_descriptor(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self._pack(tmp, "Marisa", {"custom_data.spouse": SPOUSE})
            apk = "assets/custom_wives/marisa"
            assets = [(d / "custom_data.spouse", apk + "/custom_data.spouse"),
                      (d / "custom_data.spouse", apk + "/custom_data.wife"),  # the clone the bridge makes
                      (d / "x.png", apk + "/x.png")]
            out, gen = convert_descriptors(assets, "modroom33")
            self.assertEqual([a[1] for a in out], [apk + "/x.png"])
            self.assertEqual(list(gen), [apk + "/custom_data.wife"])
            self.assertEqual(Ini(gen[apk + "/custom_data.wife"]).get("sprite", "mating_press_origin_x"), "70")

    def test_modroom_real_wife_pack_is_kept_and_spouse_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self._pack(tmp, "W", {"custom_data.wife": WIFE, "custom_data.spouse": SPOUSE})
            apk = "assets/custom_wives/w"
            assets = [(d / "custom_data.wife", apk + "/custom_data.wife"), (d / "custom_data.spouse", apk + "/custom_data.spouse")]
            out, gen = convert_descriptors(assets, "modroom33")
            self.assertEqual([a[1] for a in out], [apk + "/custom_data.wife"])
            self.assertEqual(gen, {})

    def test_hybrid_pack_is_left_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self._pack(tmp, "H", {"custom_data.futa": b"[a]\nx=1\n", "custom_data.spouse": SPOUSE})
            apk = "assets/custom_wives/h"
            assets = [(d / "custom_data.futa", apk + "/custom_data.futa"), (d / "custom_data.spouse", apk + "/custom_data.spouse")]
            out, gen = convert_descriptors(assets, "modroom33")
            self.assertEqual(out, assets)
            self.assertEqual(gen, {})

    def test_v15_wife_becomes_spouse_and_futa_gets_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self._pack(tmp, "Wifey", {"custom_data.wife": WIFE})
            f = self._pack(tmp, "Lover", {"custom_data.futa": b"[sprite]\norigin_x=1\n"})
            assets = [(w / "custom_data.wife", "assets/custom/wifey/custom_data.wife"),
                      (f / "custom_data.futa", "assets/custom/lover/custom_data.futa")]
            out, gen = convert_descriptors(assets, "v15")
            self.assertEqual(out, [])
            self.assertEqual(Ini(gen["assets/custom/wifey/custom_data.spouse"]).get("info", "name"), '"Wifey"')
            self.assertEqual(Ini(gen["assets/custom/lover/custom_data.futa"]).get("info", "name"), '"Lover"')

    def test_v15_native_pack_with_info_is_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = self._pack(tmp, "Own", {"custom_data.spouse": b'[info]\nname="Own"\n[sprite]\norigin_x=1\n'})
            assets = [(d / "custom_data.spouse", "assets/custom/own/custom_data.spouse")]
            out, gen = convert_descriptors(assets, "v15")
            self.assertEqual(out, assets)
            self.assertEqual(gen, {})


if __name__ == "__main__":
    unittest.main()
