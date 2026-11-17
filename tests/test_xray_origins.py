"""Deeproom X-ray origins measured at build time against each pack's own body
(wbp.descriptors._deeproom_xray_origins) against each pack's own sprite. The strips are written with the standard-library
writer, so the tests also run without Pillow (the feature then uses wbconv.read_png)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wbp import descriptors  # noqa: E402

from wbp import wbconv  # noqa: E402


def strip(path, frame_w, height, frames, boxes, extra=()):
    """Strip of `frames` frames; boxes = {frame: [(x0, y0, x1, y1), ...]} in frame coordinates;
    extra = single opaque pixels (x, y) in strip coordinates."""
    width = int(frame_w * frames)
    rows = [bytearray(width * 4) for _ in range(height)]
    for f, rects in boxes.items():
        for x0, y0, x1, y1 in rects:
            for y in range(y0, y1):
                for x in range(int(f * frame_w + x0), int(f * frame_w + x1)):
                    rows[y][x * 4:x * 4 + 4] = b"\xff\x00\x00\xff"
    for x, y in extra:
        rows[y][x * 4:x * 4 + 4] = b"\xff\xff\xff\xff"
    wbconv.write_png(path, wbconv.Image(width, height, rows))


class XrayOriginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def partner(self, name, canal, body, ini=""):
        d = self.root / "custom_wives" / name
        d.mkdir(parents=True)
        (d / "custom_data.spouse").write_text("[sprite]\norigin_x=80\norigin_y=84\n" + ini)
        strip(d / "custom_xray.png", 160, 168, 4, {0: [canal]})
        strip(d / "custom_mating_press.png", 160, 168, 4, {0: [body]})
        return [(str(f), f"assets/custom_stuff/custom_wives/{name}/{f.name}") for f in sorted(d.iterdir())]

    def lover(self, name, shaft, visible):
        d = self.root / "custom_futas" / name
        d.mkdir(parents=True)
        (d / "custom_data.futa").write_text("[sprite]\norigin_x=80\norigin_y=84\n")
        strip(d / "custom_xray.png", 160, 168, 3, {0: [shaft]})
        strip(d / "custom_mating_press.png", 160, 168, 9, {7: [visible]})
        return [(str(f), f"assets/custom_stuff/custom_futas/{name}/{f.name}") for f in sorted(d.iterdir())]

    # X-ray centred on x=79 (55..103), bottom edge at 84+70=154; sprite centred on x=80, bottom at 127
    XRAY_BOX = (55, 78, 103, 154)
    BODY = (40, 20, 120, 127)

    def test_standard_partner_untouched(self):
        assets = self.partner("std", self.XRAY_BOX, self.BODY)
        self.assertEqual(descriptors.convert_descriptors(assets, "deeproom"), (assets, {}))

    def test_origin_copied_from_body_is_corrected(self):
        # scarlett / bon(bbw): standard art, centred body, but [xray] origin_x=110
        assets = self.partner("shifted", self.XRAY_BOX, self.BODY, "[xray]\norigin_x=110\norigin_y=84\n")
        _, gen = descriptors.convert_descriptors(assets, "deeproom")
        text = gen["assets/custom_stuff/custom_wives/shifted/custom_data.spouse"].decode()
        self.assertIn("origin_x=110", text)          # authored values kept
        self.assertIn("mobile_origin_x=79", text)    # X-ray centre (79) back on the sprite centre
        self.assertIn("mobile_origin_y=84", text)

    def test_body_shifted_the_same_way_is_left_alone(self):
        # X-ray 30 px off the average, but the body is shifted by the same 30 px: intentional
        assets = self.partner("intent", self.XRAY_BOX, (10, 20, 90, 127), "[xray]\norigin_x=110\n")
        self.assertEqual(descriptors.convert_descriptors(assets, "deeproom")[1], {})

    def test_stray_pixels_do_not_count(self):
        d_assets = self.partner("stray", self.XRAY_BOX, self.BODY)
        strip(self.root / "custom_wives" / "stray" / "custom_xray.png", 160, 168, 4, {0: [self.XRAY_BOX]}, extra=[(150, 5), (151, 5)])
        self.assertEqual(descriptors.convert_descriptors(d_assets, "deeproom")[1], {})

    def test_lover_shaft_off_its_body_gets_x_only(self):
        # X-ray drawn 30 px left in its frame, sprite centred; height off too, but lover y is never changed
        assets = self.lover("banyue", (32, 20, 66, 120), (63, 100, 98, 150))
        _, gen = descriptors.convert_descriptors(assets, "deeproom")
        text = gen["assets/custom_stuff/custom_futas/banyue/custom_data.futa"].decode()
        self.assertIn("mobile_origin_x=48", text)    # X-ray centre 49 -> sprite centre 80.5 + median 0.5
        self.assertIn("mobile_origin_y=84", text)

    def test_lover_on_its_body_untouched(self):
        assets = self.lover("ok", (63, 57, 97, 160), (63, 100, 98, 150))
        self.assertEqual(descriptors.convert_descriptors(assets, "deeproom")[1], {})

    def test_option_off_writes_nothing(self):
        assets = self.partner("off", self.XRAY_BOX, self.BODY, "[xray]\norigin_x=110\norigin_y=84\n")
        self.assertEqual(descriptors.convert_descriptors(assets, "deeproom", xray_origins=False), (assets, {}))
        self.assertEqual(descriptors.XRAY_ORIGIN_REPORT, [])

    def test_other_targets_ignored(self):
        assets = self.partner("v", self.XRAY_BOX, self.BODY, "[xray]\norigin_x=110\n")
        self.assertNotIn("mobile_origin_x", str(descriptors.convert_descriptors(assets, "v15")[1]))


if __name__ == "__main__":
    unittest.main()
