"""Correctness tests for the pre-flight pack check (no snapshot involved).
Run: python -m unittest discover -s tests

These assert what each engine can read, so a regression such as "ModRoom's own packs are skipped"
fails here even if the golden harness baseline was recorded with the bug.
"""
import sys, tempfile, unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wbp.packs import gather_custom_assets, generate_manifest_data, missing_sprites, plan_incompatible_skips, plan_name_bridge  # noqa: E402
from wbp.profiles import get_profile  # noqa: E402

MODERN_WIFE = ["custom_data.wife", "custom_wife_portrait_0.png", "custom_wife_mating_press_0.png",
               "custom_wife_cowgirl_0.png", "custom_wife_reverse_cowgirl_0.png", "custom_wife_xray_0.png"]
MODERN_ALT = MODERN_WIFE + ["custom_wife_mating_press_alt_1.png", "custom_wife_xray_alt_1.png"]
MODERN_FUTA = ["custom_data.futa", "custom_futa_portrait_0.png", "custom_futa_mating_press_0.png",
               "custom_futa_cowgirls_0.png", "custom_futa_xray_0.png"]
STD_SPOUSE = ["custom_data.spouse", "custom_portrait.png", "custom_mating_press.png", "custom_xray.png",
              "custom_cowgirl.png", "custom_reverse_cowgirl.png"]
STD_SPOUSE_NO_COWGIRL = ["custom_data.spouse", "custom_portrait.png", "custom_mating_press.png", "custom_xray.png"]


def make(root, category, name, files):
    d = Path(root) / category / name
    d.mkdir(parents=True)
    for f in files:
        (d / f).write_bytes(b"x")


class NativeNamingTests(unittest.TestCase):
    def check(self, category, files, arch):
        with tempfile.TemporaryDirectory() as tmp:
            make(tmp, category, "Pack", files)
            return plan_incompatible_skips(tmp, target_arch=arch)

    def test_modroom_and_deeproom_keep_native_modern_packs(self):
        for arch in ("modroom33", "deeproom"):
            for category, files in (("custom_wives", MODERN_WIFE), ("custom_wives", MODERN_ALT), ("custom_futas", MODERN_FUTA)):
                portable, skips = self.check(category, files, arch)
                self.assertEqual((portable, skips), (1, []), f"{arch} dropped a native {category} pack")

    def test_v15_cannot_read_modern_names(self):
        for category, files in (("custom_wives", MODERN_WIFE), ("custom_futas", MODERN_FUTA)):
            portable, skips = self.check(category, files, "v15")
            self.assertEqual(portable, 0)
            self.assertEqual(len(skips), 1)

    def test_standard_packs_are_kept_everywhere(self):
        for arch in ("modroom33", "deeproom", "v15"):
            self.assertEqual(self.check("custom_wives", STD_SPOUSE, arch), (1, []))

    def test_modroom_skips_packs_it_would_list_and_then_crash_on(self):
        # ModRoom draws every pose sprite; a pack without a forward cowgirl leaves custom_wife_cowgirl at -1
        portable, skips = self.check("custom_wives", STD_SPOUSE_NO_COWGIRL, "modroom33")
        self.assertEqual((portable, len(skips)), (0, 1))
        self.assertIn("forward cowgirl", skips[0]["reason"])
        for arch in ("deeproom", "v15"):
            self.assertEqual(self.check("custom_wives", STD_SPOUSE_NO_COWGIRL, arch), (1, []))
        # a lover pack needs portrait, mating press, cowgirl and X-ray
        portable, skips = self.check("custom_futas", ["custom_data.futa", "custom_portrait.png", "custom_mating_press.png"], "modroom33")
        self.assertEqual((portable, len(skips)), (0, 1))
        self.assertIn("X-ray", skips[0]["reason"])

    def test_sprites_that_do_not_match_the_folder_are_skipped(self):
        for arch in ("modroom33", "deeproom"):
            portable, skips = self.check("custom_futas", MODERN_WIFE, arch)
            self.assertEqual((portable, len(skips)), (0, 1))
            self.assertIn("custom_wives", skips[0]["reason"])
            portable, skips = self.check("custom_wives", MODERN_FUTA, arch)
            self.assertEqual((portable, len(skips)), (0, 1))

    def test_numbered_data_file_and_missing_descriptor_are_skipped(self):
        for arch in ("modroom33", "deeproom", "v15"):
            self.assertEqual(len(self.check("custom_wives", ["custom_data_1.futa", "custom_portrait.png"], arch)[1]), 1)
            self.assertEqual(len(self.check("custom_wives", ["custom_portrait.png"], arch)[1]), 1)


