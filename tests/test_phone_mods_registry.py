"""Phone mods (Deeproom bundle): every import records what it creates in the registry, and REMOVE / VOICES /
startup read the registry, so they do not depend on listing folders on Android."""
import re
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "core" / "bundle_src"
CREATE = (SRC / "gml_Object_oFutaMatingPress_Create_0.gml").read_text(encoding="utf-8")
DRAW = (SRC / "gml_Object_oFutaMatingPress_Draw_0.gml").read_text(encoding="utf-8")
HTTP = (SRC / "gml_Object_oFutaMatingPress_Other_62.gml").read_text(encoding="utf-8")


class RegistryTests(unittest.TestCase):
    def test_helpers_exist(self):
        for fn in ("pm_registry_read", "pm_registry_write", "pm_registry_add", "pm_registry_remove", "tc_is_save_path"):
            self.assertIn(f"function {fn}(", CREATE)

    def test_every_import_site_records(self):
        for name, code in (("Draw_0 (inbox / local path / Open with)", DRAW), ("Other_62 (https)", HTTP)):
            lines = code.splitlines()
            for i, line in enumerate(lines):
                if re.search(r'ds_list_add\(custom_(futas|wives)_folder, _full_path\);', line) or \
                        re.search(r'var _pm_cdst = \[_pm_save \+ "/(custom_bedrooms|phone_voices)/"', line) or \
                        re.search(r'file_copy\([^,]+, _pm_save \+ "/dialogue_packs/"', line):
                    self.assertIn("pm_registry_add(", lines[i + 1], f"{name} line {i + 1}: {line.strip()}")

    def test_readers_and_remove(self):
        self.assertIn("var _rm_reg = pm_registry_read();", DRAW)      # REMOVE list
        self.assertIn("var _pk_reg = pm_registry_read();", DRAW)      # VOICES list
        self.assertIn("pm_registry_remove(pm_rm_path);", DRAW)        # removing drops the entry
        self.assertIn("var _pm_reg = pm_registry_read();", CREATE)    # startup re-registration

    def test_save_paths_stay_absolute(self):
        self.assertIn('&& !tc_is_save_path(arg0))', CREATE)
        self.assertIn("tc_is_save_path(arg0))\n    {\n        // folders created on the phone have no _manifest.txt", CREATE)


if __name__ == "__main__":
    unittest.main()
