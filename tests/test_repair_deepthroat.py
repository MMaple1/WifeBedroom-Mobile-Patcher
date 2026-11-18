"""Tests for wbconv.repair_deepthroat_* (undo the [deepthroat] block old converters wrote).   Run: python -m unittest discover -s tests"""
import sys, tempfile, unittest, zipfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wbp import wbconv as W  # noqa: E402

# What converters before 2026-11-17 wrote: origin_x copied from [sprite], origin_y v1.5's default.
INVENTED = (b'[sprite]\r\norigin_x="80.000000"\r\norigin_y="84.000000"\r\n\r\n'
            b'[deepthroat]\r\norigin_x="80.000000"\r\norigin_y="150.000000"\r\n\r\n'
            b'[stats]\r\nboob_size="1"\r\n')
# A v1.5 deepthroat_origin_y copied 1:1.
COPIED = (b'[sprite]\norigin_x="80.000000"\norigin_y="84.000000"\ndeepthroat_origin_y="170.000000"\n\n'
          b'[deepthroat]\norigin_x="80.000000"\norigin_y="170.000000"\n')


class RepairBytes(unittest.TestCase):
    def test_invented_block_is_removed_and_rest_kept(self):
        out = W.repair_deepthroat_bytes(INVENTED)
        self.assertEqual(out, b'[sprite]\r\norigin_x="80.000000"\r\norigin_y="84.000000"\r\n\r\n[stats]\r\nboob_size="1"\r\n')

    def test_invented_block_at_end_of_file(self):
        data = b'[sprite]\norigin_x="80.000000"\n\n[deepthroat]\norigin_x="80.000000"\norigin_y="150.000000"\n'
        out = W.repair_deepthroat_bytes(data)
        self.assertNotIn(b"deepthroat", out)
        self.assertTrue(out.startswith(b'[sprite]\norigin_x="80.000000"\n'))

    def test_copied_v15_value_gets_minus_70(self):
        out = W.repair_deepthroat_bytes(COPIED)
        ini = W.Ini(out)
        self.assertEqual(ini.get("deepthroat", "origin_y"), '"100.000000"')
        self.assertEqual(ini.get("sprite", "deepthroat_origin_y"), '"170.000000"')

    def test_idempotent(self):
        for data in (INVENTED, COPIED):
            once = W.repair_deepthroat_bytes(data)
            self.assertIs(W.repair_deepthroat_bytes(once), once)

    def test_bom_is_kept(self):
        out = W.repair_deepthroat_bytes(b"\xef\xbb\xbf" + INVENTED)
        self.assertTrue(out.startswith(b"\xef\xbb\xbf[sprite]"))
        self.assertNotIn(b"deepthroat", out)

    def test_hand_made_blocks_are_untouched(self):
        cases = [
            INVENTED.replace(b'origin_y="150.000000"', b'origin_y="140.000000"'),         # other value
            INVENTED.replace(b'origin_y="150.000000"', b'origin_y=150'),                  # author's own spelling
            INVENTED.replace(b'[deepthroat]\r\norigin_x="80.000000"', b'[deepthroat]\r\norigin_x="90.000000"'),  # x differs
            INVENTED.replace(b'[deepthroat]\r\n', b'[deepthroat]\r\n; tuned by hand\r\n'),  # comment
            INVENTED.replace(b'[deepthroat]\r\n', b'[deepthroat]\r\nscale="1"\r\n'),       # extra key
            INVENTED + b'\r\n[deepthroat]\r\norigin_y="150.000000"\r\n',                  # two blocks
            INVENTED.replace(b'[deepthroat]\r\n', b'[deepthroat]\r\norigin_y="140.000000"\r\n'),  # repeated key
            b'[sprite]\norigin_x="80.000000"\n',                                          # no block
            COPIED.replace(b'deepthroat_origin_y="170.000000"', b'deepthroat_origin_y="160.000000"'),  # not a copy
            INVENTED.replace(b'[sprite]\r\n', b'[sprite]\r\ndeepthroat_origin_y="150.000000"\r\n').replace(
                b'origin_x="80.000000"\r\norigin_y="150.000000"', b'origin_x="80.000000"\r\norigin_y="80.000000"'),  # new converter output
        ]
        for data in cases:
            self.assertIs(W.repair_deepthroat_bytes(data), data, data)

    def test_new_converter_output_is_not_touched(self):
        v15 = b'[sprite]\norigin_x="80.000000"\norigin_y="84.000000"\ndeepthroat_origin_y="150.000000"\n'
        out = W.convert_descriptor_bytes(v15, "spouse", "spouse")
        self.assertIs(W.repair_deepthroat_bytes(out), out)


