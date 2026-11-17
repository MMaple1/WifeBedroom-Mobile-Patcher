"""deeproom_strip_problems(): mirrors the Deeproom bundle's loaders (which loader, which file, frame count)."""
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wbp.packs import deeproom_strip_problems  # noqa: E402


def png(path, width, height=8):
    raw = b"".join(b"\x00" + bytes(width * 4) for _ in range(height))
    def chunk(t, b):
        return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xFFFFFFFF)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    Path(path).write_bytes(data)


class DeeproomStripTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def pack(self, cat, name, files, descriptor):
        d = self.root / "custom_stuff" / cat / name
        d.mkdir(parents=True)
        (d / descriptor).write_text("[sprite]\norigin_x=80\norigin_y=84\n")
        for fname, w in files.items():
            png(d / fname, w)
        return d

    def test_high_res_portraits_are_fine(self):
        # cinderace_nude / baiken_clothed: 10 frames of 256 px
        d = self.pack("custom_futas", "baiken", {"custom_portrait.png": 2560, "custom_mating_press.png": 1440,
                                                  "custom_reverse_cowgirl.png": 800, "custom_xray.png": 480}, "custom_data.futa")
        self.assertEqual(deeproom_strip_problems(d, "futa"), [])
        w = self.pack("custom_wives", "cinderace", {"custom_portrait.png": 2560, "custom_mating_press.png": 640,
                                                     "custom_reverse_cowgirl.png": 800, "custom_deepthroat.png": 800,
                                                     "custom_xray.png": 640}, "custom_data.spouse")
        self.assertEqual(deeproom_strip_problems(w, "wife"), [])

    def test_modern_only_and_copied_hybrid(self):
        nicole = self.pack("custom_futas", "nicole", {"custom_futa_portrait_0.png": 2176, "custom_futa_mating_press_0.png": 3840,
                                                       "custom_futa_cowgirls_0.png": 3040, "custom_futa_xray_0.png": 2880}, "custom_data.futa")
        self.assertEqual(deeproom_strip_problems(nicole, "futa"), [])
        # heart / angela_flux: _0 files are copies of the 10-frame standard strips; the legacy loader is used
        heart = self.pack("custom_futas", "heart", {"custom_portrait.png": 1280, "custom_futa_portrait_0.png": 1280,
                                                     "custom_mating_press.png": 1440, "custom_futa_mating_press_0.png": 1440,
                                                     "custom_reverse_cowgirl.png": 800, "custom_xray.png": 480}, "custom_data.futa")
        self.assertEqual(deeproom_strip_problems(heart, "futa"), [])

    def test_modern_wife_azure(self):
        azure = self.pack("custom_wives", "azure", {"custom_wife_portrait_0.png": 2176, "custom_wife_mating_press_0.png": 800,
                                                     "custom_wife_cowgirl_0.png": 1760, "custom_wife_reverse_cowgirl_0.png": 1600,
                                                     "custom_wife_deepthroat_0.png": 800, "custom_wife_xray_0.png": 640}, "custom_data.wife")
        self.assertEqual(deeproom_strip_problems(azure, "wife"), [])

    def test_broken_strips_are_reported(self):
        d = self.pack("custom_futas", "isabelle", {"custom_portrait.png": 1412, "custom_mating_press.png": 1440,
                                                    "custom_reverse_cowgirl.png": 800, "custom_xray.png": 640,
                                                    "custom_condom.png": 317}, "custom_data.futa")
        probs = deeproom_strip_problems(d, "futa")
        self.assertEqual(len(probs), 2, probs)  # portrait and X-ray; the 317 px condom is tolerated
        self.assertIn("custom_portrait.png is 1412 px", probs[0])
        self.assertIn("custom_xray.png is 640 px", probs[1])

    def test_partner_without_portrait(self):
        d = self.pack("custom_wives", "noport", {"custom_wife_mating_press_0.png": 800, "custom_wife_cowgirl_0.png": 1760,
                                                  "custom_wife_reverse_cowgirl_0.png": 1600}, "custom_data.wife")
        self.assertTrue(any("no partner portrait" in p for p in deeproom_strip_problems(d, "wife")))


if __name__ == "__main__":
    unittest.main()
