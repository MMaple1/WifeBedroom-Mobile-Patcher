"""wbp.descriptors - one character descriptor per exported pack, in the target engine's own format.

Engines read different descriptor files and keys (see core/ENGINE_ARCHITECTURE_REPORT.md, sections 9-10):
  ModRoom V3.3   partner: custom_data.wife only (flat [sprite] keys)
  Deeproom 4.0.3 partner: custom_data.spouse (per-pose sections) or custom_data.wife; left exactly as authored
  Wife's Bedroom v1.5 partner: custom_data.spouse, lover: custom_data.futa, both with an [info] block

The conversion is additive: every key of the source is kept, keys the target reads are derived from
keys it does not, and a key that is already present is never overwritten. Values are never changed.
A file that needs no change is passed through untouched. Packs that hold both a .futa and a
.spouse/.wife descriptor are left alone.
"""
import re
from pathlib import Path

# (section, key) of the legacy spouse layout  <->  the flat [sprite] key of the wife layout
_POSE_MAP = [
    (("mating_press", "origin_x"), ("sprite", "mating_press_origin_x")),
    (("mating_press", "origin_y"), ("sprite", "mating_press_origin_y")),
    (("deepthroat", "origin_x"), ("sprite", "deepthroat_origin_x")),
    (("deepthroat", "origin_y"), ("sprite", "deepthroat_origin_y")),
    (("reverse_cowgirl", "origin_x"), ("sprite", "cowgirl_origin_x")),
    (("reverse_cowgirl", "origin_y"), ("sprite", "cowgirl_origin_y")),
]
# v1.5 reads the X-ray origin from [sprite]; the deepthroat height is not 1:1 (see _dt_to_v15)
_V15_MAP = [
    (("xray", "origin_x"), ("sprite", "xray_x")),
    (("xray", "origin_y"), ("sprite", "xray_y")),
]
# v1.5 draws a partner's deepthroat strip where the vanilla sWifeDeepthroat goes; Deeproom's spouse loader draws it
# 70 px higher (legacy_dt_y_offset = -70). Same constant as wbconv.DT_V15_TO_DEEPROOM.
DT_V15_TO_DEEPROOM = -70


def _num(value):
    try:
        return float(str(value).strip().strip('"'))
    except (TypeError, ValueError):
        return None


def _dt_to_v15(ini):
    """[sprite] deepthroat_origin_y for v1.5 from a Deeproom [deepthroat] origin_y (plus 70)."""
    if ini.get("sprite", "deepthroat_origin_y") is not None:
        return
    v = _num(ini.get("deepthroat", "origin_y"))
    if v is None:
        return  # no Deeproom deepthroat block: v1.5 uses its own default (150), within 4 px of Deeproom's
    ini.add("sprite", "deepthroat_origin_y", f'"{v - DT_V15_TO_DEEPROOM:.6f}"')

_SECTION = re.compile(r"^\s*\[([^\]]*)\]\s*(?:[;#].*)?$")
_KEYVAL = re.compile(r"^\s*([^=;#\[\]][^=]*?)\s*=\s*(.*?)\s*$")