class RepairFolder(unittest.TestCase):
    def test_dry_run_then_apply_with_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "custom_wives"
            for name, data in (("a", INVENTED), ("b", COPIED), ("c", b"[sprite]\norigin_x=1\n")):
                (root / name).mkdir(parents=True)
                (root / name / "custom_data.spouse").write_bytes(data)
            found = W.repair_deepthroat_folder(root)
            self.assertEqual([p.parent.name for p in found], ["a", "b"])
            self.assertEqual((root / "a" / "custom_data.spouse").read_bytes(), INVENTED)  # dry run wrote nothing
            with self.assertRaises(ValueError):
                W.repair_deepthroat_folder(root, apply=True)
            backup = Path(tmp) / "backup.zip"
            W.repair_deepthroat_folder(root, apply=True, backup=backup)
            self.assertNotIn(b"deepthroat", (root / "a" / "custom_data.spouse").read_bytes())
            with zipfile.ZipFile(backup) as z:
                self.assertEqual(sorted(z.namelist()), ["a/custom_data.spouse", "b/custom_data.spouse"])
                self.assertEqual(z.read("a/custom_data.spouse"), INVENTED)
            self.assertEqual(W.repair_deepthroat_folder(root), [])
            with self.assertRaises(FileExistsError):
                (root / "a" / "custom_data.spouse").write_bytes(INVENTED)
                W.repair_deepthroat_folder(root, apply=True, backup=backup)

    def test_links_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "outside.spouse"
            outside.write_bytes(INVENTED)
            root = Path(tmp) / "custom_wives"
            (root / "a").mkdir(parents=True)
            try:
                (root / "a" / "custom_data.spouse").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("no symlink permission")
            self.assertEqual(W.repair_deepthroat_folder(root), [])

    def test_no_temp_file_left_after_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "custom_wives"
            (root / "a").mkdir(parents=True)
            (root / "a" / "custom_data.spouse").write_bytes(INVENTED)
            W.repair_deepthroat_folder(root, apply=True, backup=Path(tmp) / "b.zip")
            self.assertEqual(sorted(p.name for p in (root / "a").iterdir()), ["custom_data.spouse"])

    def test_cli_reports_errors_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "custom_wives"
            (root / "a").mkdir(parents=True)
            (root / "a" / "custom_data.spouse").write_bytes(INVENTED)
            real = W.repair_deepthroat_folder

            def boom(*a, **k):
                raise PermissionError("locked")
            W.repair_deepthroat_folder = boom
            try:
                self.assertEqual(W.repair_deepthroat_main([str(root), "--apply"]), 1)
            finally:
                W.repair_deepthroat_folder = real

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "custom_wives"
            (root / "a").mkdir(parents=True)
            (root / "a" / "custom_data.spouse").write_bytes(INVENTED)
            self.assertEqual(W.repair_deepthroat_main([str(root)]), 0)
            self.assertEqual((root / "a" / "custom_data.spouse").read_bytes(), INVENTED)
            self.assertEqual(W.repair_deepthroat_main([str(root), "--apply"]), 0)
            self.assertNotIn(b"deepthroat", (root / "a" / "custom_data.spouse").read_bytes())
            self.assertEqual(len(list(Path(tmp).glob("custom_wives_deepthroat_backup_*.zip"))), 1)


if __name__ == "__main__":
    unittest.main()
