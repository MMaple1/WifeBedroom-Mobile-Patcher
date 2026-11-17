"""wbp.toy_native: the ToyBridge game-code patches, applied by the patcher itself.

These are the same insertions the ToyBridge launcher's GamePatcher.exe makes (a direct Intiface WebSocket
client, the UDP thrust broadcast, and the HMV beat-sync hooks), expressed as GML snippets in
core/gml_patches/native_toy/ plus the anchors below. The text edits are pure functions (patch_text) so they
can be tested without the game files; apply_native_toy() runs them through UndertaleModCli.

Anchors (identical in Deeproom, ModRoom and Wife's Bedroom v1.5): the single `thrust_time = 0;` line in
oFutaMatingPress Create_0, the single `thrust_prev = thrust;` line and the end of its Draw_0, the top of
Step_0, and the white colour arguments of oBackground Draw_0. When direct and HMV are both on, their Other_68
handlers are kept side by side (GamePatcher.exe kept only the one it wrote last).
"""
import subprocess
import tempfile
from pathlib import Path

from wbp.common import LOGGER, PATCH_MISSES, gml

NL = chr(10)
PRESS = "gml_Object_oFutaMatingPress_"
BACKGROUND_DRAW = "gml_Object_oBackground_Draw_0"
OTHER_68 = PRESS + "Other_68"
CREATE_ANCHOR = "thrust_time = 0;"
DRAW_ANCHOR = "thrust_prev = thrust;"
DRAW_END_ANCHOR = "mouse_y_prev = mouse_y;"
HMV_COLOR = "oFutaMatingPress.hmv_background_color"


def _snip(name):
    return gml("native_toy/" + name)


def _lines(snippet):
    return snippet[:-1].split("\n") if snippet.endswith("\n") else snippet.split("\n")


def _already(text, snippet):
    first = next((l.strip() for l in snippet.split("\n") if l.strip()), "")
    return bool(first) and first in text


def _insert_after_line(text, anchor, snippet, label):
    if _already(text, snippet):
        return text
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.strip() == anchor]
    if not hits:
        PATCH_MISSES.append(label)
        return text
    lines[hits[0] + 1:hits[0] + 1] = _lines(snippet)
    return "\n".join(lines)


def _prepend(text, snippet):
    return text if _already(text, snippet) else snippet + text


def _append(text, snippet):
    """Add the snippet at the end of the event's own code.

    Wife's Bedroom v1.5 ends Draw_0 with an enum block, so there the snippet goes after the last top-level
    `mouse_y_prev = mouse_y;`; elsewhere it goes after the last non-blank line."""
    if _already(text, snippet):
        return text
    lines = text.split(NL)
    tops = [i for i, l in enumerate(lines) if l.rstrip() == DRAW_END_ANCHOR]
    last = tops[-1] if tops else max((i for i, l in enumerate(lines) if l.strip()), default=-1)
    lines[last + 1:last + 1] = _lines(snippet)
    return NL.join(lines)


def hmv_background(text):
    """Tint the background with the beat colour: every white colour argument in oBackground Draw_0."""
    if HMV_COLOR in text:
        return text
    return text.replace("c_white", HMV_COLOR).replace("16777215", HMV_COLOR)


def patch_text(entry, text, features):
    """Return `text` of code entry `entry` with the snippets for `features` ({'direct', 'udp', 'hmv'}) applied."""
    if entry == PRESS + "Create_0":
        for feat in ("direct", "udp", "hmv"):
            if feat in features:
                text = _insert_after_line(text, CREATE_ANCHOR, _snip(feat + "_create"), f"toy_native:{feat}_create")
    elif entry == PRESS + "Draw_0":
        if "hmv" in features:  # first: a later insert at the same anchor lands in front of it, which keeps direct before hmv
            text = _append(text, _snip("hmv_draw_end"))
        if "direct" in features:
            text = _prepend(text, _snip("direct_draw_top"))
            text = _insert_after_line(text, DRAW_ANCHOR, _snip("direct_draw_thrust"), "toy_native:direct_draw_thrust")
            text = _append(text, _snip("direct_draw_end"))
        if "udp" in features:
            text = _insert_after_line(text, DRAW_ANCHOR, _snip("udp_draw"), "toy_native:udp_draw")
    elif entry == PRESS + "Step_0":
        if "hmv" in features:
            text = _prepend(text, _snip("hmv_step_top"))
    elif entry == BACKGROUND_DRAW:
        if "hmv" in features:
            text = hmv_background(text)
    return text