class Ini:
    """Line-preserving INI document: edits add lines and never rewrite existing ones."""

    def __init__(self, data: bytes):
        self.bom = data.startswith(b"\xef\xbb\xbf")
        raw = data[3:] if self.bom else data
        try:
            self.text, self.enc = raw.decode("utf-8"), "utf-8"
        except UnicodeDecodeError:
            self.text, self.enc = raw.decode("latin-1"), "latin-1"
        self.eol = "\r\n" if "\r\n" in self.text else "\n"
        self.lines = self.text.replace("\r\n", "\n").split("\n")
        self.changed = False

    def _scan(self):
        """Yield (line_index, section_lower, key_lower, value) for every key line."""
        sec = ""
        for i, line in enumerate(self.lines):
            m = _SECTION.match(line)
            if m:
                sec = m.group(1).strip().lower()
                continue
            m = _KEYVAL.match(line)
            if m:
                yield i, sec, m.group(1).strip().lower(), m.group(2)

    def get(self, section, key):
        s, k = section.lower(), key.lower()
        for _, sec, key_, val in self._scan():
            if sec == s and key_ == k:
                return val
        return None

    def has_section(self, section):
        s = section.lower()
        return any(_SECTION.match(l) and _SECTION.match(l).group(1).strip().lower() == s for l in self.lines)

    def add(self, section, key, value):
        """Add key=value to the section when the key is absent. Returns True when a line was added."""
        if self.get(section, key) is not None:
            return False
        s = section.lower()
        last = None
        in_sec = False
        for i, line in enumerate(self.lines):
            m = _SECTION.match(line)
            if m:
                in_sec = m.group(1).strip().lower() == s
                if in_sec:
                    last = i
                continue
            if in_sec and _KEYVAL.match(line):
                last = i
        new = f"{key}={value}"
        if last is None:
            while self.lines and self.lines[-1] == "":
                self.lines.pop()
            self.lines += ["", f"[{section}]", new, ""]
        else:
            self.lines.insert(last + 1, new)
        self.changed = True
        return True

    def to_bytes(self):
        out = self.eol.join(self.lines).encode(self.enc)
        return (b"\xef\xbb\xbf" + out) if self.bom else out


def _derive(ini, pairs, forward=True):
    """Copy values between the two layouts of `pairs`; forward = left -> right."""
    for left, right in pairs:
        src, dst = (left, right) if forward else (right, left)
        val = ini.get(*src)
        if val is not None:
            ini.add(dst[0], dst[1], val)


def convert(data: bytes, source: str, target: str, name: str = "") -> bytes:
    """Return descriptor bytes for `target`. Unchanged input comes back as the same bytes object.

    source: 'futa' | 'spouse' | 'wife'
    target: 'wife' (ModRoom) | 'v15_spouse' | 'v15_futa'
    name:   display name added as [info] name for v1.5 when the file has none
    """
    ini = Ini(data)
    if target == "wife" and source == "spouse":
        _derive(ini, _POSE_MAP, forward=True)
    elif target == "v15_spouse":
        if source == "wife":
            _derive(ini, _POSE_MAP, forward=False)
        _derive(ini, _V15_MAP, forward=True)
        if source == "spouse":
            _dt_to_v15(ini)
    if target.startswith("v15") and name and ini.get("info", "name") is None:
        ini.add("info", "name", '"' + name.replace('"', "'") + '"')
    return ini.to_bytes() if ini.changed else data


_DESC = {"custom_data.futa": "futa", "custom_data.spouse": "spouse", "custom_data.wife": "wife"}


# --------------------------------------------------------------------------- Deeproom X-ray origins
# Measured 2026-11-17 over the Deeproom 4.0.3 library with robust boxes (rows/columns with >= 3 opaque
# pixels; stray pixels ignored), using frame 0 of each X-ray strip.
#   * Horizontally the X-ray centre lines up with the centre of the pack's OWN mating-press sprite
#     (partner: frame 0; lover: frame 7): median 0.0 / +0.5 px, p10..p90 within 0.5 px.
#   * Vertically the bottom edge of the partner X-ray sits +70 px below the origin (p10..p90 70..72); relative
#     to the bottom of the partner sprite it is +27 px. For lovers the vertical sprite reference is unreliable
#     (pose and length vary), so lover heights are never changed.
# A correction is made only when the library measure AND the pack's own sprite agree that the X-ray is off,
# in the same direction (x: > 4 px, y: > 6 px). Packs whose sprite is shifted the same way are left alone.
XRAY_RULES = {
    "wife": {"abs_x": -1.0, "body_dx": 0.0, "abs_bottom": 70.0, "body_dy": 27.0, "fix_y": True, "body_frames": (0,)},
    "futa": {"abs_x": -0.5, "body_dx": 0.5, "abs_bottom": 76.0, "body_dy": None, "fix_y": False, "body_frames": (7,)},
}
XRAY_X_TOL, XRAY_Y_TOL = 4.0, 6.0
XRAY_FRAME_MAX = (110, 170)  # frame 0 wider/taller than this is not a plain X-ray overlay; left alone
XRAY_ORIGIN_REPORT = []      # (pack folder, old offset, new offset) of the last Deeproom build, for the log