class ProfileAndPlannerTests(unittest.TestCase):
    def test_profiles_state_what_each_engine_reads(self):
        self.assertTrue(get_profile("modroom33").modern_names_ok)
        self.assertTrue(get_profile("deeproom").modern_names_ok)
        self.assertFalse(get_profile("v15").modern_names_ok)
        self.assertIsNotNone(get_profile("modroom33").needs)
        self.assertIsNone(get_profile("deeproom").needs)
        self.assertIsNone(get_profile("v15").needs)

    def test_planner_keeps_modern_packs_as_authored(self):
        names = {f.lower() for f in MODERN_WIFE}
        for arch in ("deeproom", "modroom33"):
            copies = plan_name_bridge(names, arch, "wife", True)
            self.assertFalse([d for _, d in copies if d == "custom_mating_press.png"], arch)
        # Deeproom also never adds a .spouse (it would route a modern pack to the legacy loader); in ModRoom the
        # descriptor copy is removed afterwards by convert_descriptors, which keeps the real .wife
        self.assertFalse([d for _, d in plan_name_bridge(names, "deeproom", "wife", True) if d == "custom_data.spouse"])

    def test_planner_never_mixes_kinds_and_ignores_v15(self):
        names = {f.lower() for f in STD_SPOUSE}
        copies = plan_name_bridge(names, "modroom33", "wife", False)
        self.assertTrue(copies)
        self.assertFalse([d for _, d in copies if "futa" in d])
        self.assertEqual(plan_name_bridge(names, "v15", "wife", False), [])

    def test_validator_and_packer_agree_on_a_standard_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            make(tmp, "custom_wives", "Pack", STD_SPOUSE)
            folder = Path(tmp) / "custom_wives" / "Pack"
            self.assertEqual(missing_sprites(folder, "wife", get_profile("modroom33")), [])
            built = {a.rsplit("/", 1)[-1] for _, a in gather_custom_assets(tmp, target_arch="modroom33")}
            for needed in ("custom_wife_mating_press_0.png", "custom_wife_cowgirl_0.png", "custom_wife_reverse_cowgirl_0.png"):
                self.assertIn(needed, built)

    def test_validator_and_packer_agree_on_an_incomplete_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            make(tmp, "custom_wives", "Pack", STD_SPOUSE_NO_COWGIRL)
            folder = Path(tmp) / "custom_wives" / "Pack"
            self.assertEqual(missing_sprites(folder, "wife", get_profile("modroom33")), ["forward cowgirl", "reverse cowgirl"])
            built = {a.rsplit("/", 1)[-1] for _, a in gather_custom_assets(tmp, target_arch="modroom33")}
            self.assertNotIn("custom_wife_cowgirl_0.png", built)


class NoDuplicateFoldersTests(unittest.TestCase):
    """Each engine gets files and manifests only in the directory it reads."""

    def dirs(self, paths):
        out = set()
        for p in paths:
            parts = p.split("/")
            if len(parts) > 2 and parts[1].startswith("custom"):
                out.add(parts[1] if parts[1] != "custom_stuff" else "custom_stuff/" + parts[2])
        return out

    def test_deeproom_has_only_custom_stuff(self):
        with tempfile.TemporaryDirectory() as tmp:
            for cat in ("custom_futas", "custom_wives"):
                make(tmp, "custom_stuff/" + cat, "P", ["custom_data.futa" if cat == "custom_futas" else "custom_data.spouse", "custom_portrait.png"])
            man = generate_manifest_data(tmp, target_arch="deeproom")
            files = [a for _, a in gather_custom_assets(tmp, target_arch="deeproom")]
            for d in self.dirs(list(man) + files):
                self.assertTrue(d.startswith("custom_stuff/"), d)
            self.assertTrue(any(k.startswith("assets/custom_stuff/custom_futas/") for k in man))

    def test_modroom_has_only_root_custom_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            make(tmp, "custom_futas", "P", ["custom_data.futa", "custom_portrait.png"])
            make(tmp, "custom_wives", "W", ["custom_data.wife", "custom_wife_portrait_0.png"])
            man = generate_manifest_data(tmp, target_arch="modroom33")
            files = [a for _, a in gather_custom_assets(tmp, target_arch="modroom33")]
            self.assertFalse([k for k in man if k.startswith("assets/custom_stuff/")])
            self.assertEqual(self.dirs(list(man) + files), {"custom_futas", "custom_wives"})

    def test_v15_manifests_stay_under_custom(self):
        with tempfile.TemporaryDirectory() as tmp:
            make(tmp, "custom", "P", ["custom_data.futa", "custom_portrait.png"])
            man = generate_manifest_data(tmp, is_v15=True, target_arch="v15")
            self.assertEqual(self.dirs(list(man)), {"custom"})


if __name__ == "__main__":
    unittest.main()