def other_68_text(features):
    """Async networking event: the direct client's reader, and/or the HMV listener."""
    parts = []
    if "direct" in features:
        parts.append(_snip("direct_other68"))
    if "hmv" in features:
        parts.append(_snip("hmv_other68"))
    return "".join(parts)


ENTRIES = [PRESS + "Create_0", PRESS + "Draw_0", PRESS + "Step_0", BACKGROUND_DRAW]

_ADD_EVENT_CSX = """using System;
using System.Linq;
using UndertaleModLib.Models;
EnsureDataLoaded();
var obj = Data.GameObjects.ByName("oFutaMatingPress");
obj.EventHandlerFor(EventType.Other, 68u, Data);
"""


def apply_native_toy(droid, utmt_cli, features, work_dir):
    """Apply the toy patches for `features` to the game data file `droid` in place. Returns True on success."""
    features = set(features)
    if not features:
        return True
    work = Path(work_dir) / "toy_native"
    work.mkdir(parents=True, exist_ok=True)
    droid = Path(droid)
    run = lambda args: subprocess.run([str(utmt_cli)] + args, capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")

    res = run(["dump", str(droid), "-o", str(work / "dump"), "-c", "UMT_DUMP_ALL"])
    code_dir = work / "dump" / "CodeEntries"
    if res.returncode != 0 or not code_dir.is_dir():
        LOGGER.log(f"Notice: toy patch skipped: could not dump the game code ({(res.stderr or res.stdout).strip()[-150:]})", prefix="[!]")
        return False

    # the Other_68 (async networking) event does not exist in the game: create it, then it can be replaced like any entry
    csx = work / "add_other_68.csx"
    csx.write_text(_ADD_EVENT_CSX, encoding="utf-8")
    with_event = work / "with_event.droid"
    res = run(["load", str(droid), "-s", str(csx), "-o", str(with_event), "-f"])
    if res.returncode != 0 or not with_event.exists():
        LOGGER.log(f"Notice: toy patch skipped: could not add the networking event ({(res.stderr or res.stdout).strip()[-150:]})", prefix="[!]")
        return False

    rep = ["replace", str(with_event)]
    changed = 0
    for entry in ENTRIES:
        f = code_dir / (entry + ".gml")
        if not f.exists():
            if entry != BACKGROUND_DRAW or "hmv" in features:
                PATCH_MISSES.append(f"toy_native:{entry} not found")
            continue
        old = f.read_bytes().decode("utf-8")
        new = patch_text(entry, old, features)
        if new != old:
            f.write_bytes(new.encode("utf-8"))
            rep += ["-c", f"{entry}={f}"]
            changed += 1
    o68 = work / (OTHER_68 + ".gml")
    o68.write_bytes(other_68_text(features).encode("utf-8"))
    rep += ["-c", f"{OTHER_68}={o68}", "-o", str(droid)]
    res = run(rep)
    if res.returncode != 0:
        LOGGER.log(f"Notice: toy patch failed while writing the game code ({(res.stderr or res.stdout).strip()[-150:]})", prefix="[!]")
        return False
    LOGGER.log(f"Toy patches applied natively ({', '.join(sorted(features))}): {changed} code entries edited, networking event added.", prefix="[+]")
    return True