_OPAQUE = bytes(0 if a <= 16 else 1 for a in range(256))  # alpha -> 0/1


def _load_rgba(path):
    """(width, height, rows of RGBA bytes). Pillow when installed (fast), else the standard-library
    reader in wbconv (the patcher's launcher Python usually has no Pillow)."""
    try:
        from PIL import Image
        img = Image.open(path).convert("RGBA")
        w, h = img.size
        data = img.tobytes()
        return w, h, [data[y * w * 4:(y + 1) * w * 4] for y in range(h)]
    except ImportError:
        from wbp import wbconv
        img = wbconv.read_png(path)
        return img.width, img.height, [bytes(r) for r in img.rows]


def _robust_box(img, frame, frame_w, min_run=3):
    """{'cx', 'top', 'bottom', 'w', 'h'} of one frame of a strip from _load_rgba(), ignoring rows/columns
    with fewer than min_run opaque pixels (stray pixels), or None. cx is weighted by opaque pixels per column."""
    width, height, rows_rgba = img
    x0 = int(frame * frame_w)
    x1 = min(width, int(x0 + frame_w))
    w = x1 - x0
    rows, cols = [], [0] * w
    for row in rows_rgba:
        mask = row[x0 * 4 + 3:x1 * 4:4].translate(_OPAQUE)
        rows.append(mask.count(1))
        start = mask.find(1)
        while start != -1:
            cols[start] += 1
            start = mask.find(1, start + 1)
    xs = [x for x, c in enumerate(cols) if c >= min_run]
    ys = [y for y, c in enumerate(rows) if c >= min_run]
    if not xs or not ys:
        return None
    total = sum(cols[x] for x in xs)
    return {"cx": sum(x * cols[x] for x in xs) / total, "top": ys[0], "bottom": ys[-1] + 1,
            "w": xs[-1] + 1 - xs[0], "h": ys[-1] + 1 - ys[0]}


def _ini_num(ini, section, key, default):
    try:
        return float(str(ini.get(section, key)).strip().strip('"').strip("'"))
    except (TypeError, ValueError):
        return default


def _bundle_xray_offset(ini, frame_w):
    """The offset the Deeproom bundle uses for a partner X-ray without a measured origin."""
    ox = _ini_num(ini, "xray", "origin_x", _ini_num(ini, "sprite", "xray_x", 80.0))
    oy = _ini_num(ini, "xray", "origin_y", _ini_num(ini, "sprite", "xray_y", 84.0))
    ox = 80.0 if ox > 120 or ox < 40 else ox
    oy = 84.0 if oy > 120 or oy < 40 else oy
    if int(frame_w) != 160:  # Draw_0 resets non-160 px strips every frame
        return 80 * frame_w / 160, 84 * frame_w / 160
    return ox, oy


def _bundle_lover_xray_offset(ini, frame_w, legacy):
    """The offset the Deeproom bundle uses for a lover X-ray without a measured origin."""
    oy = 84.0
    if not legacy:
        off = _ini_num(ini, "sprite", "xray_offset_y", 0.0)
        oy = 84 - off if off > 0 else 84 + off
    return 80 * frame_w / 160, oy * frame_w / 160


def _body_reference(kind, ents, legacy, ini):
    """(body strip path, frame width fn, origin) of the pack's mating press, as the bundle loads it."""
    sox, soy = _ini_num(ini, "sprite", "origin_x", 80.0), _ini_num(ini, "sprite", "origin_y", 84.0)
    if kind == "wife":
        if legacy:
            ent = ents.get("custom_mating_press.png")
            return ent, (lambda w: w / 4), (_ini_num(ini, "mating_press", "origin_x", sox), _ini_num(ini, "mating_press", "origin_y", soy))
        ent = ents.get("custom_wife_mating_press_0.png")
        return ent, (lambda w: w / 5), (_ini_num(ini, "sprite", "mating_press_origin_x", _ini_num(ini, "mating_press", "origin_x", sox)),
                                       _ini_num(ini, "sprite", "mating_press_origin_y", _ini_num(ini, "mating_press", "origin_y", soy)))
    if legacy:
        ent = ents.get("custom_mating_press.png")
        return ent, (lambda w: w / max(1, round(w / (sox * 2 if sox > 0 else 160)))), (sox, soy)
    ent = ents.get("custom_futa_mating_press_0.png")
    return ent, (lambda w: w / 24), (_ini_num(ini, "sprite", "mating_press_origin_x", sox), _ini_num(ini, "sprite", "mating_press_origin_y", soy))