class BridgeFrameConversionTests(unittest.TestCase):
    """A name bridge between the standard and ModRoom (_0.png) formats converts the strip's frame count."""

    def test_standard_futa_to_modroom_is_padded_to_modern_frame_counts(self):
        from wbp import wbconv
        strips = {"custom_portrait.png": (10, 128), "custom_mating_press.png": (9, 160),
                  "custom_reverse_cowgirl.png": (5, 160), "custom_xray.png": (3, 160)}
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "custom_futas" / "Pack"
            d.mkdir(parents=True)
            (d / "custom_data.futa").write_bytes(b"[info]\n")
            for name, (n, fw) in strips.items():
                wbconv.write_png(d / name, wbconv.Image(n * fw, 2, [bytearray(n * fw * 4) for _ in range(2)]))
            def widths(**kw):
                a = dict((apk, src) for src, apk in gather_custom_assets(tmp, target_arch="modroom33", **kw))
                return {k.rsplit("/", 1)[1]: wbconv.png_size(v)[0] for k, v in a.items() if k.endswith("_0.png")}
            got = widths()
            # a portrait would need dropped/invented frames: renamed unchanged unless approximate is requested
            self.assertEqual(got.get("custom_futa_portrait_0.png"), 10 * 128)
            self.assertEqual(widths(approximate=True).get("custom_futa_portrait_0.png"), 17 * 128)
            self.assertEqual(got.get("custom_futa_mating_press_0.png"), 24 * 160)
            self.assertEqual(got.get("custom_futa_xray_0.png"), 18 * 160)
            self.assertEqual(got.get("custom_futa_cowgirls_0.png"), 19 * 160)


class WifeXrayNamingTests(unittest.TestCase):
    """A .spouse pack's X-ray is renamed to custom_wife_xray_0.png only for ModRoom; other engines keep their names."""

    def test_xray_zero_name_only_under_modroom(self):
        from wbp import wbconv
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "custom_wives" / "Pack"
            d.mkdir(parents=True)
            (d / "custom_data.spouse").write_bytes(b"[info]\n")
            for name, n, fw in (("custom_portrait.png", 10, 128), ("custom_mating_press.png", 4, 160), ("custom_xray.png", 4, 160)):
                wbconv.write_png(d / name, wbconv.Image(n * fw, 2, [bytearray(n * fw * 4) for _ in range(2)]))
            for arch, has_zero in (("modroom33", True), ("deeproom", False), ("v15", False)):
                for approximate in (False, True):
                    paths = {apk: src for src, apk in gather_custom_assets(tmp, is_v15=(arch == "v15"), target_arch=arch, approximate=approximate)}
                    zero = [p for p in paths if p.endswith("custom_wife_xray_0.png")]
                    self.assertEqual(bool(zero), has_zero, (arch, approximate))
                    if zero:
                        self.assertEqual(wbconv.png_size(paths[zero[0]])[0], 4 * 160)   # frames untouched


class ForwardCowgirlAndPortraitTests(unittest.TestCase):
    def _png(self, d, name, n, fw=160):
        from wbp import wbconv
        wbconv.write_png(d / name, wbconv.Image(n * fw, 2, [bytearray(n * fw * 4) for _ in range(2)]))

    def test_partner_without_forward_cowgirl_gets_a_padded_one_for_modroom(self):
        from wbp import wbconv
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "custom_wives" / "Pack"
            d.mkdir(parents=True)
            (d / "custom_data.spouse").write_bytes(b"[info]")
            self._png(d, "custom_mating_press.png", 4)
            self._png(d, "custom_reverse_cowgirl.png", 5)
            paths = {apk: src for src, apk in gather_custom_assets(tmp, target_arch="modroom33")}
            fwd = [p for p in paths if p.endswith("custom_wife_cowgirl_0.png")]
            self.assertEqual(len(fwd), 1)
            self.assertEqual(wbconv.png_size(paths[fwd[0]])[0], 11 * 160)

    def test_loose_portrait_goes_where_the_engine_reads_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "custom_futas" / "Pack"
            d.mkdir(parents=True)
            (d / "custom_data.futa").write_bytes(b"[info]")
            self._png(d, "my_portrait.png", 10, 128)
            for arch, want in (("deeproom", "assets/custom_stuff/custom_futas/pack/custom_portrait.png"), ("modroom33", "assets/custom_futas/pack/custom_portrait.png")):
                got = [apk for _, apk in gather_custom_assets(tmp, target_arch=arch) if apk.endswith("custom_portrait.png")]
                self.assertEqual(got, [want], arch)


class PackNameTests(unittest.TestCase):
    def test_a_repeated_display_name_keeps_the_folder_tag_not_a_doubled_name(self):
        from wbp.packs import unique_apk_name
        used = {"astolfo", "astolfo_futa"}
        self.assertEqual(unique_apk_name("astolfo", "Astolfo (naked)", used), "astolfo_naked")
        self.assertEqual(unique_apk_name("astolfo_futa", "Astolfo (naked)", used), "astolfo_futa_naked")
        self.assertEqual(unique_apk_name("alice", "Alice", {"alice"}), "alice_2")
        self.assertEqual(unique_apk_name("new", "x", {"old"}), "new")