def _deeproom_xray_origins(assets):
    """Deeproom builds: add [xray] mobile_origin_x/y to descriptors whose X-ray does not line up with the pack's own sprite,
    measured from the strips the bundle will load (see XRAY_RULES). The pack's own files are not changed;
    only the copy written into the APK gets the two extra keys, which the bundle's loaders use as-is.
    Uses Pillow when installed, otherwise the standard-library PNG reader (slower)."""
    XRAY_ORIGIN_REPORT.clear()
    folders = {}
    for idx, (src, apk) in enumerate(assets):
        a = apk.replace("\\", "/")
        kind = "wife" if "/custom_wives/" in a else "futa" if "/custom_futas/" in a else None
        if kind:
            folders.setdefault((kind, a.rsplit("/", 1)[0]), {})[a.rsplit("/", 1)[-1].lower()] = (idx, Path(src), apk)
    drop, generated = set(), {}
    from wbp.common import print_progress
    for n_done, ((kind, folder), ents) in enumerate(folders.items(), 1):
        print_progress(n_done, len(folders), prefix="Aligning X-ray overlays")
        rule = XRAY_RULES[kind]
        if kind == "wife":
            descs = [ents[n] for n in ("custom_data.spouse", "custom_data.wife") if n in ents]
            if not descs or "custom_data.futa" in ents:
                continue
            legacy = "custom_data.spouse" in ents or "custom_mating_press.png" in ents or "custom_wife_mating_press_0.png" not in ents
            xray = ents.get("custom_xray.png" if legacy else "custom_wife_xray_0.png")
            frames_for = (lambda w: 4) if legacy else (lambda w: max(1, min(w // 160, 8)) if w >= 160 and w % 160 == 0 else 3)
        else:
            descs = [ents["custom_data.futa"]] if "custom_data.futa" in ents else []
            if not descs:
                continue
            legacy = "custom_mating_press.png" in ents or "custom_futa_mating_press_0.png" not in ents
            xray = ents.get("custom_xray.png" if legacy else "custom_futa_xray_0.png")
            frames_for = (lambda w: 3) if legacy else (lambda w: 18)
        if not xray:
            continue
        try:
            ximg = _load_rgba(xray[1])
        except Exception:
            continue
        xfw = ximg[0] / frames_for(ximg[0])
        xbox = _robust_box(ximg, 0, xfw)
        if not xbox or xbox["w"] > XRAY_FRAME_MAX[0] or xbox["h"] > XRAY_FRAME_MAX[1]:
            continue
        ini = Ini(descs[0][1].read_bytes())
        cur = _bundle_xray_offset(ini, xfw) if kind == "wife" else _bundle_lover_xray_offset(ini, xfw, legacy)
        abs_dx = (xbox["cx"] - cur[0]) - rule["abs_x"]
        abs_dy = (xbox["bottom"] - cur[1]) - rule["abs_bottom"]
        want_x = abs(abs_dx) > XRAY_X_TOL
        want_y = rule["fix_y"] and abs(abs_dy) > XRAY_Y_TOL
        if not (want_x or want_y):
            continue  # most packs: no need to open the body strip
        body_ent, body_fw, (mox, moy) = _body_reference(kind, ents, legacy, ini)
        if not body_ent:
            continue
        try:
            bimg = _load_rgba(body_ent[1])
        except Exception:
            continue
        bfw = body_fw(bimg[0])
        frame = rule["body_frames"][0]
        if (frame + 1) * bfw > bimg[0] + 1:
            continue
        bbox = _robust_box(bimg, frame, bfw)
        if not bbox:
            continue
        body_dx = (xbox["cx"] - cur[0]) - (bbox["cx"] - mox) - rule["body_dx"]
        new = [cur[0], cur[1]]
        if want_x and abs(body_dx) > XRAY_X_TOL and (body_dx > 0) == (abs_dx > 0):
            new[0] = cur[0] + body_dx
        if want_y:
            body_dy = (xbox["bottom"] - cur[1]) - (bbox["bottom"] - moy) - rule["body_dy"]
            if abs(body_dy) > XRAY_Y_TOL and (body_dy > 0) == (abs_dy > 0):
                new[1] = xbox["bottom"] - rule["abs_bottom"]
        if new == [cur[0], cur[1]]:
            continue
        new = (round(new[0], 1), round(new[1], 1))
        for idx, src, apk in descs:
            dini = Ini(src.read_bytes())
            if dini.get("xray", "mobile_origin_x") is not None:
                continue  # the author already set one
            dini.add("xray", "mobile_origin_x", f"{new[0]:g}")
            dini.add("xray", "mobile_origin_y", f"{new[1]:g}")
            drop.add(idx)
            generated[apk] = dini.to_bytes()
        XRAY_ORIGIN_REPORT.append((str(descs[0][1].parent), tuple(round(v, 1) for v in cur), new))
    if not drop:
        return assets, generated
    return [a for i, a in enumerate(assets) if i not in drop], generated


def convert_descriptors(assets, target_arch, xray_origins=True):
    """Post-process the asset list from gather_custom_assets().

    Returns (assets, generated): `assets` without the descriptors that were replaced and `generated`
    a dict apk_path -> bytes to write instead. Deeproom: partner and lover descriptors get a measured X-ray
    origin where the X-ray would not line up with the character sprite (see _deeproom_xray_origins); nothing else changes.
    """
    if target_arch == "deeproom":
        if not xray_origins:
            XRAY_ORIGIN_REPORT.clear()
            return assets, {}
        return _deeproom_xray_origins(assets)
    if target_arch not in ("modroom33", "v15"):
        return assets, {}
    dirs = {}
    for idx, (src, apk) in enumerate(assets):
        base = apk.rsplit("/", 1)[-1].lower()
        if base in _DESC:
            dirs.setdefault(apk.rsplit("/", 1)[0], {})[base] = (idx, Path(src), apk)
    drop, generated = set(), {}
    for folder, ents in dirs.items():
        if "custom_data.futa" in ents and ("custom_data.spouse" in ents or "custom_data.wife" in ents):
            continue  # hybrid pack: leave every file as it is
        name = ents[next(iter(ents))][1].parent.name
        read = lambda p: Path(p).read_bytes()
        if target_arch == "modroom33":
            if "custom_data.spouse" not in ents and "custom_data.wife" not in ents:
                continue
            real_wife = next((e for b, e in ents.items() if b == "custom_data.wife" and e[1].name.lower() == "custom_data.wife"), None)
            if real_wife:
                keep = real_wife
                data = None
            else:
                spouse = next(e for e in ents.values() if e[1].name.lower() == "custom_data.spouse")
                data = convert(read(spouse[1]), "spouse", "wife", name)
                keep = (None, spouse[1], folder + "/custom_data.wife")
            for e in ents.values():
                if e is not keep and e[2].rsplit("/", 1)[-1].lower() in ("custom_data.spouse", "custom_data.wife"):
                    drop.add(e[0])
            if data is not None:
                generated[folder + "/custom_data.wife"] = data
        else:  # v15
            if "custom_data.futa" in ents:
                idx, src, apk = ents["custom_data.futa"]
                raw = read(src)
                new = convert(raw, "futa", "v15_futa", name)
                if new is not raw:
                    drop.add(idx)
                    generated[apk] = new
            elif "custom_data.spouse" in ents:
                idx, src, apk = ents["custom_data.spouse"]
                raw = read(src)
                new = convert(raw, "spouse", "v15_spouse", name)
                if new is not raw:
                    drop.add(idx)
                    generated[apk] = new
            elif "custom_data.wife" in ents:
                idx, src, apk = ents["custom_data.wife"]
                drop.add(idx)
                generated[folder + "/custom_data.spouse"] = convert(read(src), "wife", "v15_spouse", name)
    return [a for i, a in enumerate(assets) if i not in drop], generated
