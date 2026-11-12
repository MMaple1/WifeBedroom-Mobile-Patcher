#!/usr/bin/env python3
"""
WB_Mobile_Patcher.py - Universal Mobile Touch Overlay Patcher & APK Builder for GameMaker

Comprehensive Engineering & Enhancement Catalog:
-----------------------------------------------------------------------------
[A] TOYBRIDGE FOUNDATION ENHANCEMENTS (Originated from ToyBridge 1.5.2)
-----------------------------------------------------------------------------
1. [TB-01] Synthetic Right-Click & Touch Hold Logic:
   - Evaluates touch coordinates and touch hold timer (mob_lp_timer) to synthesize
     desktop right-click inputs, enabling all interaction mechanics on touchscreen.
2. [TB-02] Dual-Column Vertical Menu Layout:
   - Partitions long desktop single-column dropdowns into touch-friendly dual columns.
3. [TB-03] Drag-to-Scroll Accumulator (menu_scroll_update):
   - Replaces desktop mouse-wheel scrolling with momentum touch-drag scrolling.
4. [TB-04] SIZES Options Page Hyper-Scale Toggle (TouchHyperToggle):
   - Adds [HYPER: ON/OFF] toggle on options page 2, expanding slider limits by 2.5x (up to 4.25).
5. [TB-05] On-Device Mod Sharing Activity (wbmods.PhoneImportActivity):
   - Native Android activity handling VIEW and SEND intent-filters for .zip and .json mods,
     copying incoming archives to app-private storage (files/phone_inbox/).
6. [TB-06] Optional External Toy Telemetry Broadcast (buttplug_socket):
   - Broadcasts real-time thrust, speed, and orgasm packets over UDP port 45735 to Intiface Central.

-----------------------------------------------------------------------------
[B] DEEPROOM MOBILE ARCHITECTURAL ENHANCEMENTS (Custom Engine Architecture)
-----------------------------------------------------------------------------
7. [DR-01] Native Text Stream Manifest Scanning (_manifest.txt):
   - Replaces blocking synchronous filesystem loops (file_find_*) with pre-indexed
     text manifests, eliminating Android ANR (Application Not Responding) startup freezes.
8. [DR-02] Universal Origin-Based Model Scaling & Slicing:
   - Dynamically calculates frame bounds using author's origin_x:
     Frame Width = origin_x * 2 | Frame Count = round(Sheet Width / Frame Width)
     Scale Factor = 160 / Frame Width.
   - Standardizes non-standard sizes (160px, 200px, 224px, 308px, 410px) to 160px baseline.
9. [DR-03] Lover-Wife Portrait Fallback Parity Architecture:
   - Refactors Lover's portrait rendering pipeline (_lover_base_portrait) to match Wife's
     fallback parity (defaults to sFutaPortrait1 if custom art is uninitialized).
10. [DR-04] Non-Negative Sprite Shield & Fallback Logic:
    - Injects safety guards before all draw_sprite_ext calls for c_sprite, dt_c_sprite,
      and legacy_xray_sprite, guaranteeing non-negative sprite IDs (cures requested -1 crash).
11. [DR-05] Custom Wife X-Ray Coordinate Initialization:
    - Explicitly initializes xray_origin_x = 80 and xray_origin_y = 84 in func_load_custom_spouse,
      preventing runner exceptions when loading custom wives missing custom_data.spouse.
12. [DR-06] Character Selection Grid with Auto-Scroll (CSS Jump-to-Selected):
    - Visual 6x2 character thumbnail grid with automatic scroll offset calculation that
      centers directly on the currently equipped partner when the menu opens.
13. [DR-07] Geometric Vector Star Badges & Favorites Filtering:
    - Pure vector rendering (draw_rectangle / draw_line_width) for star badges with
      isolated 28x28px touch hitboxes, eliminating raster font Unicode rendering errors.
    - Persistent ds_map favorites system with prioritized [FAV: ALL/ON] filter toggle.
14. [DR-08] Virtual Keyboard & Search Bar Integration:
    - On-screen touch keyboard invocation (keyboard_virtual_show) and real-time name filtering.
15. [DR-09] Mutual Panel Exclusivity & Radar Chart Containment:
    - Enforces mutual exclusivity between NEW LOVER and NEW WIFE floating menus.
    - Binds stat radar charts strictly to open panels (portrait_number == 0 or 1).
16. [DR-10] Climax Screen Protection & Panel Auto-Closing:
    - When Lover climax triggers (via [N] key or gameplay), both floating panels and stat
      graphs automatically force-close, and switch buttons are hidden until climax ends.
17. [DR-11] Translucent Mobile Overlay with Strict Modal Z-Ordering:
    - Floating Action Button (FAB) and drawer styled with subtle 0.12 idle / 0.40 active opacity.
    - Strictly suppressed when Character Selection Screen is open (stays behind modal layer).
18. [DR-12] Single-Trigger Overlay Action Bar:
    - Cleaned duplicate quick-bar loops so actions ([R], [N], [C], [O]) trigger exactly once per tap.
19. [DR-13] Uninterrupted 8-Mechanic Gameplay:
    - All 8 gameplay interactions (thrusting, grabbing, pumping, slapping, buckets, kissing,
      boobs, headpats) remain active while UI menus are open; startup disclaimer shows once.
20. [DR-14] Dialogue Pack Precedence Hierarchy:
    - Inverts dialogue loading order so custom dialogue_packs/ override internal character text.
21. [DR-15] Persistent Sandboxed Storage Redirection:
    - Redirects runtime save and INI writes directly to app-private storage (setting_data.sav,
      favorites.ini), bypassing GameMaker Android working_directory path resolution bugs.
22. [DR-16] Pure Python Binary AXML Editor:
    - Parses and modifies Android binary XML chunks in-place, registering PhoneImportActivity
      and bundling phone_import.dex without external Android SDK/build-tools.
23. [DR-17] Cryptographic Alignment & Multi-Scheme Signing:
    - Zipaligns and signs APKs using v1 (JAR), v2 (APK Signature Scheme v2), and v3 schemes.
24. [DR-18] Isolated Directory Architecture & Auto-Quarantine:
    - Dedicated input/ folder for game assets, core/ for tools/keys, and output/ for signed APKs.
    - Incompatible or corrupted character packs are automatically isolated to output/quarantine/.
"""

import sys
sys.dont_write_bytecode = True
import os
import re
import zlib
import struct
import glob
import json
import shutil
import io
from pathlib import Path

def extract_pack_display_name(pack_path: Path) -> str:
    """
    Reads [info] name="..." from .futa, .spouse, .bedroom, or .txt INI files.
    Allows numeric Steam Workshop IDs (e.g. 3821177370) to automatically display
    their real character names (e.g. Ankha, Pomni, Miku) in the Character Selection Grid.
    """
    for df_name in ["custom_data.futa", "custom_data.spouse", "custom_data.bedroom", "custom_data.txt"]:
        df = pack_path / df_name
        if df.is_file():
            try:
                content = df.read_text(encoding="utf-8", errors="ignore")
                m = re.search(r'name\s*=\s*["\']?([^"\'\r\n]+)["\']?', content, re.IGNORECASE)
                if m:
                    cand = m.group(1).strip()
                    if cand:
                        return cand
            except Exception:
                pass
    return pack_path.name

def detect_mod_engine_version(folder: Path) -> str:
    """
    Detects whether a mod folder is designed for Wife's Bedroom v1.5 or Deeproom 4.0 / v1.4.
    Evaluates folder nomenclature, unified custom/ structure, and data.win binary characteristics.
    Returns '1.5' or '1.4'.
    """
    if not folder or not folder.is_dir():
        return "1.4"
    f_lower = folder.name.lower()
    if "1_5" in f_lower or "1.5" in f_lower or "v15" in f_lower:
        return "1.5"
    if (folder / "custom").is_dir() and not (folder / "custom_futas").is_dir() and not (folder / "custom_wives").is_dir():
        return "1.5"
    dwin = folder / "data.win"
    if dwin.is_file():
        if dwin.stat().st_size < 40 * 1024 * 1024:
            return "1.5"
    return "1.4"

def find_matching_base_apk(input_dir: Path, patcher_dir: Path, target_version: str = "1.4") -> Path:
    """
    Finds the optimal base APK matching the target engine version (1.4 vs 1.5).
    Guarantees native runner parity between libyoyo.so and game.droid bytecode.
    """
    if target_version == "1.5":
        v15_candidates = [
            input_dir / "wifes_bedroom1_5.apk",
            input_dir / "wifes_bedroom_1_5.apk",
            input_dir / "base_1_5.apk",
            input_dir / "wifes_bedroom_v1_5.apk",
            patcher_dir / "wifes_bedroom1_5.apk",
            patcher_dir / "wifes_bedroom_1_5.apk",
            patcher_dir / "input" / "wifes_bedroom1_5.apk",
            patcher_dir / "input" / "wifes_bedroom_1_5.apk"
        ]
        for c in v15_candidates:
            if c.is_file():
                return c.resolve()

    # 1.4 / Deeproom 4.0 candidates (or general fallback)
    v14_candidates = [
        input_dir / "wifes_bedroom1_4.apk",
        input_dir / "wifes_bedroom_1_4.apk",
        input_dir / "base.apk",
        input_dir / "wifes_bedroom.apk",
        patcher_dir / "input" / "wifes_bedroom1_4.apk",
        patcher_dir / "input" / "wifes_bedroom_1_4.apk",
        patcher_dir / "input" / "wifes_bedroom.apk",
        patcher_dir / "input" / "base.apk",
        patcher_dir / "base.apk",
        patcher_dir / "wifes_bedroom.apk"
    ]
    for c in v14_candidates:
        if c.is_file():
            return c.resolve()

    # Any .apk in input_dir
    if input_dir.is_dir():
        for f in input_dir.iterdir():
            if f.is_file() and f.suffix.lower() == ".apk":
                return f.resolve()

    return None

def clean_output_dir(output_dir, preserve_file=None):
    """Cleans older builds and signature files from output/ directory."""
    removed = 0
    preserve_resolved = Path(preserve_file).resolve() if preserve_file else None
    for p in output_dir.glob("*"):
        if p.is_file() and p.suffix.lower() in [".apk", ".idsig", ".bak"]:
            if preserve_resolved and p.resolve() == preserve_resolved:
                continue
            try:
                p.unlink(missing_ok=True)
                removed += 1
            except Exception:
                pass
    if removed > 0:
        LOGGER.log(f"Cleaned {removed} previous build file(s) from output/.", prefix="[+]")

class AxmlEditor:
    """Pure-Python binary Android XML editor ported from ToyBridge 1.5.2 AxmlEditor.cs.
    Registers wbmods.PhoneImportActivity with VIEW and SEND intent-filters for .zip and .json mods."""
    IMPORT_ACTIVITY_CLASS = "wbmods.PhoneImportActivity"
    CHUNK_STRING_POOL = 0x0001
    CHUNK_RESOURCE_MAP = 0x0180
    CHUNK_START_ELEMENT = 0x0102
    CHUNK_END_ELEMENT = 0x0103
    NO_INDEX = 0xFFFFFFFF
    ANDROID_NS = "http://schemas.android.com/apk/res/android"
    ATTR_THEME = 0x01010000
    ATTR_LABEL = 0x01010001
    ATTR_NAME = 0x01010003
    ATTR_EXPORTED = 0x01010010
    ATTR_MIME_TYPE = 0x01010026
    THEME_NO_DISPLAY = 0x01030055
    TYPE_REFERENCE = 0x01
    TYPE_STRING = 0x03
    TYPE_BOOLEAN = 0x12
    MIME_TYPES = ["application/zip", "application/x-zip-compressed", "application/json", "application/octet-stream"]

    @staticmethod
    def read_u16(data, at):
        return struct.unpack("<H", data[at:at+2])[0]

    @staticmethod
    def read_u32(data, at):
        return struct.unpack("<I", data[at:at+4])[0]

    @staticmethod
    def read_strings(data):
        if len(data) < 16 or AxmlEditor.read_u16(data, 0) != 0x0003:
            raise ValueError("not a binary XML file")
        pool_start = AxmlEditor.read_u16(data, 2)
        if AxmlEditor.read_u16(data, pool_start) != AxmlEditor.CHUNK_STRING_POOL:
            raise ValueError("string pool not where expected")
        pool_size = AxmlEditor.read_u32(data, pool_start + 4)
        count = AxmlEditor.read_u32(data, pool_start + 8)
        if AxmlEditor.read_u32(data, pool_start + 12) != 0:
            raise ValueError("styled string pool not supported")
        utf8 = (AxmlEditor.read_u32(data, pool_start + 16) & 0x100) != 0
        strings_start = pool_start + AxmlEditor.read_u32(data, pool_start + 20)

        strings = []
        for i in range(count):
            at = strings_start + AxmlEditor.read_u32(data, pool_start + 28 + (i * 4))
            if utf8:
                at += 2 if (data[at] & 0x80) != 0 else 1
                b = data[at]
                at += 1
                if (b & 0x80) != 0:
                    b = ((b & 0x7F) << 8) | data[at]
                    at += 1
                s = data[at:at+b].decode("utf-8", errors="ignore")
                strings.append(s)
            else:
                chars = AxmlEditor.read_u16(data, at)
                at += 2
                if (chars & 0x8000) != 0:
                    chars = ((chars & 0x7FFF) << 16) | AxmlEditor.read_u16(data, at)
                    at += 2
                s = data[at:at+chars*2].decode("utf-16le", errors="ignore")
                strings.append(s)
        return strings, pool_start, pool_size, utf8

    @staticmethod
    def write_utf8_length(stream, length):
        if length > 0x7F:
            stream.write(bytes([0x80 | (length >> 8)]))
        stream.write(bytes([length & 0xFF]))

    @staticmethod
    def write_string_pool(strings, utf8):
        body = io.BytesIO()
        offsets = []
        for s in strings:
            offsets.append(body.tell())
            if utf8:
                b = s.encode("utf-8")
                AxmlEditor.write_utf8_length(body, len(s))
                AxmlEditor.write_utf8_length(body, len(b))
                body.write(b)
                body.write(b"\x00")
            else:
                if len(s) >= 0x8000:
                    body.write(struct.pack("<H", 0x8000 | (len(s) >> 16)))
                body.write(struct.pack("<H", len(s) & 0xFFFF))
                body.write(s.encode("utf-16le"))
                body.write(b"\x00\x00")
        while body.tell() % 4 != 0:
            body.write(b"\x00")

        header_and_offsets = 28 + (len(strings) * 4)
        pool = io.BytesIO()
        pool.write(struct.pack("<H", AxmlEditor.CHUNK_STRING_POOL))
        pool.write(struct.pack("<H", 28))
        pool.write(struct.pack("<I", header_and_offsets + body.tell()))
        pool.write(struct.pack("<I", len(strings)))
        pool.write(struct.pack("<I", 0))
        pool.write(struct.pack("<I", 0x100 if utf8 else 0))
        pool.write(struct.pack("<I", header_and_offsets))
        pool.write(struct.pack("<I", 0))
        for off in offsets:
            pool.write(struct.pack("<I", off))
        pool.write(body.getvalue())
        return pool.getvalue()

    @staticmethod
    def has_import_activity(manifest_bytes):
        try:
            strings, _, _, _ = AxmlEditor.read_strings(manifest_bytes)
            return AxmlEditor.IMPORT_ACTIVITY_CLASS in strings
        except Exception:
            return False

    @staticmethod
    def add_import_activity(manifest):
        if AxmlEditor.has_import_activity(manifest):
            return manifest

        strings, pool_start, pool_size, utf8 = AxmlEditor.read_strings(manifest)
        map_start = pool_start + pool_size
        if AxmlEditor.read_u16(manifest, map_start) != AxmlEditor.CHUNK_RESOURCE_MAP:
            raise ValueError("resource map not where expected")
        map_size = AxmlEditor.read_u32(manifest, map_start + 4)
        resource_ids = []
        for i in range(map_start + 8, map_start + map_size, 4):
            resource_ids.append(AxmlEditor.read_u32(manifest, i))

        def str_idx(val):
            if val in strings:
                return strings.index(val)
            strings.append(val)
            return len(strings) - 1

        def attr_idx(name, res_id):
            if res_id in resource_ids:
                return resource_ids.index(res_id)
            strings.append(name)
            idx = len(strings) - 1
            while len(resource_ids) < idx:
                resource_ids.append(0)
            resource_ids.append(res_id)
            return idx

        nodes_start = map_start + map_size
        application_end = -1
        label = None
        application_name = strings.index("application") if "application" in strings else -1

        pos = nodes_start
        while pos + 8 <= len(manifest):
            chunk_type = AxmlEditor.read_u16(manifest, pos)
            chunk_size = AxmlEditor.read_u32(manifest, pos + 4)
            if chunk_size < 8:
                break
            if chunk_type == AxmlEditor.CHUNK_START_ELEMENT and AxmlEditor.read_u32(manifest, pos + 20) == application_name:
                attr_count = AxmlEditor.read_u16(manifest, pos + 28)
                for a in range(attr_count):
                    at = pos + 36 + (a * 20)
                    name_idx = AxmlEditor.read_u32(manifest, at + 4)
                    if name_idx < len(resource_ids) and resource_ids[name_idx] == AxmlEditor.ATTR_LABEL:
                        label = (manifest[at + 15], AxmlEditor.read_u32(manifest, at + 16))
            elif chunk_type == AxmlEditor.CHUNK_END_ELEMENT and AxmlEditor.read_u32(manifest, pos + 20) == application_name:
                application_end = pos
            pos += chunk_size

        if application_name < 0 or application_end < 0:
            raise ValueError("no <application> element")

        ns = str_idx(AxmlEditor.ANDROID_NS)
        nodes = io.BytesIO()

        def start_elem(elem, attrs):
            nodes.write(struct.pack("<H", AxmlEditor.CHUNK_START_ELEMENT))
            nodes.write(struct.pack("<H", 16))
            nodes.write(struct.pack("<I", 36 + len(attrs) * 20))
            nodes.write(struct.pack("<I", 1))
            nodes.write(struct.pack("<I", AxmlEditor.NO_INDEX))
            nodes.write(struct.pack("<I", AxmlEditor.NO_INDEX))
            nodes.write(struct.pack("<I", str_idx(elem)))
            nodes.write(struct.pack("<H", 20))
            nodes.write(struct.pack("<H", 20))
            nodes.write(struct.pack("<H", len(attrs)))
            nodes.write(struct.pack("<HHH", 0, 0, 0))
            for name, raw, val_type, data in attrs:
                nodes.write(struct.pack("<I", ns))
                nodes.write(struct.pack("<I", name))
                nodes.write(struct.pack("<I", raw))
                nodes.write(struct.pack("<H", 8))
                nodes.write(struct.pack("<B", 0))
                nodes.write(struct.pack("<B", val_type))
                nodes.write(struct.pack("<I", data))

        def end_elem(elem):
            nodes.write(struct.pack("<H", AxmlEditor.CHUNK_END_ELEMENT))
            nodes.write(struct.pack("<H", 16))
            nodes.write(struct.pack("<I", 24))
            nodes.write(struct.pack("<I", 1))
            nodes.write(struct.pack("<I", AxmlEditor.NO_INDEX))
            nodes.write(struct.pack("<I", AxmlEditor.NO_INDEX))
            nodes.write(struct.pack("<I", str_idx(elem)))

        def str_attr(name, val):
            s_i = str_idx(val)
            return (name, s_i, AxmlEditor.TYPE_STRING, s_i)

        name_attr = attr_idx("name", AxmlEditor.ATTR_NAME)
        mime_attr = attr_idx("mimeType", AxmlEditor.ATTR_MIME_TYPE)

        activity_attrs = [
            (attr_idx("theme", AxmlEditor.ATTR_THEME), AxmlEditor.NO_INDEX, AxmlEditor.TYPE_REFERENCE, AxmlEditor.THEME_NO_DISPLAY),
        ]
        if label is not None:
            activity_attrs.append((attr_idx("label", AxmlEditor.ATTR_LABEL), AxmlEditor.NO_INDEX, label[0], label[1]))
        activity_attrs.append(str_attr(name_attr, AxmlEditor.IMPORT_ACTIVITY_CLASS))
        activity_attrs.append((attr_idx("exported", AxmlEditor.ATTR_EXPORTED), AxmlEditor.NO_INDEX, AxmlEditor.TYPE_BOOLEAN, 0xFFFFFFFF))

        start_elem("activity", activity_attrs)

        for action, extra_mimes in [
            ("android.intent.action.VIEW", []),
            ("android.intent.action.SEND", ["application/*"]),
            ("android.intent.action.SEND_MULTIPLE", ["application/*", "*/*"])
        ]:
            start_elem("intent-filter", [])
            start_elem("action", [str_attr(name_attr, action)])
            end_elem("action")
            start_elem("category", [str_attr(name_attr, "android.intent.category.DEFAULT")])
            end_elem("category")
            for mime in AxmlEditor.MIME_TYPES + extra_mimes:
                start_elem("data", [str_attr(mime_attr, mime)])
                end_elem("data")
            end_elem("intent-filter")

        end_elem("activity")

        pool = AxmlEditor.write_string_pool(strings, utf8)
        output = io.BytesIO()
        output.write(manifest[:8])
        output.write(pool)
        output.write(struct.pack("<H", AxmlEditor.CHUNK_RESOURCE_MAP))
        output.write(struct.pack("<H", 8))
        output.write(struct.pack("<I", 8 + (len(resource_ids) * 4)))
        for rid in resource_ids:
            output.write(struct.pack("<I", rid))
        output.write(manifest[nodes_start:application_end])
        output.write(nodes.getvalue())
        output.write(manifest[application_end:])

        result = bytearray(output.getvalue())
        struct.pack_into("<I", result, 4, len(result))
        return bytes(result)

import tempfile
import zipfile
import traceback
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# -----------------------------------------------------------------------------
# PROGRESS BAR FEEDBACK
# -----------------------------------------------------------------------------
def print_progress(current, total, prefix="Packaging APK", bar_length=30):
    percent = float(current) / max(1, total)
    arrow = "=" * max(0, int(round(percent * bar_length)) - 1) + ">" if percent > 0 else ""
    spaces = " " * (bar_length - len(arrow))
    sys.stdout.write(f"\r[*] {prefix}: [{arrow}{spaces}] {int(percent * 100)}% ({current}/{total})")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")

# -----------------------------------------------------------------------------
# LOGGING & ERROR REPORTING SYSTEM
# -----------------------------------------------------------------------------
class ExecutionLogger:
    def __init__(self):
        self.logs = []
        self.log_dir = Path(__file__).parent.resolve()

    def log(self, msg, prefix="[*]"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"{prefix} [{timestamp}] {msg}"
        print(formatted)
        self.logs.append(formatted)

    def error(self, msg):
        self.log(msg, prefix="[ERROR]")

    def progress(self, prefix, current, total):
        print_progress(current, total, prefix=prefix)

    def write_error_report(self, exc, stage="Unknown"):
        err_file = self.log_dir / "patch_overlay_latest_error.log"
        with open(err_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("           WB_Mobile_Patcher Failure Diagnosis\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Failed Stage: {stage}\n")
            f.write(f"Exception Type: {type(exc).__name__}\n")
            f.write(f"Exception Message: {str(exc)}\n\n")
            f.write("-" * 60 + "\n")
            f.write("Python Traceback:\n")
            f.write("-" * 60 + "\n")
            f.write(traceback.format_exc() + "\n\n")
            f.write("-" * 60 + "\n")
            f.write("Execution Log Trail:\n")
            f.write("-" * 60 + "\n")
            for line in self.logs:
                f.write(line + "\n")
        print(f"\n[!] A detailed diagnosis report was saved to: {err_file.name}")

LOGGER = ExecutionLogger()
# Auto-clean __pycache__ if created by any external tool
_PATCHER_DIR_REF = Path(__file__).parent.resolve()

def _clean_pycache():
    try:
        _pc = _PATCHER_DIR_REF / "__pycache__"
        if _pc.exists():
            shutil.rmtree(_pc, ignore_errors=True)
    except Exception:
        pass

_clean_pycache()
import atexit
atexit.register(_clean_pycache)


# -----------------------------------------------------------------------------
# TOOL & ENVIRONMENT RESOLUTION
# -----------------------------------------------------------------------------
def get_utmt_cli():
    env_cli = os.environ.get("UTMT_CLI")
    if env_cli and Path(env_cli).exists():
        return str(Path(env_cli).resolve())

    patcher_dir = Path(__file__).parent.resolve()
    core_dir = patcher_dir / "core"

    which_utmt = shutil.which("UndertaleModCli") or shutil.which("UndertaleModCli.exe")
    if which_utmt:
        return which_utmt

    candidates = [
        core_dir / "UndertaleModCli.exe",
        core_dir / "UndertaleModCli" / "UndertaleModCli.exe",
        core_dir / "UTMT_CLI" / "UndertaleModCli.exe",
        patcher_dir / "UndertaleModCli.exe",
        patcher_dir / "tools" / "UndertaleModCli.exe"
    ]
    for c in candidates:
        if c.exists():
            return str(c.resolve())

    which_utmt = shutil.which("UndertaleModCli")
    if which_utmt:
        return which_utmt

    raise FileNotFoundError("UndertaleModCli.exe not found. Please set UTMT_CLI environment variable.")

def get_jdk_tool(tool_name):
    jdk_dirs = [
        Path(r"C:\Program Files\Microsoft\jdk-11.0.16.101-hotspot\bin"),
        Path(r"C:\Program Files\Java\jdk-17\bin"),
        Path(r"C:\Program Files\Java\jdk-11\bin"),
        Path(r"C:\Program Files\Android\Android Studio\jbr\bin")
    ]
    for jd in jdk_dirs:
        p = jd / f"{tool_name}.exe"
        if p.exists():
            return str(p)
    found = shutil.which(tool_name)
    return found if found else tool_name

def find_uber_apk_signer():
    patcher_dir = Path(__file__).parent.resolve()
    core_dir = patcher_dir / "core"
    candidates = [
        core_dir / "uber-apk-signer.jar",
        patcher_dir / "uber-apk-signer.jar",
        patcher_dir / "tools" / "uber-apk-signer.jar"
    ]
    for c in candidates:
        if c.exists():
            return str(c.resolve())
    return None

# -----------------------------------------------------------------------------
# CUSTOM ASSET DISCOVERY & MANIFEST GENERATOR
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# TOYBRIDGE MODPACK CLASSIFICATION & QUARANTINE ROUTINES
# -----------------------------------------------------------------------------
_OLD_CONVENTION_DATA_PATTERN = re.compile(r'^custom_data_\d+\.(futa|spouse)$', re.IGNORECASE)
_OLD_CONVENTION_PATTERN = re.compile(r'^custom_(futa|wife)_\w+_\d+\.png$', re.IGNORECASE)

KNOWN_DATA_FILES = {
    'custom_data.futa': 'futa',
    'custom_data.wife': 'wife',
    'custom_data.spouse': 'wife',
    'custom_data.bedroom': 'bedroom',
}

def classify_custom_pack(folder: Path):
    """
    Classifies one character/bedroom folder as portable (simple convention - can just be
    copied into the other mod system's expected layout) or not (uses the older numbered
    convention or lacks recognized custom_data files, which causes crashes on mobile).
    Exact classification logic from ToyBridgeLauncher's GamePatcher / ToyLauncher.
    """
    try:
        entries = list(folder.iterdir())
    except OSError as e:
        return False, f"Couldn't read folder: {e}", None

    names = [e.name for e in entries]
    lower_to_orig = {e.name.lower(): e.name for e in entries}

    # 1. Check for numbered-alt data file (custom_data_1.futa style)
    for name in names:
        if _OLD_CONVENTION_DATA_PATTERN.match(name):
            return False, "Uses a numbered-alt data file (custom_data_1.futa style) - not portable.", None

    # 2. Check for recognized data file
    data_file = None
    kind = None
    for df, k in KNOWN_DATA_FILES.items():
        if df in lower_to_orig:
            data_file = lower_to_orig[df]
            kind = k
            break

    if not data_file:
        return False, "No recognized custom_data.futa/.wife/.spouse/.bedroom file found.", None

    # 3. Check for old numbered sprite convention (custom_futa_mating_press_0.png, etc.)
    old_style_files = [n for n in names if _OLD_CONVENTION_PATTERN.match(n)]
    if old_style_files:
        return False, f"Uses the older numbered sprite convention ({old_style_files[0]}, etc.) - not portable.", kind

    return True, "Simple convention - portable as-is.", kind

def quarantine_incompatible_packs(mods_dir: Path, quarantine_dir: Path):
    """
    Scans mods_dir for custom_futas, custom_wives, custom_bedrooms and moves any
    incompatible/failing packs to quarantine_dir preserving relative category structure.
    Returns (portable_count, quarantined_count, list_of_quarantined).
    """
    mods_dir = Path(mods_dir)
    quarantine_dir = Path(quarantine_dir)
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    portable = []
    quarantined = []

    target_cats = ["custom_futas", "custom_wives", "custom_bedrooms", "custom"]
    for cat in target_cats:
        cat_path = mods_dir / cat
        if not cat_path.is_dir():
            continue

        cat_quarantine = quarantine_dir / cat
        cat_quarantine.mkdir(parents=True, exist_ok=True)

        for pack in sorted(cat_path.iterdir()):
            if pack.is_dir() and not pack.name.startswith("."):
                is_p, reason, kind = classify_custom_pack(pack)
                if is_p:
                    portable.append((pack.name, cat))
                else:
                    dest = cat_quarantine / pack.name
                    if dest.exists():
                        shutil.rmtree(dest, ignore_errors=True)
                    shutil.move(str(pack), str(dest))
                    quarantined.append((pack.name, cat, reason))

    return len(portable), len(quarantined), quarantined

def sanitize_apk_part(name: str) -> str:
    """Sanitizes directory/file component for Android APK AssetManager compatibility (lowercase, underscores, no spaces, no illegal punctuation)."""
    clean = name.strip().lower().replace(" ", "_").replace("#", "").replace(":", "_").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace('"', '').replace("'", "")
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean or "unnamed"

def sanitize_apk_path(rel_path: Path) -> str:
    """Sanitizes full relative path for Android APK asset manager."""
    parts = [sanitize_apk_part(p) for p in rel_path.parts]
    return "/".join(parts)

def generate_manifest_data(folder, is_v15=False):
    """
    Generates in-memory _manifest.txt files for every directory GameMaker scans
    on Android (custom_futas, custom_wives, custom_bedrooms, custom_music,
    custom_sounds, dialogue, dialogue_packs, texture_packs).
    Sanitizes all directory components and entries to lowercase with underscores,
    matching ToyBridge's exact Android AAssetManager specification.
    Returns dict: relative_apk_path -> bytes
    """
    manifests = {}
    folder = Path(folder).resolve()
    valid_exts = {".png", ".ogg", ".wav", ".mp3", ".json", ".futa", ".spouse", ".wife", ".bedroom", ".ini", ".txt", ".jpg", ".jpeg", ".gif", ".webp"}

    target_dirs = [
        "custom_futas", "custom_wives", "custom_bedrooms",
        "custom_music", "custom_sounds", "dialogue", "dialogue_packs", "texture_packs"
    ]

    # 1. First process all standard directories on disk
    for td_name in target_dirs:
        top_dir = folder / td_name
        if not top_dir.is_dir():
            continue

        for root, dirs, files in os.walk(top_dir):
            root_path = Path(root)
            rel_to_folder = root_path.relative_to(folder)

            clean_dirs = sorted([sanitize_apk_part(d) for d in dirs if not d.startswith(".") and d != "__pycache__"])
            clean_files = sorted([sanitize_apk_part(f) for f in files if Path(f).suffix.lower() in valid_exts and f != "_manifest.txt"])
            entries = clean_dirs + clean_files

            if entries:
                manifest_text = "\n".join(entries) + "\n"
                manifest_apk_path = f"assets/{sanitize_apk_path(rel_to_folder)}/_manifest.txt"
                manifests[manifest_apk_path] = manifest_text.encode("utf-8")

        top_dirs = sorted([sanitize_apk_part(item.name) for item in top_dir.iterdir() if item.is_dir() and not item.name.startswith(".")])
        top_files = sorted([sanitize_apk_part(item.name) for item in top_dir.iterdir() if item.is_file() and item.suffix.lower() in valid_exts and item.name != "_manifest.txt"])
        top_entries = top_dirs + top_files

        if top_entries:
            manifest_text = "\n".join(top_entries) + "\n"
            top_manifest_apk_path = f"assets/{td_name}/_manifest.txt"
            manifests[top_manifest_apk_path] = manifest_text.encode("utf-8")

    # 2. Process v1.5 custom/ packs and PREPEND them to the FRONT of manifests (Page 1 in CSS)
    custom_dir = folder / "custom"
    if custom_dir.is_dir():
        top_entries_v15 = {"custom_futas": [], "custom_wives": [], "custom_bedrooms": [], "custom": []}
        used_cat_names_m = {"custom_futas": set(), "custom_wives": set(), "custom_bedrooms": set()}
        for pack in sorted(custom_dir.iterdir()):
            if pack.is_dir() and not pack.name.startswith("."):
                cat = None
                if (pack / "custom_data.futa").exists():
                    cat = "custom_futas"
                elif (pack / "custom_data.spouse").exists():
                    cat = "custom_wives"
                elif (pack / "custom_data.bedroom").exists():
                    cat = "custom_bedrooms"

                # Extract real character name from INI for clean CSS display
                display_name = extract_pack_display_name(pack)
                clean_pname = sanitize_apk_part(display_name)
                if cat:
                    if clean_pname in used_cat_names_m[cat]:
                        clean_pname = f"{clean_pname}_{sanitize_apk_part(pack.name)}"
                    used_cat_names_m[cat].add(clean_pname)
                    top_entries_v15[cat].append(clean_pname)
                top_entries_v15["custom"].append(clean_pname)

                for root, dirs, files in os.walk(pack):
                    rel_to_pack = Path(root).relative_to(pack)
                    clean_sub = "/".join(sanitize_apk_part(p) for p in rel_to_pack.parts) if rel_to_pack.parts else ""

                    clean_dirs = sorted([sanitize_apk_part(d) for d in dirs if not d.startswith(".") and d != "__pycache__"])
                    clean_files = sorted([sanitize_apk_part(Path(f).stem) + Path(f).suffix.lower() for f in files if Path(f).suffix.lower() in valid_exts and f != "_manifest.txt" and not f.startswith(".") and not f.endswith("~")])
                    entries = clean_dirs + clean_files

                    if entries:
                        mtext = "\n".join(entries) + "\n"
                        if is_v15:
                            p_v15 = f"assets/custom/{clean_pname}/{clean_sub}/_manifest.txt" if clean_sub else f"assets/custom/{clean_pname}/_manifest.txt"
                            manifests[p_v15] = mtext.encode("utf-8")
                        elif cat:
                            p_cat = f"assets/{cat}/{clean_pname}/{clean_sub}/_manifest.txt" if clean_sub else f"assets/{cat}/{clean_pname}/_manifest.txt"
                            manifests[p_cat] = mtext.encode("utf-8")

        for cat_k, packs_v in top_entries_v15.items():
            if packs_v:
                if not is_v15 and cat_k == "custom":
                    continue
                if is_v15 and cat_k != "custom":
                    continue
                top_manifest_apk_path = f"assets/{cat_k}/_manifest.txt"
                existing = manifests.get(top_manifest_apk_path, b"").decode("utf-8").splitlines()
                merged = sorted(set(existing + list(packs_v)))
                manifests[top_manifest_apk_path] = ("\n".join(merged) + "\n").encode("utf-8")

    return manifests

def gather_custom_assets(folder, is_v15=False):
    """
    Finds all valid GameMaker custom asset files in custom_* directories, dialogue*, texture_packs, etc.
    Filters out raw art project files (.aseprite, .clip, .pdn, .kra, .zip, etc.) to prevent APK bloat and Android asset table crashes.
    Sanitizes all relative APK paths to lowercase with underscores to match ToyBridge's exact Android AssetManager convention.
    Returns list of (full_file_path, relative_apk_path).
    """
    valid_exts = {".png", ".ogg", ".wav", ".mp3", ".json", ".futa", ".spouse", ".wife", ".bedroom", ".ini", ".txt", ".jpg", ".jpeg", ".gif", ".webp"}
    folder = Path(folder).resolve()
    assets = []

    target_prefixes = ("custom_", "dialogue", "texture_packs", "templates")

    for root, dirs, files in os.walk(folder):
        rel_root = Path(root).relative_to(folder)
        root_parts = rel_root.parts
        if not root_parts:
            for file in files:
                if file.lower() == "options.ini":
                    fpath = Path(root) / file
                    assets.append((fpath, f"assets/{file.lower()}"))
            continue

        first_dir = root_parts[0].lower()
        if any(first_dir.startswith(pref) for pref in target_prefixes):
            for file in files:
                fpath = Path(root) / file
                if fpath.suffix.lower() in valid_exts and fpath.name.lower() != "data.win" and not fpath.name.startswith(".") and not fpath.name.endswith("~"):
                    rel_p = fpath.relative_to(folder)
                    apk_p = f"assets/{sanitize_apk_path(rel_p)}"
                    assets.append((fpath, apk_p))

    # Solution 1: Automatic routing of v1.5 custom/ packs into Deeproom 4.0 categories
    custom_dir = folder / "custom"
    if custom_dir.is_dir():
        used_cat_names = {"custom_futas": set(), "custom_wives": set(), "custom_bedrooms": set()}
        for pack in sorted(custom_dir.iterdir()):
            if pack.is_dir() and not pack.name.startswith("."):
                cat = None
                if (pack / "custom_data.futa").exists():
                    cat = "custom_futas"
                elif (pack / "custom_data.spouse").exists():
                    cat = "custom_wives"
                elif (pack / "custom_data.bedroom").exists():
                    cat = "custom_bedrooms"

                # Extract real character name from INI for clean CSS display
                display_name = extract_pack_display_name(pack)
                clean_pname = sanitize_apk_part(display_name)
                if cat:
                    if clean_pname in used_cat_names[cat]:
                        clean_pname = f"{clean_pname}_{sanitize_apk_part(pack.name)}"
                    used_cat_names[cat].add(clean_pname)
                for root, dirs, files in os.walk(pack):
                    rel_to_pack = Path(root).relative_to(pack)
                    clean_sub = "/".join(sanitize_apk_part(p) for p in rel_to_pack.parts) if rel_to_pack.parts else ""
                    for f in files:
                        fpath = Path(root) / f
                        if fpath.suffix.lower() in valid_exts and not fpath.name.startswith(".") and not fpath.name.endswith("~"):
                            clean_f = sanitize_apk_part(fpath.stem) + fpath.suffix.lower()
                            sub_p = f"{clean_sub}/{clean_f}" if clean_sub else clean_f
                            if is_v15:
                                assets.append((fpath, f"assets/custom/{clean_pname}/{sub_p}"))
                            elif cat:
                                assets.append((fpath, f"assets/{cat}/{clean_pname}/{sub_p}"))

    return assets

# -----------------------------------------------------------------------------
# GML SCRIPT PATCHING ROUTINES (WITH VERSION REDUNDANCY)
# -----------------------------------------------------------------------------
def apply_unified_diff(source_text: str, diff_text: str) -> str:
    """Applies a standard unified diff to source text in pure Python."""
    source_lines = source_text.splitlines(keepends=True)
    diff_lines = diff_text.splitlines(keepends=True)
    hunk_header_re = re.compile(r"^@@ -(\\d+)(?:,(\\d+))? \\+(\\d+)(?:,(\\d+))? @@")
    out_lines = []
    src_idx = 0
    i = 0
    while i < len(diff_lines):
        line = diff_lines[i]
        match = hunk_header_re.match(line)
        if match:
            old_start = int(match.group(1)) - 1
            while src_idx < old_start and src_idx < len(source_lines):
                out_lines.append(source_lines[src_idx])
                src_idx += 1
            i += 1
            while i < len(diff_lines) and not diff_lines[i].startswith("@@ ") and not diff_lines[i].startswith("--- "):
                h_line = diff_lines[i]
                if not h_line:
                    i += 1
                    continue
                tag = h_line[0]
                content = h_line[1:]
                if tag == " ":
                    out_lines.append(content)
                    src_idx += 1
                elif tag == "-":
                    src_idx += 1
                elif tag == "+":
                    out_lines.append(content)
                i += 1
            continue
        i += 1
    while src_idx < len(source_lines):
        out_lines.append(source_lines[src_idx])
        src_idx += 1
    return "".join(out_lines)

def patch_common_tc_funcs(code):
    """Patches tc_norm_path and tc_ff_* using exact function boundaries to eliminate native loops on Android."""
    old_norm = '''function tc_norm_path(arg0)
{
    arg0 = string(arg0);
    while (string_pos("//", arg0) > 0)
    {
        arg0 = string_replace_all(arg0, "//", "/");
    }
    return arg0;
}'''

    new_norm = '''function tc_norm_path(arg0)
{
    arg0 = string(arg0);
    while (string_pos("//", arg0) > 0)
    {
        arg0 = string_replace_all(arg0, "//", "/");
    }
    if (os_type == os_android || os_type == os_ios)
    {
        while (string_char_at(arg0, 1) == "/")
        {
            arg0 = string_delete(arg0, 1, 1);
        }
    }
    return arg0;
}'''

    if old_norm in code:
        code = code.replace(old_norm, new_norm, 1)

    old_tde = '''function tc_dir_exists(arg0)
{
    arg0 = tc_norm_path(arg0);
    if (string_char_at(arg0, string_length(arg0)) == "/")
    {
        arg0 = string_copy(arg0, 1, string_length(arg0) - 1);
    }
    return directory_exists(arg0) || file_exists(arg0 + "/_manifest.txt");
}'''

    new_tde = '''function tc_dir_exists(arg0)
{
    arg0 = tc_norm_path(arg0);
    if (string_char_at(arg0, string_length(arg0)) == "/")
    {
        arg0 = string_copy(arg0, 1, string_length(arg0) - 1);
    }
    return directory_exists(arg0) || file_exists(arg0 + "/_manifest.txt") || file_exists(arg0);
}'''
    if old_tde in code:
        code = code.replace(old_tde, new_tde, 1)

    new_tc_all = '''function tc_ff_first(arg0, arg1)
{
    tc_ff_items = -1;
    var _m = tc_norm_path(arg0);
    var _cut = string_last_pos("/", _m);
    var _mf = (_cut > 0) ? (string_copy(_m, 1, _cut) + "_manifest.txt") : "_manifest.txt";
    if (!file_exists(_mf))
    {
        if (os_type == os_android || os_type == os_ios) return "";
        return file_find_first(arg0, arg1);
    }
    var _pat = string_lower(string_delete(_m, 1, _cut));
    var _suf = (string_char_at(_pat, 1) == "*") ? string_delete(_pat, 1, 1) : "";
    tc_ff_items = [];
    var _f = file_text_open_read(_mf);
    if (_f != -1)
    {
        while (!file_text_eof(_f))
        {
            var _ln = string_replace_all(string_replace_all(file_text_readln(_f), chr(13), ""), chr(10), "");
            var _lo = string_lower(_ln);
            var _ok = _ln != "" && _lo != "_manifest.txt";
            if (_ok && string_char_at(_pat, 1) == "*")
            {
                _ok = _suf == "" || (string_length(_lo) >= string_length(_suf) && string_copy(_lo, (string_length(_lo) - string_length(_suf)) + 1, string_length(_suf)) == _suf);
            }
            else if (_ok)
            {
                _ok = _lo == _pat;
            }
            if (_ok)
            {
                array_push(tc_ff_items, _ln);
            }
        }
        file_text_close(_f);
    }
    if (os_type != os_android && os_type != os_ios)
    {
        var _real = file_find_first(arg0, arg1);
        while (_real != "")
        {
            if (!array_contains(tc_ff_items, _real))
            {
                array_push(tc_ff_items, _real);
            }
            _real = file_find_next();
        }
        file_find_close();
    }
    tc_ff_pos = 0;
    return tc_ff_next();
}

function tc_ff_next()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type == os_android || os_type == os_ios) return "";
        return file_find_next();
    }
    if (tc_ff_pos >= array_length(tc_ff_items))
    {
        return "";
    }
    tc_ff_pos++;
    return tc_ff_items[tc_ff_pos - 1];
}

function tc_ff_close()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type != os_android && os_type != os_ios) file_find_close();
    }
    tc_ff_items = -1;
    tc_ff_pos = 0;
}'''

    i1 = code.find("function tc_ff_first(arg0, arg1)")
    ic = code.find("function tc_ff_close()", i1)
    if i1 != -1 and ic != -1:
        brace_depth = 0
        found_start = False
        end_pos = -1
        for pos in range(ic, len(code)):
            if code[pos] == "{":
                brace_depth += 1
                found_start = True
            elif code[pos] == "}":
                brace_depth -= 1
                if found_start and brace_depth == 0:
                    end_pos = pos + 1
                    break
        if end_pos != -1:
            code = code[:i1] + new_tc_all + code[end_pos:]

    return code


def patch_background_code(code):
    """Patches oBackground_Create_0 to eliminate bedroom manifest loop hangs and scan custom bedrooms on Android."""
    code = patch_common_tc_funcs(code)
    old_bg_scan = '''function func_scan_custom_backgrounds()
{
    ds_list_clear(custom_background_folders);
    var _file = tc_ff_first(tc_wd + "/custom_bedrooms/*", 16);
    while (_file != "")
    {
        var _full_path = tc_wd + "/custom_bedrooms/" + _file;
        if (tc_dir_exists(_full_path) && func_check_custom_background(_full_path))
        {
            custom_background_loaded = true;
            ds_list_add(custom_background_folders, _full_path);
            show_debug_message("Loaded custom background pack: " + _file);
        }
        _file = tc_ff_next();
    }
    tc_ff_close();
}'''

    new_bg_scan = '''function func_scan_custom_backgrounds()
{
    ds_list_clear(custom_background_folders);
    custom_background_name_array = [];
    var _base_dir = (os_type == os_android || os_type == os_ios) ? "custom_bedrooms" : (tc_wd + "/custom_bedrooms");
    var _file = tc_ff_first(_base_dir + "/*", 16);
    while (_file != "")
    {
        if (_file != "." && _file != "..")
        {
            var _full_path = _base_dir + "/" + _file;
            if (func_check_custom_background(_full_path))
            {
                custom_background_loaded = true;
                ds_list_add(custom_background_folders, _full_path);
                show_debug_message("Loaded custom background pack: " + _file);
            }
        }
        _file = tc_ff_next();
    }
    tc_ff_close();
}'''
    if old_bg_scan in code:
        code = code.replace(old_bg_scan, new_bg_scan, 1)
    LOGGER.log("oBackground_Create_0: Neutralized native filesystem loops and scanned custom bedrooms.", prefix="[+]")
    return code


def patch_dialogue_code(code):
    """Patches oDialogueManager_Create_0 to eliminate dialogue manifest loop hangs on Android."""
    code = patch_common_tc_funcs(code)
    old_dlg_parse = '''    var _data = json_parse(_json_string);
    dialogue_json = _data;
    return true;'''

    new_dlg_parse = '''    try
    {
        var _data = json_parse(_json_string);
        dialogue_json = _data;
        return true;
    }
    catch (_err)
    {
        show_debug_message("Dialogue JSON parse error bypassed safely");
        return false;
    }'''

    old_dlg_load_full = '''function load_dialogue_file()
{
    var check_load_dialogue = func_load_dialogue(chosen_dialogue);
    if (check_load_dialogue == "")
    {
        exit;
    }
    var _file_name = "dialogue_packs/" + chosen_dialogue;
    if (!file_exists(_file_name))
    {
        if (file_exists("custom_dialogues/" + chosen_dialogue))
        {
            _file_name = "custom_dialogues/" + chosen_dialogue;
        }
    }
    var _buffer = buffer_load(_file_name);
    var _json_string = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);
    var _data = json_parse(_json_string);
    dialogue_json = _data;
    return true;
}'''

    new_dlg_load_full = '''function load_dialogue_file()
{
    func_load_dialogue(chosen_dialogue);
    if (chosen_dialogue == "")
    {
        return false;
    }
    var _file_name = "dialogue_packs/" + chosen_dialogue;
    if (!file_exists(_file_name))
    {
        if (file_exists("custom_dialogues/" + chosen_dialogue))
        {
            _file_name = "custom_dialogues/" + chosen_dialogue;
        }
        else if (file_exists("dialogue/" + chosen_dialogue))
        {
            _file_name = "dialogue/" + chosen_dialogue;
        }
        else if (file_exists(chosen_dialogue))
        {
            _file_name = chosen_dialogue;
        }
        else
        {
            return false;
        }
    }
    var _buffer = buffer_load(_file_name);
    if (_buffer == -1)
    {
        return false;
    }
    var _json_string = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);
    try
    {
        var _data = json_parse(_json_string);
        dialogue_json = _data;
        return true;
    }
    catch (_err)
    {
        show_debug_message("Dialogue JSON parse error bypassed safely");
        return false;
    }
}'''

    if old_dlg_load_full in code:
        code = code.replace(old_dlg_load_full, new_dlg_load_full, 1)

    if old_dlg_parse in code:
        code = code.replace(old_dlg_parse, new_dlg_parse, 1)
    # Dialogue Packs Precedence Over Character Dialogue
    old_top_dlg = '''        else if (_has_custom_top)
        {
            var _dlg_key = arg0;
            if (_dlg_key == "top_close_to_orgasm")
            {
                _dlg_key = "sex_halfway";
            }
            else if (_dlg_key == "condom_broke")
            {
                _dlg_key = "condom_broken";
            }
            else if (_dlg_key == "remove_full_condom")
            {
                _dlg_key = "condom_off";
            }
            else if (_dlg_key == "sex_after_with_condom")
            {
                _dlg_key = "sex_after";
            }
            else if (_dlg_key == "impregnate")
            {
                _dlg_key = "sex_orgasm";
            }
            else if (_dlg_key == "impregnate_after")
            {
                _dlg_key = "sex_after";
            }
            var _set = oFutaMatingPress.custom_dialogue_set_top;
            if (variable_struct_exists(_set, _dlg_key))
            {
                var _arr = variable_struct_get(_set, _dlg_key);
                if (is_array(_arr) && array_length(_arr) > 0)
                {
                    var _picked = _arr[irandom(array_length(_arr) - 1)];
                    if (_picked != "")
                    {
                        _picked = string_replace_all(_picked, "{0}", inject);
                        _picked = oFutaMatingPress.func_replace_tags(_picked);
                        lover_text = _picked;
                    }
                }
            }
        }
        else
        {
            lover_text = pick_from_dialogue_json(arg0, inject);
        }'''
    new_top_dlg = '''        else
        {
            if (dialogue_available && dialogue_toggle && chosen_dialogue != "")
            {
                lover_text = pick_from_dialogue_json(arg0, inject);
            }
            if (lover_text == "" && _has_custom_top)
            {
                var _dlg_key = arg0;
                if (_dlg_key == "top_close_to_orgasm") _dlg_key = "sex_halfway";
                else if (_dlg_key == "condom_broke") _dlg_key = "condom_broken";
                else if (_dlg_key == "remove_full_condom") _dlg_key = "condom_off";
                else if (_dlg_key == "sex_after_with_condom") _dlg_key = "sex_after";
                else if (_dlg_key == "impregnate") _dlg_key = "sex_orgasm";
                else if (_dlg_key == "impregnate_after") _dlg_key = "sex_after";
                var _set = oFutaMatingPress.custom_dialogue_set_top;
                if (variable_struct_exists(_set, _dlg_key))
                {
                    var _arr = variable_struct_get(_set, _dlg_key);
                    if (is_array(_arr) && array_length(_arr) > 0)
                    {
                        var _picked = _arr[irandom(array_length(_arr) - 1)];
                        if (_picked != "")
                        {
                            _picked = string_replace_all(_picked, "{0}", inject);
                            _picked = oFutaMatingPress.func_replace_tags(_picked);
                            lover_text = _picked;
                        }
                    }
                }
            }
            if (lover_text == "")
            {
                lover_text = pick_from_dialogue_json(arg0, inject);
            }
        }'''
    if old_top_dlg in code:
        code = code.replace(old_top_dlg, new_top_dlg, 1)

    LOGGER.log("oDialogueManager_Create_0: Neutralized native filesystem loops and protected dialogue JSON parsing.", prefix="[+]")
    return code


def patch_create_code(code, enable_toy_telemetry=False, opts=None):
    if opts is None: opts = {}
    """Patches Create_0 with variable safety, C ovulation disentanglement, and pill fallbacks."""
    code = patch_common_tc_funcs(code)
    if "boob_box = false;" not in code:
        code = "boob_box = false;\n" + code
        LOGGER.log("Create_0: Initialized boob_box = false upfront.", prefix="[+]")

    old_futa_origins = '''            sprite_origin_x = 80;
            sprite_origin_y = 84;
            portrait_origin_x = 64;
            portrait_origin_y = 64;'''

    new_futa_origins = '''            sprite_origin_x = 80;
            sprite_origin_y = 84;
            cowgirl_origin_x = 80;
            cowgirl_origin_y = 84;
            mp_origin_x = 80;
            mp_origin_y = 84;
            dt_origin_x = 80;
            dt_origin_y = 84;
            portrait_origin_x = 64;
            portrait_origin_y = 64;'''

    if old_futa_origins in code:
        code = code.replace(old_futa_origins, new_futa_origins, 1)
        LOGGER.log("Create_0: Initialized cowgirl_origin_y upfront.", prefix="[+]")

    old_climax_ov = '''    if (sex_position != 3)
    {
        for (var i = 0; i < wife_climax_stage; i++)
        {
            if (i == 0)
            {
                func_ovulate();
            }
            else
            {
                var total_chance = 0.2 + (count_normal * 0.3) + stat_bonus;
                var drop_chance = total_chance / i;
                if (random(1) <= drop_chance)
                {
                    func_ovulate();
                }
            }
        }
    }'''

    new_climax_ov = '''    // Ovulation separated from wife climax - triggered exclusively via [O] Ovulate button
    // (func_ovulate removed from func_wife_climax)'''

    if old_climax_ov in code:
        code = code.replace(old_climax_ov, new_climax_ov, 1)
        LOGGER.log("Create_0: Disentangled C from ovulation in func_wife_climax.", prefix="[+]")

    if 'working_directory + "/setting_data.sav"' in code:
        code = code.replace('working_directory + "/setting_data.sav"', '"setting_data.sav"')
        LOGGER.log("Create_0: Replaced working_directory path with persistent sandboxed setting_data.sav.", prefix="[+]")

    old_legacy_shaft_0 = '''                case "shaft":
                    comment = "layer 1 (base/sheath)";
                    if (penis_type_index == 0)
                    {
                        comment = "human shaft";
                        return 7;
                    }
                    if (penis_type_index == 1)
                    {
                        comment = "horse sheath";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis full";
                        return -1;
                    }
                    if (penis_type_index == 3)
                    {
                        comment = "knotted horse full";
                        return -1;
                    }
                    return 7;'''

    new_legacy_shaft_0 = '''                case "shaft":
                    comment = "layer 1 (base/sheath) - safely falls back to base custom asset if pill art missing";
                    return 7;'''

    if old_legacy_shaft_0 in code:
        code = code.replace(old_legacy_shaft_0, new_legacy_shaft_0, 1)

    old_legacy_shaft_1 = '''                case "shaft":
                    comment = "layer 1 (base/sheath)";
                    if (penis_type_index == 0)
                    {
                        comment = "human shaft";
                        return 2;
                    }
                    if (penis_type_index == 1)
                    {
                        comment = "horse sheath";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis";
                        return -1;
                    }
                    if (penis_type_index == 3)
                    {
                        comment = "knotted horse shaft";
                        return -1;
                    }
                    return 2;'''

    new_legacy_shaft_1 = '''                case "shaft":
                    comment = "layer 1 (base/sheath) - safely falls back to base custom asset if pill art missing";
                    return 2;'''

    if old_legacy_shaft_1 in code:
        code = code.replace(old_legacy_shaft_1, new_legacy_shaft_1, 1)

    old_mod_shaft_0 = '''            case "shaft":
                comment = "layer 1 (base/sheath)";
                if (penis_type_index == 0)
                {
                    comment = "human shaft";
                    return 7;
                }
                if (penis_type_index == 1)
                {
                    comment = "horse sheath";
                    return 11;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis full";
                    return 15;
                }
                if (penis_type_index == 3)
                {
                    comment = "knotted horse full";
                    return 18;
                }
                return 7;'''

    new_mod_shaft_0 = '''            case "shaft":
                comment = "layer 1 (base/sheath) - safe fallback to base shaft if custom spritesheet lacks pill frames";
                var _spr_frames = sprite_get_number(top_sprite);
                if (penis_type_index == 1 && _spr_frames > 11)
                    return 11;
                if (penis_type_index == 2 && _spr_frames > 15)
                    return 15;
                if (penis_type_index == 3 && _spr_frames > 18)
                    return 18;
                return 7;'''

    if old_mod_shaft_0 in code:
        code = code.replace(old_mod_shaft_0, new_mod_shaft_0, 1)
        LOGGER.log("Create_0: Safe pill art asset fallback active in func_get_futa_frame.", prefix="[+]")

    # Persist continuous_toggle in setting_data.sav
    old_clench_save = 'ini_write_real("features", "custom_clench_toggle", custom_clench_toggle);'
    new_clench_save = '''ini_write_real("features", "custom_clench_toggle", custom_clench_toggle);
    ini_write_real("features", "continuous_toggle", continuous_toggle);'''
    if old_clench_save in code and 'ini_write_real("features", "continuous_toggle"' not in code:
        code = code.replace(old_clench_save, new_clench_save, 1)

    old_clench_load = 'custom_clench_toggle = ini_read_real("features", "custom_clench_toggle", 0);'
    new_clench_load = '''custom_clench_toggle = ini_read_real("features", "custom_clench_toggle", 0);
    continuous_toggle = bool(ini_read_real("features", "continuous_toggle", false));'''
    if old_clench_load in code and 'ini_read_real("features", "continuous_toggle"' not in code:
        code = code.replace(old_clench_load, new_clench_load, 1)
        LOGGER.log("Create_0: Added continuous_toggle persistence to setting_data.sav.", prefix="[+]")

    old_norm_find = '''function tc_norm_path(arg0)
{
    arg0 = string(arg0);
    while (string_pos("//", arg0) > 0)
    {
        arg0 = string_replace_all(arg0, "//", "/");
    }
    return arg0;
}'''
    new_norm_find = '''function tc_norm_path(arg0)
{
    arg0 = string(arg0);
    while (string_pos("//", arg0) > 0)
    {
        arg0 = string_replace_all(arg0, "//", "/");
    }
    if (os_type == os_android || os_type == os_ios)
    {
        while (string_char_at(arg0, 1) == "/")
        {
            arg0 = string_delete(arg0, 1, 1);
        }
    }
    return arg0;
}'''
    if old_norm_find in code:
        code = code.replace(old_norm_find, new_norm_find, 1)
        LOGGER.log("Create_0: Injected leading slash removal in tc_norm_path for Android asset loading.", prefix="[+]")

    old_tc_target = '''function tc_ff_first(arg0, arg1)
{
    tc_ff_items = -1;
    var _m = tc_norm_path(arg0);
    var _cut = string_last_pos("/", _m);
    var _mf = (_cut > 0) ? (string_copy(_m, 1, _cut) + "_manifest.txt") : "_manifest.txt";
    if (!file_exists(_mf))
    {
        return file_find_first(arg0, arg1);
    }
    var _pat = string_lower(string_delete(_m, 1, _cut));
    var _suf = (string_char_at(_pat, 1) == "*") ? string_delete(_pat, 1, 1) : "";
    tc_ff_items = [];
    var _f = file_text_open_read(_mf);
    while (!file_text_eof(_f))
    {
        var _ln = string_replace_all(string_replace_all(file_text_readln(_f), "
", ""), "
", "");
        var _lo = string_lower(_ln);
        var _ok = _ln != "" && _lo != "_manifest.txt";
        if (_ok && string_char_at(_pat, 1) == "*")
        {
            _ok = _suf == "" || (string_length(_lo) >= string_length(_suf) && string_copy(_lo, (string_length(_lo) - string_length(_suf)) + 1, string_length(_suf)) == _suf);
        }
        else if (_ok)
        {
            _ok = _lo == _pat;
        }
        if (_ok)
        {
            array_push(tc_ff_items, _ln);
        }
    }
    file_text_close(_f);
    var _real = file_find_first(arg0, arg1);
    while (_real != "")
    {
        if (!array_contains(tc_ff_items, _real))
        {
            array_push(tc_ff_items, _real);
        }
        _real = file_find_next();
    }
    file_find_close();
    tc_ff_pos = 0;
    return tc_ff_next();
}'''
    new_tc_target = '''function tc_ff_first(arg0, arg1)
{
    tc_ff_items = -1;
    var _m = tc_norm_path(arg0);
    var _cut = string_last_pos("/", _m);
    var _mf = (_cut > 0) ? (string_copy(_m, 1, _cut) + "_manifest.txt") : "_manifest.txt";
    if (!file_exists(_mf))
    {
        if (os_type == os_android || os_type == os_ios) return "";
        return file_find_first(arg0, arg1);
    }
    var _pat = string_lower(string_delete(_m, 1, _cut));
    var _suf = (string_char_at(_pat, 1) == "*") ? string_delete(_pat, 1, 1) : "";
    tc_ff_items = [];
    var _f = file_text_open_read(_mf);
    if (_f != -1)
    {
        while (!file_text_eof(_f))
        {
            var _ln = string_replace_all(string_replace_all(file_text_readln(_f), "
", ""), "
", "");
            var _lo = string_lower(_ln);
            var _ok = _ln != "" && _lo != "_manifest.txt";
            if (_ok && string_char_at(_pat, 1) == "*")
            {
                _ok = _suf == "" || (string_length(_lo) >= string_length(_suf) && string_copy(_lo, (string_length(_lo) - string_length(_suf)) + 1, string_length(_suf)) == _suf);
            }
            else if (_ok)
            {
                _ok = _lo == _pat;
            }
            if (_ok)
            {
                array_push(tc_ff_items, _ln);
            }
        }
        file_text_close(_f);
    }
    if (os_type != os_android && os_type != os_ios)
    {
        var _real = file_find_first(arg0, arg1);
        while (_real != "")
        {
            if (!array_contains(tc_ff_items, _real))
            {
                array_push(tc_ff_items, _real);
            }
            _real = file_find_next();
        }
        file_find_close();
    }
    tc_ff_pos = 0;
    return tc_ff_next();
}'''
    if old_tc_target in code:
        code = code.replace(old_tc_target, new_tc_target, 1)
        LOGGER.log("Create_0: Neutralized native file_find_first loops in tc_ff_first to eliminate Android filesystem hangs.", prefix="[+]")

    old_next_find = '''function tc_ff_next()
{
    if (!is_array(tc_ff_items))
    {
        return file_find_next();
    }
    if (tc_ff_pos >= array_length(tc_ff_items))
    {
        return "";
    }
    tc_ff_pos++;
    return tc_ff_items[tc_ff_pos - 1];
}

function tc_ff_close()
{
    if (!is_array(tc_ff_items))
    {
        file_find_close();
    }
    tc_ff_items = -1;
    tc_ff_pos = 0;
}'''
    new_next_find = '''function tc_ff_next()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type == os_android || os_type == os_ios)
        {
            return "";
        }
        return file_find_next();
    }
    if (tc_ff_pos >= array_length(tc_ff_items))
    {
        return "";
    }
    tc_ff_pos++;
    return tc_ff_items[tc_ff_pos - 1];
}

function tc_ff_close()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type != os_android && os_type != os_ios)
        {
            file_find_close();
        }
    }
    tc_ff_items = -1;
    tc_ff_pos = 0;
}'''
    if old_next_find in code:
        code = code.replace(old_next_find, new_next_find, 1)
        LOGGER.log("Create_0: Neutralized native file_find_next/close on mobile.", prefix="[+]")

    # 1. Prevent Out-Of-Memory startup crash by skipping upfront thumbnail loading on mobile
    old_legacy_w_load = '''                var _w_port = _full_path + "/custom_portrait.png";
                var _w_spr = -1;
                if (file_exists(_w_port))
                {
                    _w_spr = sprite_add(_w_port, 10, false, false, 32, 48);
                }
                ds_list_add(wife_selector_portraits, _w_spr);'''

    new_legacy_w_load = '''                var _w_port = _full_path + "/custom_portrait.png";
                var _w_spr = -1;
                if (!_is_mobile && file_exists(_w_port))
                {
                    _w_spr = sprite_add(_w_port, 10, false, false, 32, 48);
                }
                ds_list_add(wife_selector_portraits, _w_spr);'''

    if old_legacy_w_load in code:
        code = code.replace(old_legacy_w_load, new_legacy_w_load, 1)

    old_cf_find = '''function check_custom_futa(arg0)
{
    arg0 = tc_norm_path(arg0);
    var is_legacy = false;
    if (file_exists(string(arg0) + "/custom_mating_press.png"))
    {
        is_legacy = check_custom_image_size(arg0);
    }
    check_struct = {};
    if (is_legacy)
    {
        check_struct.custom_data = file_exists(string(arg0) + "/custom_data.futa");
        check_struct.custom_portrait = file_exists(string(arg0) + "/custom_portrait.png");
        check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_mating_press.png");
        check_struct.custom_cowgirls = file_exists(string(arg0) + "/custom_reverse_cowgirl.png");
        check_struct.custom_xray = file_exists(string(arg0) + "/custom_xray.png");
    }
    else
    {
        check_struct.custom_data = file_exists(string(arg0) + "/custom_data.futa");
        check_struct.custom_portrait = file_exists(string(arg0) + "/custom_futa_portrait_0.png");
        check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_futa_mating_press_0.png");
        check_struct.custom_cowgirls = file_exists(string(arg0) + "/custom_futa_cowgirls_0.png");
        check_struct.custom_xray = file_exists(string(arg0) + "/custom_futa_xray_0.png");
    }
    return check_struct;
}'''

    new_cf_find = '''function check_custom_futa(arg0)
{
    arg0 = tc_norm_path(arg0);
    var is_legacy = file_exists(string(arg0) + "/custom_mating_press.png") && !file_exists(string(arg0) + "/custom_futa_mating_press_0.png");
    check_struct = {};
    if (is_legacy)
    {
        check_struct.custom_data = file_exists(string(arg0) + "/custom_data.futa");
        check_struct.custom_portrait = file_exists(string(arg0) + "/custom_portrait.png");
        check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_mating_press.png");
        check_struct.custom_cowgirls = file_exists(string(arg0) + "/custom_reverse_cowgirl.png");
        check_struct.custom_xray = file_exists(string(arg0) + "/custom_xray.png");
    }
    else
    {
        check_struct.custom_data = file_exists(string(arg0) + "/custom_data.futa");
        check_struct.custom_portrait = file_exists(string(arg0) + "/custom_futa_portrait_0.png");
        check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_futa_mating_press_0.png");
        check_struct.custom_cowgirls = file_exists(string(arg0) + "/custom_futa_cowgirls_0.png");
        check_struct.custom_xray = file_exists(string(arg0) + "/custom_futa_xray_0.png");
    }
    return check_struct;
}'''

    if old_cf_find in code:
        code = code.replace(old_cf_find, new_cf_find, 1)
        LOGGER.log("Create_0: Eliminated check_custom_image_size blocking sprite_add startup hang.", prefix="[+]")

    # -------------------------------------------------------------
    # MOD COMPATIBILITY OVERHAUL: Radio, Voice Packs, Vanilla Dialogues, Texture Packs
    # -------------------------------------------------------------
    old_radio = '''function func_radio_scan()
{
    ds_list_clear(radio_track_list);
    var _base = tc_wd + "/custom_music";
    if (!tc_dir_exists(_base))
    {
        radio_has_tracks = false;
        exit;
    }
    var _f = tc_ff_first(_base + "/*.ogg", 0);'''

    new_radio = '''function func_radio_scan()
{
    ds_list_clear(radio_track_list);
    var _base = (os_type == os_android || os_type == os_ios) ? "custom_music" : (tc_wd + "/custom_music");
    var _f = tc_ff_first(_base + "/*.ogg", 0);'''
    if old_radio in code:
        code = code.replace(old_radio, new_radio, 1)

    old_cs = '''var _cs_base = tc_wd + "/custom_sounds/futa";
if (tc_dir_exists(_cs_base))
{
    var _cs_file = tc_ff_first(_cs_base + "/*", 16);
    while (_cs_file != "")
    {
        var _cs_full = _cs_base + "/" + _cs_file;
        if (tc_dir_exists(_cs_full))
        {
            ds_list_add(cs_futa_packs, _cs_full);
            ds_list_add(cs_futa_pack_names, _cs_file);
        }
        _cs_file = tc_ff_next();
    }
    tc_ff_close();
}'''

    new_cs = '''var _cs_bases = ["custom_sounds/futa", "custom_sounds"];
for (var _bi = 0; _bi < array_length(_cs_bases); _bi++)
{
    var _base = _cs_bases[_bi];
    var _cs_file = tc_ff_first(_base + "/*", 16);
    while (_cs_file != "")
    {
        if (_cs_file != "." && _cs_file != ".." && _cs_file != "futa" && _cs_file != "wife (placeholder)" && _cs_file != "sfx (placeholder)")
        {
            var _cs_full = _base + "/" + _cs_file;
            if (file_exists(_cs_full + "/moan_slow/_manifest.txt") || file_exists(_cs_full + "/moan_fast/_manifest.txt") || file_exists(_cs_full + "/_manifest.txt") || tc_dir_exists(_cs_full))
            {
                if (ds_list_find_index(cs_futa_pack_names, _cs_file) == -1)
                {
                    ds_list_add(cs_futa_packs, _cs_full);
                    ds_list_add(cs_futa_pack_names, _cs_file);
                }
            }
        }
        _cs_file = tc_ff_next();
    }
    tc_ff_close();
}'''
    if old_cs in code:
        code = code.replace(old_cs, new_cs, 1)

    old_gca = '''function func_get_custom_audio(arg0, arg1)
{
    if (tc_dir_exists(arg1) == true)
    {
        ds_list_clear(arg0);
        show_debug_message("scanning folder: " + string(arg1));
        var _file = tc_ff_first(string(arg1) + "/*.ogg", 0);'''

    new_gca = '''function func_get_custom_audio(arg0, arg1)
{
    arg1 = tc_norm_path(arg1);
    var _has_manifest = file_exists(arg1 + "/_manifest.txt");
    if (_has_manifest || tc_dir_exists(arg1))
    {
        ds_list_clear(arg0);
        show_debug_message("scanning folder: " + string(arg1));
        var _file = tc_ff_first(string(arg1) + "/*.ogg", 0);'''
    if old_gca in code:
        code = code.replace(old_gca, new_gca, 1)

    old_v_dlg = '''function func_load_vanilla_dialogue(arg0)
{
    custom_dialogue_set_top = -1;
    var _path = working_directory + "dialogue/" + arg0;
    if (!file_exists(_path))
    {
        exit;
    }'''

    new_v_dlg = '''function func_load_vanilla_dialogue(arg0)
{
    custom_dialogue_set_top = -1;
    var _path = (os_type == os_android || os_type == os_ios) ? ("dialogue/" + arg0) : (working_directory + "dialogue/" + arg0);
    if (!file_exists(_path))
    {
        _path = "dialogue_packs/" + arg0;
        if (!file_exists(_path))
        {
            exit;
        }
    }'''
    if old_v_dlg in code:
        code = code.replace(old_v_dlg, new_v_dlg, 1)

    old_tp_backup = '''function func_texture_pack_backup_vanilla()
{
    global.sprite_backup = [];
    
    function backup_sprite(arg0)
    {
        array_push(global.sprite_backup, 
        {
            sprite: arg0,
            frames: sprite_get_number(arg0),
            xorig: sprite_get_xoffset(arg0),
            yorig: sprite_get_yoffset(arg0)
        });
    }
    
    for (var i = 0; i < array_length(sprite_list); i += 1)
    {
        backup_sprite(sprite_list[i]);
    }
}'''

    new_tp_backup = '''function func_texture_pack_backup_vanilla()
{
    global.sprite_backup = [];
    for (var i = 0; i < array_length(sprite_list); i += 1)
    {
        var _spr_item = sprite_list[i];
        var _entry = {
            sprite: _spr_item,
            frames: sprite_get_number(_spr_item),
            xorig: sprite_get_xoffset(_spr_item),
            yorig: sprite_get_yoffset(_spr_item)
        };
        array_push(global.sprite_backup, _entry);
    }
}'''
    if old_tp_backup in code:
        code = code.replace(old_tp_backup, new_tp_backup, 1)

    old_tp_replace = '''function func_texture_pack_replace(arg0)
{
    for (var i = 0; i < array_length(sprite_list); i++)
    {
        var _filename = "texture_packs/" + arg0 + "/" + sprite_get_name(sprite_list[i]) + ".png";
        if (file_exists(_filename))
        {
            sprite_replace(sprite_list[i], _filename, global.sprite_backup[i].frames, false, false, global.sprite_backup[i].xorig, global.sprite_backup[i].yorig);
        }
    }
}'''

    new_tp_replace = '''function func_texture_pack_replace(arg0)
{
    for (var i = 0; i < array_length(sprite_list); i++)
    {
        var _filename = "texture_packs/" + arg0 + "/" + sprite_get_name(sprite_list[i]) + ".png";
        if (file_exists(_filename))
        {
            sprite_replace(sprite_list[i], _filename, global.sprite_backup[i].frames, false, false, global.sprite_backup[i].xorig, global.sprite_backup[i].yorig);
        }
        else if (i < array_length(global.sprite_backup))
        {
            sprite_assign(sprite_list[i], global.sprite_backup[i].sprite);
        }
    }
}'''
    if old_tp_replace in code:
        code = code.replace(old_tp_replace, new_tp_replace, 1)

    old_futa_buf = r"""var _f_buf = buffer_load("custom_futas/_manifest.txt");
if (_f_buf == -1 && _wd != "")
{
    _f_buf = buffer_load(_wd + "/custom_futas/_manifest.txt");
}
if (_f_buf != -1)
{
    var _f_str = buffer_read(_f_buf, buffer_string);
    buffer_delete(_f_buf);
    _f_str = string_replace_all(_f_str, "\r", "");
    var _cur_line = "";
    for (var _ci = 1; _ci <= string_length(_f_str); _ci++)
    {
        var _ch = string_char_at(_f_str, _ci);
        if (_ch == "\n")
        {
            if (_cur_line != "")
            {
                array_push(_futa_names, _cur_line);
                _cur_line = "";
            }
        }
        else
        {
            _cur_line += _ch;
        }
    }
    if (_cur_line != "")
    {
        array_push(_futa_names, _cur_line);
    }
}
else
{
    var _ff_futa = tc_ff_first(_wd + "/custom_futas/*", 16);
    while (_ff_futa != "")
    {
        array_push(_futa_names, _ff_futa);
        _ff_futa = tc_ff_next();
    }
    tc_ff_close();
}"""
    new_futa_buf = """var _futa_names = [];
var _mf_p = "custom_futas/_manifest.txt";
var _mf_futa = file_text_open_read(_mf_p);
if (_mf_futa == -1 && _wd != "")
{
    _mf_futa = file_text_open_read(_wd + "/custom_futas/_manifest.txt");
}
if (_mf_futa != -1)
{
    while (!file_text_eof(_mf_futa))
    {
        var _mf_line = string_replace_all(string_replace_all(file_text_readln(_mf_futa), chr(13), ""), chr(10), "");
        if (_mf_line != "" && _mf_line != "_manifest.txt")
        {
            array_push(_futa_names, _mf_line);
        }
    }
    file_text_close(_mf_futa);
}
if (array_length(_futa_names) == 0)
{
    var _f_buf = buffer_load(_mf_p);
    if (_f_buf == -1 && _wd != "")
    {
        _f_buf = buffer_load(_wd + "/custom_futas/_manifest.txt");
    }
    if (_f_buf != -1)
    {
        var _f_str = string_replace_all(buffer_read(_f_buf, buffer_string), chr(13), "");
        buffer_delete(_f_buf);
        var _cur_line = "";
        for (var _ci = 1; _ci <= string_length(_f_str); _ci++)
        {
            var _ch = string_char_at(_f_str, _ci);
            if (_ch == chr(10))
            {
                if (_cur_line != "" && _cur_line != "_manifest.txt")
                {
                    array_push(_futa_names, _cur_line);
                    _cur_line = "";
                }
            }
            else
            {
                _cur_line += _ch;
            }
        }
        if (_cur_line != "" && _cur_line != "_manifest.txt")
        {
            array_push(_futa_names, _cur_line);
        }
    }
}"""
    if old_futa_buf in code:
        code = code.replace(old_futa_buf, new_futa_buf, 1)
        LOGGER.log("Create_0: Injected native text stream manifest reader for custom futas.", prefix="[+]")

    old_wife_buf = r"""var _w_buf = buffer_load("custom_wives/_manifest.txt");
if (_w_buf == -1 && _wd != "")
{
    _w_buf = buffer_load(_wd + "/custom_wives/_manifest.txt");
}
if (_w_buf != -1)
{
    var _w_str = buffer_read(_w_buf, buffer_string);
    buffer_delete(_w_buf);
    _w_str = string_replace_all(_w_str, "\r", "");
    var _cur_wline = "";
    for (var _ci = 1; _ci <= string_length(_w_str); _ci++)
    {
        var _ch = string_char_at(_w_str, _ci);
        if (_ch == "\n")
        {
            if (_cur_wline != "")
            {
                array_push(_wife_names, _cur_wline);
                _cur_wline = "";
            }
        }
        else
        {
            _cur_wline += _ch;
        }
    }
    if (_cur_wline != "")
    {
        array_push(_wife_names, _cur_wline);
    }
}
else
{
    var _ff_wife = tc_ff_first(_wd + "/custom_wives/*", 16);
    while (_ff_wife != "")
    {
        array_push(_wife_names, _ff_wife);
        _ff_wife = tc_ff_next();
    }
    tc_ff_close();
}"""
    new_wife_buf = """var _wife_names = [];
var _mf_pw = "custom_wives/_manifest.txt";
var _mf_wife = file_text_open_read(_mf_pw);
if (_mf_wife == -1 && _wd != "")
{
    _mf_wife = file_text_open_read(_wd + "/custom_wives/_manifest.txt");
}
if (_mf_wife != -1)
{
    while (!file_text_eof(_mf_wife))
    {
        var _mf_line2 = string_replace_all(string_replace_all(file_text_readln(_mf_wife), chr(13), ""), chr(10), "");
        if (_mf_line2 != "" && _mf_line2 != "_manifest.txt")
        {
            array_push(_wife_names, _mf_line2);
        }
    }
    file_text_close(_mf_wife);
}
if (array_length(_wife_names) == 0)
{
    var _w_buf = buffer_load(_mf_pw);
    if (_w_buf == -1 && _wd != "")
    {
        _w_buf = buffer_load(_wd + "/custom_wives/_manifest.txt");
    }
    if (_w_buf != -1)
    {
        var _w_str = string_replace_all(buffer_read(_w_buf, buffer_string), chr(13), "");
        buffer_delete(_w_buf);
        var _cur_wline = "";
        for (var _ci = 1; _ci <= string_length(_w_str); _ci++)
        {
            var _ch = string_char_at(_w_str, _ci);
            if (_ch == chr(10))
            {
                if (_cur_wline != "" && _cur_wline != "_manifest.txt")
                {
                    array_push(_wife_names, _cur_wline);
                    _cur_wline = "";
                }
            }
            else
            {
                _cur_wline += _ch;
            }
        }
        if (_cur_wline != "" && _cur_wline != "_manifest.txt")
        {
            array_push(_wife_names, _cur_wline);
        }
    }
}"""
    if old_wife_buf in code:
        code = code.replace(old_wife_buf, new_wife_buf, 1)
        LOGGER.log("Create_0: Injected native text stream manifest reader for custom wives.", prefix="[+]")

        # Character Loader Fortification: Guarantee non-negative, valid sprites for custom lovers and wives
    old_apply_futa = '''function func_apply_custom_futa_stats()
{
    if (is_legacy_custom)
    {
        top_sprite = legacy_custom_mating_press;
        penis_sprite = legacy_custom_mating_press;
        hair_sprite = legacy_custom_mating_press;
        face_sprite = legacy_custom_portrait;
        bangs_sprite = legacy_custom_portrait;
        condom_offset_mpress = custom_condom_offset_mpress;
        condom_offset_cowgirls = custom_condom_offset_cowgirls;
    }
    else
    {
        top_sprite = custom_mating_press;
        penis_sprite = custom_mating_press;
        hair_sprite = custom_mating_press;
        face_sprite = custom_portrait;
        bangs_sprite = custom_portrait;
        condom_offset_mpress = custom_condom_offset_mpress;
        condom_offset_cowgirls = custom_condom_offset_cowgirls;
    }'''

    new_apply_futa = '''function func_apply_custom_futa_stats()
{
    if (is_legacy_custom)
    {
        top_sprite = (sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press != -1) ? legacy_custom_mating_press : sFutaMatingPress;
        penis_sprite = top_sprite;
        hair_sprite = top_sprite;
        face_sprite = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
        bangs_sprite = face_sprite;
        condom_offset_mpress = custom_condom_offset_mpress;
        condom_offset_cowgirls = custom_condom_offset_cowgirls;
    }
    else
    {
        top_sprite = (sprite_exists(custom_mating_press) && custom_mating_press != -1) ? custom_mating_press : sFutaMatingPress;
        penis_sprite = top_sprite;
        hair_sprite = top_sprite;
        face_sprite = (sprite_exists(custom_portrait) && custom_portrait != -1) ? custom_portrait : sFutaPortrait1;
        bangs_sprite = face_sprite;
        condom_offset_mpress = custom_condom_offset_mpress;
        condom_offset_cowgirls = custom_condom_offset_cowgirls;
    }'''
    if old_apply_futa in code:
        code = code.replace(old_apply_futa, new_apply_futa, 1)

    old_apply_wife = '''    wife_bangs_sprite = custom_wife_portrait;
    wife_hair_sprite = custom_wife_mating_press;'''

    new_apply_wife = '''    var _valid_wife_port = -1;
    if (sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1) _valid_wife_port = custom_wife_portrait;
    else if (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1) _valid_wife_port = legacy_custom_wife_portrait;
    else _valid_wife_port = sFutaPortrait1;
    wife_bangs_sprite = _valid_wife_port;

    var _valid_wife_body = -1;
    if (sprite_exists(custom_wife_mating_press) && custom_wife_mating_press != -1) _valid_wife_body = custom_wife_mating_press;
    else if (sprite_exists(legacy_custom_wife_mating_press) && legacy_custom_wife_mating_press != -1) _valid_wife_body = legacy_custom_wife_mating_press;
    else _valid_wife_body = sWifeMatingPress;
    wife_hair_sprite = _valid_wife_body;'''
    if old_apply_wife in code:
        code = code.replace(old_apply_wife, new_apply_wife, 1)

    old_get_port = '''            }
            break;
    }
    return return_port;
}

function func_wife_portrait_body(arg0)'''

    new_get_port = '''            }
            break;
    }
    if (return_port <= 0 || !sprite_exists(return_port)) return_port = sFutaPortrait1;
    return return_port;
}

function func_wife_portrait_body(arg0)'''
    if old_get_port in code:
        code = code.replace(old_get_port, new_get_port, 1)

    old_get_boobs = '''            }
            break;
    }
    return return_port;
}

function func_get_alt_boob_sprite(arg0)'''

    new_get_boobs = '''            }
            break;
    }
    if (return_port <= 0 || !sprite_exists(return_port)) return_port = sFutaPortrait1;
    return return_port;
}

function func_get_alt_boob_sprite(arg0)'''
    if old_get_boobs in code:
        code = code.replace(old_get_boobs, new_get_boobs, 1)

    old_cis = '''function check_custom_image_size(arg0)
{
    var result = -1;
    var test_sprite = sprite_add(arg0 + "/custom_mating_press.png", 1, false, false, 0, 0);
    var w = sprite_get_width(test_sprite);
    var frame_width = 160;
    var frames = w / frame_width;
    if (frames != 19)
    {
        result = true;
    }
    else
    {
        result = false;
    }
    sprite_delete(test_sprite);
    return result;
}'''

    new_cis = '''function check_custom_image_size(arg0)
{
    return true;
}'''

    if old_cis in code:
        code = code.replace(old_cis, new_cis, 1)

    # 2. Universal Modroom & Legacy Wife character support (checks both naming schemes)
    old_check_w = '''function check_custom_wife(arg0)
{
    arg0 = tc_norm_path(arg0);
    check_struct = {};
    check_struct.custom_wife_mating_press = file_exists(string(arg0) + "/custom_wife_mating_press_0.png");
    check_struct.custom_wife_cowgirl = file_exists(string(arg0) + "/custom_wife_cowgirl_0.png");
    check_struct.custom_wife_reverse_cowgirl = file_exists(string(arg0) + "/custom_wife_reverse_cowgirl_0.png");
    check_struct.custom_wife_portrait = file_exists(string(arg0) + "/custom_wife_portrait_0.png");
    return check_struct;
}'''

    new_check_w = '''function check_custom_wife(arg0)
{
    arg0 = tc_norm_path(arg0);
    check_struct = {};
    check_struct.custom_wife_mating_press = file_exists(string(arg0) + "/custom_wife_mating_press_0.png") || file_exists(string(arg0) + "/custom_mating_press.png");
    check_struct.custom_wife_cowgirl = file_exists(string(arg0) + "/custom_wife_cowgirl_0.png") || file_exists(string(arg0) + "/custom_reverse_cowgirl.png");
    check_struct.custom_wife_reverse_cowgirl = file_exists(string(arg0) + "/custom_wife_reverse_cowgirl_0.png") || file_exists(string(arg0) + "/custom_reverse_cowgirl.png");
    check_struct.custom_wife_portrait = file_exists(string(arg0) + "/custom_wife_portrait_0.png") || file_exists(string(arg0) + "/custom_portrait.png");
    return check_struct;
}'''

    if old_check_w in code:
        code = code.replace(old_check_w, new_check_w, 1)
        LOGGER.log("Create_0: Enabled universal Modroom & Legacy format detection in check_custom_wife.", prefix="[+]")

    old_lcw = '''function func_load_custom_wife(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    if (file_exists(string(arg0) + "/custom_data.spouse"))'''
    new_lcw = '''function func_load_custom_wife(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    if (file_exists(string(arg0) + "/custom_data.spouse") || file_exists(string(arg0) + "/custom_mating_press.png") || !file_exists(string(arg0) + "/custom_wife_mating_press_0.png"))'''
    if old_lcw in code:
        code = code.replace(old_lcw, new_lcw, 1)
        LOGGER.log("Create_0: Universal Legacy Spouse Detection in func_load_custom_wife enabled.", prefix="[+]")

    # 3. Guard livestream JSON parsing against malformed JSON syntax crashes
    old_ls_json = '''    file_text_close(_ls_file);
    livestream_dialogue = json_parse(_ls_json_string);'''

    new_ls_json = '''    file_text_close(_ls_file);
    try
    {
        livestream_dialogue = json_parse(_ls_json_string);
    }
    catch (_err)
    {
        show_debug_message("Livestream JSON parse error bypassed safely");
    }'''

    if old_ls_json in code:
        code = code.replace(old_ls_json, new_ls_json, 1)

        # 4. Instant In-Memory Manifest Indexing on Mobile (Eliminates 13,000+ synchronous file_exists JNI calls)
    old_futa_loop = '''for (var _fi = 0; _fi < array_length(_futa_names); _fi++)
{
    var _file = _futa_names[_fi];
    var _full_path = _is_mobile ? ("custom_futas/" + _file) : (_wd + "/custom_futas/" + _file);
    if (_futa_manifest || tc_dir_exists(_full_path))'''

    new_futa_loop = '''for (var _fi = 0; _fi < array_length(_futa_names); _fi++)
{
    var _file = _futa_names[_fi];
    var _full_path = _is_mobile ? ("custom_futas/" + _file) : (_wd + "/custom_futas/" + _file);
    if (_is_mobile && _futa_manifest)
    {
        custom_sprite_loaded = true;
        tutorial = false;
        ds_list_add(custom_futas_folder, _full_path);
        ds_list_add(futa_selector_names, _file);
        ds_list_add(futa_selector_has_deepthroat, true);
        ds_list_add(futa_selector_has_alts, false);
        ds_list_add(futa_selector_portraits, -1);
    }
    else if (_futa_manifest || tc_dir_exists(_full_path))'''

    if old_futa_loop in code:
        code = code.replace(old_futa_loop, new_futa_loop, 1)

    old_wife_loop = '''for (var _wi = 0; _wi < array_length(_wife_names); _wi++)
{
    var _file = _wife_names[_wi];
    if (_wife_manifest || tc_dir_exists(_wd + "/custom_wives/" + _file))'''

    new_wife_loop = '''for (var _wi = 0; _wi < array_length(_wife_names); _wi++)
{
    var _file = _wife_names[_wi];
    var _full_path = _is_mobile ? ("custom_wives/" + _file) : (_wd + "/custom_wives/" + _file);
    if (_is_mobile && _wife_manifest)
    {
        custom_wife_sprite_loaded = true;
        ds_list_add(custom_wives_folder, _full_path);
        ds_list_add(wife_selector_names, _file);
        ds_list_add(wife_selector_has_cowgirl, true);
        ds_list_add(wife_selector_portraits, -1);
    }
    else if (_wife_manifest || tc_dir_exists(_wd + "/custom_wives/" + _file))'''

    if old_wife_loop in code:
        code = code.replace(old_wife_loop, new_wife_loop, 1)

    # 5. Bypass recursive phone_mods BFS directory scanning on launch
    old_pm_scan = '''if (os_type == os_android || os_type == os_ios)
{
    var _pm_save = game_save_id;'''

    new_pm_scan = '''if (false && (os_type == os_android || os_type == os_ios))
{
    var _pm_save = game_save_id;'''

    if old_pm_scan in code:
        code = code.replace(old_pm_scan, new_pm_scan, 1)
        LOGGER.log("Create_0: Injected instant manifest indexing and bypassed ANR startup hangs.", prefix="[+]")

    # Standardize custom wife/partner xray origins & resizers against base models (160x168, origin 80, 84)
    old_legacy_xray_read = '''        xray_origin_x = ini_read_real("xray", "origin_x", sprite_origin_x);
        xray_origin_y = ini_read_real("xray", "origin_y", sprite_origin_y);'''
    new_legacy_xray_read = '''        var _def_xo = ini_read_real("sprite", "xray_x", ini_read_real("xray", "origin_x", 80));
        var _def_yo = ini_read_real("sprite", "xray_y", ini_read_real("xray", "origin_y", 84));
        if (_def_xo > 120 || _def_xo < 40) _def_xo = 80;
        if (_def_yo > 120 || _def_yo < 40) _def_yo = 84;
        xray_origin_x = _def_xo;
        xray_origin_y = _def_yo;'''
    if old_legacy_xray_read in code:
        code = code.replace(old_legacy_xray_read, new_legacy_xray_read, 1)

    old_legacy_xray_add = 'legacy_custom_wife_xray = sprite_add(f_xray, 4, false, false, xray_origin_x, xray_origin_y);'
    new_legacy_xray_add = '''legacy_custom_wife_xray = sprite_add(f_xray, 4, false, false, xray_origin_x, xray_origin_y);
        var _lcwx_w = sprite_get_width(legacy_custom_wife_xray);
        if (_lcwx_w > 0 && _lcwx_w != 160)
        {
            var _lcwx_sc = 160 / _lcwx_w;
            sprite_set_offset(legacy_custom_wife_xray, xray_origin_x / _lcwx_sc, xray_origin_y / _lcwx_sc);
        }'''
    if old_legacy_xray_add in code:
        code = code.replace(old_legacy_xray_add, new_legacy_xray_add, 1)

    old_custom_wife_xray = 'custom_wife_xray = sprite_add(file_check, 3, false, false, sprite_origin_x, sprite_origin_y);'
    new_custom_wife_xray = '''var _cwx_ox = ini_read_real("sprite", "xray_x", ini_read_real("xray", "origin_x", 80));
        var _cwx_oy = ini_read_real("sprite", "xray_y", ini_read_real("xray", "origin_y", 84));
        if (_cwx_ox > 120 || _cwx_ox < 40) _cwx_ox = 80;
        if (_cwx_oy > 120 || _cwx_oy < 40) _cwx_oy = 84;
        custom_wife_xray = sprite_add(file_check, 3, false, false, _cwx_ox, _cwx_oy);
        var _cwx_w = sprite_get_width(custom_wife_xray);
        if (_cwx_w > 0 && _cwx_w != 160)
        {
            var _cwx_sc = 160 / _cwx_w;
            sprite_set_offset(custom_wife_xray, _cwx_ox / _cwx_sc, _cwx_oy / _cwx_sc);
        }'''
    if old_custom_wife_xray in code:
        code = code.replace(old_custom_wife_xray, new_custom_wife_xray, 1)

    # Partner (Futa) X-ray resizer & origin scaling
    old_partner_xray_add = 'custom_xray = sprite_add(f_xray, 18, false, false, 80, (custom_xray_offset_y > 0) ? (84 - custom_xray_offset_y) : (84 + custom_xray_offset_y));'
    new_partner_xray_add = '''custom_xray = sprite_add(f_xray, 18, false, false, 80, (custom_xray_offset_y > 0) ? (84 - custom_xray_offset_y) : (84 + custom_xray_offset_y));
        var _px_w = sprite_get_width(custom_xray);
        if (_px_w > 0 && _px_w != 160)
        {
            var _px_sc = 160 / _px_w;
            var _px_yoff = (custom_xray_offset_y > 0) ? (84 - custom_xray_offset_y) : (84 + custom_xray_offset_y);
            sprite_set_offset(custom_xray, 80 / _px_sc, _px_yoff / _px_sc);
        }'''
    if old_partner_xray_add in code:
        code = code.replace(old_partner_xray_add, new_partner_xray_add, 1)

    old_legacy_futa_xray_add = 'legacy_custom_xray = sprite_add(f_xray, 3, false, false, 80, 84);'
    new_legacy_futa_xray_add = '''legacy_custom_xray = sprite_add(f_xray, 3, false, false, 80, 84);
        var _lfx_w = sprite_get_width(legacy_custom_xray);
        if (_lfx_w > 0 && _lfx_w != 160)
        {
            var _lfx_sc = 160 / _lfx_w;
            sprite_set_offset(legacy_custom_xray, 80 / _lfx_sc, 84 / _lfx_sc);
        }'''
    if old_legacy_futa_xray_add in code:
        code = code.replace(old_legacy_futa_xray_add, new_legacy_futa_xray_add, 1)
    old_wr = "else if (custom_wife_sprite_loaded == true && irandom(4) == 0)"
    new_wr = "else if (custom_wife_sprite_loaded == true && irandom(4) == 0 && title == false)"
    if old_wr in code:
        code = code.replace(old_wr, new_wr, 1)
        LOGGER.log("Create_0: Added title == false guard to custom wife randomizer on startup.", prefix="[+]")

    old_fb = '''function func_wife_portrait_body(arg0)
{
    var return_port = sFutaPortrait1;
    switch (arg0)
    {
        case sWifeMatingPress:
            return_port = sFutaPortrait1;
            break;
        case sWifeMatingPressDevil:
            return_port = sFutaPortraitDevil;
            break;
        case sWifeMatingPressSlime:
            return_port = sFutaPortraitSlime;
            break;
        case sWifeMatingPressAndroid:
            return_port = sFutaPortraitAndroid;
            break;
        case sWifeMatingPressFurry:
            return_port = sFutaPortraitFurry;
            break;
        case custom_wife_mating_press:
            return_port = custom_wife_portrait;
            break;
    }
    return return_port;
}'''
    new_fb = '''function func_wife_portrait_body(arg0)
{
    var return_port = sFutaPortrait1;
    switch (arg0)
    {
        case sWifeMatingPress:
            return_port = sFutaPortrait1;
            break;
        case sWifeMatingPressDevil:
            return_port = sFutaPortraitDevil;
            break;
        case sWifeMatingPressSlime:
            return_port = sFutaPortraitSlime;
            break;
        case sWifeMatingPressAndroid:
            return_port = sFutaPortraitAndroid;
            break;
        case sWifeMatingPressFurry:
            return_port = sFutaPortraitFurry;
            break;
        case custom_wife_mating_press:
            return_port = (sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1) ? custom_wife_portrait : sFutaPortrait1;
            break;
        case legacy_custom_wife_mating_press:
            return_port = (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1) ? legacy_custom_wife_portrait : sFutaPortrait1;
            break;
    }
    return (sprite_exists(return_port) && return_port != -1) ? return_port : sFutaPortrait1;
}'''
    if old_fb in code:
        code = code.replace(old_fb, new_fb, 1)
        LOGGER.log("Create_0: Fortified func_wife_portrait_body with legacy spouse support and non-negative sprite guarantees.", prefix="[+]")

    old_facfs = '''function func_apply_custom_futa_stats()
{
    if (is_legacy_custom)
    {
        top_sprite = legacy_custom_mating_press;
        penis_sprite = legacy_custom_mating_press;
        hair_sprite = legacy_custom_mating_press;
        face_sprite = legacy_custom_portrait;
        bangs_sprite = legacy_custom_portrait;'''
    new_facfs = '''function func_apply_custom_futa_stats()
{
    if (is_legacy_custom)
    {
        top_sprite = legacy_custom_mating_press;
        penis_sprite = legacy_custom_mating_press;
        hair_sprite = legacy_custom_mating_press;
        face_sprite = legacy_custom_portrait;
        bangs_sprite = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;'''
    if old_facfs in code:
        code = code.replace(old_facfs, new_facfs, 1)

    # In func_get_portrait, ensure non-negative return for legacy_custom_mating_press
    old_fgp_case = '''                case legacy_custom_mating_press:
                    return_port = legacy_custom_portrait;
                    break;'''
    new_fgp_case = '''                case legacy_custom_mating_press:
                    return_port = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
                    break;'''
    if old_fgp_case in code:
        code = code.replace(old_fgp_case, new_fgp_case, 1)

    # In func_load_custom_futa, dynamic frame count fallback for legacy_custom_portrait
    old_flcf_port = '''            f_port = string(arg0) + "/custom_portrait.png";
            if (file_exists(f_port))
            {
                if (sprite_exists(legacy_custom_portrait))
                {
                    sprite_delete(legacy_custom_portrait);
                }
                legacy_custom_portrait = sprite_add(f_port, 10, false, false, portrait_origin_x, portrait_origin_y);
            }
            else
            {
                legacy_custom_portrait = -1;
            }'''

    new_flcf_port = '''            f_port = string(arg0) + "/custom_portrait.png";
            if (file_exists(f_port))
            {
                if (sprite_exists(legacy_custom_portrait))
                {
                    sprite_delete(legacy_custom_portrait);
                }
                legacy_custom_portrait = sprite_add(f_port, 10, false, false, portrait_origin_x, portrait_origin_y);
                if (!sprite_exists(legacy_custom_portrait) || legacy_custom_portrait == -1)
                {
                    var _test_p = sprite_add(f_port, 1, false, false, 0, 0);
                    if (sprite_exists(_test_p) && _test_p != -1)
                    {
                        var _pw = sprite_get_width(_test_p);
                        var _ph = sprite_get_height(_test_p);
                        sprite_delete(_test_p);
                        var _p_frames = max(1, round(_pw / _ph));
                        legacy_custom_portrait = sprite_add(f_port, _p_frames, false, false, portrait_origin_x, portrait_origin_y);
                    }
                }
            }'''
    if old_flcf_port in code:
        code = code.replace(old_flcf_port, new_flcf_port, 1)

    old_fgpb_ret = '''            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit3)
            {
                return_port = sFutaPortrait3;
            }
            break;
    }
    return return_port;
}'''
    new_fgpb_ret = '''            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit3)
            {
                return_port = sFutaPortrait3;
            }
            break;
    }
    if (!sprite_exists(return_port) || return_port <= 0)
    {
        return_port = sFutaPortrait1;
    }
    return return_port;
}'''
    if old_fgpb_ret in code:
        code = code.replace(old_fgpb_ret, new_fgpb_ret, 1)

    # Universal Futa Detection and Direct Native Loaders (removes file_exists APK blockers)
    old_flcf_header = '''function func_load_custom_futa(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    is_legacy_custom = false;
    if (file_exists(string(arg0) + "/custom_mating_press.png"))'''

    new_flcf_header = '''function func_load_custom_futa(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    is_legacy_custom = false;
    if (file_exists(string(arg0) + "/custom_mating_press.png") || file_exists(string(arg0) + "/custom_data.futa") || (os_type == os_android || os_type == os_ios))'''

    if old_flcf_header in code:
        code = code.replace(old_flcf_header, new_flcf_header, 1)

    old_f_mate_block = '''            f_mate = string(arg0) + "/custom_mating_press.png";
            if (file_exists(f_mate))
            {
                if (sprite_exists(legacy_custom_mating_press))
                {
                    sprite_delete(legacy_custom_mating_press);
                }
                legacy_custom_mating_press = sprite_add(f_mate, 9, false, false, mp_origin_x, mp_origin_y);
            }'''

    new_f_mate_block = '''            f_mate = string(arg0) + "/custom_mating_press.png";
            var _test_m = sprite_add(f_mate, 1, false, false, 0, 0);
            var _frame_w = (sprite_origin_x > 0) ? (sprite_origin_x * 2) : 160;
            var _mf = 9;
            if (sprite_exists(_test_m) && _test_m != -1)
            {
                var _mw = sprite_get_width(_test_m);
                sprite_delete(_test_m);
                _mf = max(1, round(_mw / _frame_w));
            }
            var _temp_mate = sprite_add(f_mate, _mf, false, false, sprite_origin_x, sprite_origin_y);
            if (sprite_exists(_temp_mate) && _temp_mate != -1)
            {
                is_legacy_custom = true;
                if (sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press > 189)
                {
                    sprite_delete(legacy_custom_mating_press);
                }
                legacy_custom_mating_press = _temp_mate;
                custom_mating_press_scale = 160 / _frame_w;
                sprite_set_offset(legacy_custom_mating_press, sprite_origin_x, sprite_origin_y);
            }'''

    if old_f_mate_block in code:
        code = code.replace(old_f_mate_block, new_f_mate_block, 1)

    old_f_condom_block = '''            f_condom = string(arg0) + "/custom_condom.png";
            if (file_exists(f_condom))
            {
                if (sprite_exists(legacy_custom_condom))
                {
                    sprite_delete(legacy_custom_condom);
                }
                legacy_custom_condom = sprite_add(f_condom, 2, false, false, sprite_origin_x, sprite_origin_y);
            }'''

    new_f_condom_block = '''            f_condom = string(arg0) + "/custom_condom.png";
            var _temp_cdm = sprite_add(f_condom, 2, false, false, sprite_origin_x, sprite_origin_y);
            if (sprite_exists(_temp_cdm) && _temp_cdm != -1)
            {
                if (sprite_exists(legacy_custom_condom))
                {
                    sprite_delete(legacy_custom_condom);
                }
                legacy_custom_condom = _temp_cdm;
            }'''

    if old_f_condom_block in code:
        code = code.replace(old_f_condom_block, new_f_condom_block, 1)

    old_spouse_load = '''        f_mate = string(arg0) + "/custom_mating_press.png";
        if (file_exists(f_mate))
        {
            if (sprite_exists(legacy_custom_wife_mating_press))
            {
                sprite_delete(legacy_custom_wife_mating_press);
            }
            legacy_custom_wife_mating_press = sprite_add(f_mate, 4, false, false, mp_origin_x, mp_origin_y);
        }'''
    new_spouse_load = '''        f_mate = string(arg0) + "/custom_mating_press.png";
        var _test_w = sprite_add(f_mate, 1, false, false, 0, 0);
        var _w_frame_w = (sprite_origin_x > 0) ? (sprite_origin_x * 2) : 160;
        var _w_frames = 4;
        if (sprite_exists(_test_w) && _test_w != -1)
        {
            var _w_total_w = sprite_get_width(_test_w);
            sprite_delete(_test_w);
            _w_frames = max(1, round(_w_total_w / _w_frame_w));
        }
        if (sprite_exists(legacy_custom_wife_mating_press))
        {
            sprite_delete(legacy_custom_wife_mating_press);
        }
        legacy_custom_wife_mating_press = sprite_add(f_mate, _w_frames, false, false, sprite_origin_x, sprite_origin_y);
        custom_wife_mating_press_scale = 160 / _w_frame_w;
        sprite_set_offset(legacy_custom_wife_mating_press, sprite_origin_x, sprite_origin_y);'''
    if old_spouse_load in code:
        code = code.replace(old_spouse_load, new_spouse_load, 1)

    # Safe sprite_delete protection: NEVER delete built-in game assets (<= 189)
    old_port_del = '''if (sprite_exists(legacy_custom_portrait))
                {
                    sprite_delete(legacy_custom_portrait);
                }'''
    new_port_del = '''if (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait > 189)
                {
                    sprite_delete(legacy_custom_portrait);
                }'''
    if old_port_del in code:
        code = code.replace(old_port_del, new_port_del)

    old_wport_del = '''if (sprite_exists(legacy_custom_wife_portrait))
            {
                sprite_delete(legacy_custom_wife_portrait);
            }'''
    new_wport_del = '''if (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait > 189)
            {
                sprite_delete(legacy_custom_wife_portrait);
            }'''
    if old_wport_del in code:
        code = code.replace(old_wport_del, new_wport_del)

    # Universal Futa detection and direct loader
    old_futa_hdr = '''function func_load_custom_futa(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    is_legacy_custom = false;
    if (file_exists(string(arg0) + "/custom_mating_press.png"))'''
    new_futa_hdr = '''function func_load_custom_futa(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    is_legacy_custom = false;
    if (file_exists(string(arg0) + "/custom_mating_press.png") || file_exists(string(arg0) + "/custom_data.futa") || (os_type == os_android || os_type == os_ios))'''
    if old_futa_hdr in code:
        code = code.replace(old_futa_hdr, new_futa_hdr, 1)


    # Initialize Favorites Maps in Create_0 cleanly without freezing
    favs_init_code = """
global.favs_futa = ds_map_create();
global.favs_wife = ds_map_create();
selector_favs_only = false;

// Load persisted favorites and enhancement settings from session save component
if (file_exists("setting_data.sav"))
{
    ini_open("setting_data.sav");
    for (var _fi = 0; _fi < ds_list_size(custom_futas_folder); _fi++)
    {
        var _fn = filename_name(ds_list_find_value(custom_futas_folder, _fi));
        if (ini_read_real("favs_futa", _fn, 0) == 1)
        {
            ds_map_add(global.favs_futa, _fn, 1);
        }
    }
    for (var _wi = 0; _wi < ds_list_size(custom_wives_folder); _wi++)
    {
        var _wn = filename_name(ds_list_find_value(custom_wives_folder, _wi));
        if (ini_read_real("favs_wife", _wn, 0) == 1)
        {
            ds_map_add(global.favs_wife, _wn, 1);
        }
    }
    if (ini_key_exists("options", "hyper_sizes")) tc_hyper = bool(ini_read_real("options", "hyper_sizes", false));
    if (ini_key_exists("options", "selector_favs_only")) selector_favs_only = bool(ini_read_real("options", "selector_favs_only", false));
    ini_close();
}
"""
    code = code + favs_init_code

    old_bf = """function func_get_portrait_boobs(arg0, arg1)
{
    var return_port = sFutaPortrait1;
    switch (arg1)
    {
        case 0:
            if (outfit_toggle == false)
            {
                switch (arg0)
                {
                    case sFutaMatingPress:
                        return_port = sFutaPortrait1;
                        break;
                    case sFutaMatingPressDevil:
                        return_port = sFutaPortraitDevil;
                        break;
                    case sFutaMatingPressSlime:
                        return_port = sFutaPortraitSlime;
                        break;
                    case sFutaMatingPressAndroid:
                        return_port = sFutaPortraitAndroid;
                        break;
                    case sFutaMatingPressAlien:
                        return_port = sFutaPortraitAlien;
                        break;
                    case sFutaMatingPressClown:
                        return_port = sFutaPortraitClown;
                        break;
                    case sFutaMatingBunny:
                        return_port = sFutaPortraitBunny;
                        break;
                    case sFutaMatingFurry:
                        return_port = sFutaPortraitFurry;
                        break;
                    case custom_mating_press:
                        return_port = custom_portrait;
                        break;
                    case legacy_custom_mating_press:
                        return_port = legacy_custom_portrait;
                        break;
                }
            }"""
    new_bf = """function func_get_portrait_boobs(arg0, arg1)
{
    var return_port = sFutaPortrait1;
    switch (arg1)
    {
        case 0:
            if (outfit_toggle == false)
            {
                switch (arg0)
                {
                    case sFutaMatingPress:
                        return_port = sFutaPortrait1;
                        break;
                    case sFutaMatingPressDevil:
                        return_port = sFutaPortraitDevil;
                        break;
                    case sFutaMatingPressSlime:
                        return_port = sFutaPortraitSlime;
                        break;
                    case sFutaMatingPressAndroid:
                        return_port = sFutaPortraitAndroid;
                        break;
                    case sFutaMatingPressAlien:
                        return_port = sFutaPortraitAlien;
                        break;
                    case sFutaMatingPressClown:
                        return_port = sFutaPortraitClown;
                        break;
                    case sFutaMatingBunny:
                        return_port = sFutaPortraitBunny;
                        break;
                    case sFutaMatingFurry:
                        return_port = sFutaPortraitFurry;
                        break;
                    case custom_mating_press:
                        return_port = (sprite_exists(custom_portrait) && custom_portrait != -1) ? custom_portrait : sFutaPortrait1;
                        break;
                    case legacy_custom_mating_press:
                        return_port = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
                        break;
                }
            }"""
    if old_bf in code:
        code = code.replace(old_bf, new_bf, 1)

    old_bf_ret = """                    case custom_wife_mating_press:
                        return_port = custom_wife_portrait;
                        break;
                }
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit1)
            {
                return_port = sFutaPortrait2;
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit2)
            {
                return_port = sFutaPortrait4;
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit3)
            {
                return_port = sFutaPortrait3;
            }
            break;
    }
    return return_port;"""

    new_bf_ret = """                    case custom_wife_mating_press:
                        return_port = (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1) ? legacy_custom_wife_portrait : ((sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1) ? custom_wife_portrait : sFutaPortrait1);
                        break;
                }
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit1)
            {
                return_port = sFutaPortrait2;
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit2)
            {
                return_port = sFutaPortrait4;
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit3)
            {
                return_port = sFutaPortrait3;
            }
            break;
    }
    return (sprite_exists(return_port) && return_port != -1) ? return_port : sFutaPortrait1;"""
    if old_bf_ret in code:
        code = code.replace(old_bf_ret, new_bf_ret, 1)

    old_clf = """                    case custom_mating_press:
                        return_port = custom_portrait;
                        break;
                    case legacy_custom_mating_press:
                        return_port = legacy_custom_portrait;
                        break;"""
    new_clf = """                    case custom_mating_press:
                        return_port = (sprite_exists(custom_portrait) && custom_portrait != -1) ? custom_portrait : sFutaPortrait1;
                        break;
                    case legacy_custom_mating_press:
                        return_port = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
                        break;"""
    if old_clf in code: code = code.replace(old_clf, new_clf, 1)

    old_clw = """                    case custom_wife_mating_press:
                        return_port = custom_wife_portrait;
                        break;"""
    new_clw = """                    case custom_wife_mating_press:
                        return_port = (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1) ? legacy_custom_wife_portrait : ((sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1) ? custom_wife_portrait : sFutaPortrait1);
                        break;"""
    if old_clw in code: code = code.replace(old_clw, new_clw, 1)

    old_ret_boobs = "    return return_port;\n}\n\nfunction func_get_alt_boob_sprite"
    new_ret_boobs = "    return (sprite_exists(return_port) && return_port != -1) ? return_port : sFutaPortrait1;\n}\n\nfunction func_get_alt_boob_sprite"
    if old_ret_boobs in code: code = code.replace(old_ret_boobs, new_ret_boobs, 1)


    if enable_toy_telemetry:
        bp_create = """
buttplug_socket = network_create_socket(network_socket_udp);
buttplug_buffer = buffer_create(256, buffer_grow, 1);
buttplug_last_send = 0;
buttplug_port = 45735;
"""
        code = code + bp_create
        LOGGER.log("Create_0: Enabled ToyBridge UDP toy telemetry socket on port 45735.", prefix="[+]")

    # Initialize xray_origin_x and xray_origin_y in func_load_custom_spouse to prevent unset variable crash
    code = code.replace('    var xray_origin_x, xray_origin_y;', '    var xray_origin_x = 80;\n    var xray_origin_y = 84;', 1)
    code = code.replace(
        'if (file_exists(string(arg0) + "/custom_data.spouse"))',
        'if (file_exists(string(arg0) + "/custom_data.spouse") || file_exists(string(arg0) + "/custom_data.wife") || (os_type == os_android || os_type == os_ios))',
        1
    )

    LOGGER.log("Create_0: Standardized all partner & spouse xray assets to base reference (160x168, 80, 84).", prefix="[+]")

    return code

def patch_step_code(code):
    """Patches Step_0 to enable gameplay hovers/touch inputs while panels are open and remove Rickroll."""
    old_step_hovers = '''if (title == false && start_timer < 1 && futa_selector_open == false && newlover_menu_toggle == false && newwife_menu_toggle == false)
{
    hover_portrait = point_in_rectangle(mouse_x, mouse_y, 10, room_height - 128, 87, room_height - 64);
    kiss_box = point_in_rectangle(mouse_x, mouse_y, (portrait_x - 6) + custom_kiss_x_offset, ((portrait_y + (top_breath * 64)) - 3) + custom_kiss_y_offset, portrait_x + 6 + custom_kiss_x_offset, portrait_y + (top_breath * 64) + 3 + custom_kiss_y_offset);
    boob_box = point_in_rectangle(mouse_x, mouse_y, 10 + custom_boob_x_offset, (room_height - 58) + custom_boob_y_offset, 87 + custom_boob_x_offset, (room_height - 25) + custom_boob_y_offset);
    headpat_press = point_in_rectangle(mouse_x, mouse_y, (portrait_x - 32) + custom_headpat_x_offset, (portrait_y - 56) + custom_headpat_y_offset, portrait_x + 32 + custom_headpat_x_offset, (portrait_y - 24) + custom_headpat_y_offset);
}
else if (futa_selector_open == true || newlover_menu_toggle == true || newwife_menu_toggle == true)
{
    hover_portrait = false;
    kiss_box = false;
    boob_box = false;
    headpat_press = false;
}'''

    new_step_hovers = '''if (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)
{
    hover_portrait = point_in_rectangle(mouse_x, mouse_y, 10, room_height - 128, 87, room_height - 64);
    kiss_box = point_in_rectangle(mouse_x, mouse_y, (portrait_x - 6) + custom_kiss_x_offset, ((portrait_y + (top_breath * 64)) - 3) + custom_kiss_y_offset, portrait_x + 6 + custom_kiss_x_offset, portrait_y + (top_breath * 64) + 3 + custom_kiss_y_offset);
    boob_box = point_in_rectangle(mouse_x, mouse_y, 10 + custom_boob_x_offset, (room_height - 58) + custom_boob_y_offset, 87 + custom_boob_x_offset, (room_height - 25) + custom_boob_y_offset);
    headpat_press = point_in_rectangle(mouse_x, mouse_y, (portrait_x - 32) + custom_headpat_x_offset, (portrait_y - 56) + custom_headpat_y_offset, portrait_x + 32 + custom_headpat_x_offset, (portrait_y - 24) + custom_headpat_y_offset);
}
else if (futa_selector_open == true)
{
    hover_portrait = false;
    kiss_box = false;
    boob_box = false;
    headpat_press = false;
}'''

    if old_step_hovers in code:
        code = code.replace(old_step_hovers, new_step_hovers, 1)

    old_step_headpat = 'if (title == false && start_timer < 1 && futa_selector_open == false && newlover_menu_toggle == false && newwife_menu_toggle == false)'
    new_step_headpat = 'if (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)'

    if old_step_headpat in code:
        code = code.replace(old_step_headpat, new_step_headpat, 1)
        LOGGER.log("Step_0: Enabled all touch inputs and hovers with open panels.", prefix="[+]")

    pattern = r'if\s*\(\s*variable_global_exists\("rg_chosen_pill"\)\s*&&\s*global\.rg_chosen_pill\s*==\s*"Rick_Astley"\s*\)\s*\{.*?\n\}'
    if re.search(pattern, code, flags=re.DOTALL):
        code = re.sub(pattern, '// Rickroll easter egg neutralized by patcher', code, flags=re.DOTALL)
        LOGGER.log("Step_0: Neutralized Rickroll fake crash.", prefix="[+]")

    return code

def apply_hyper_sizes(code: str) -> str:
    """Optionally adds HYPER: ON/OFF toggle to SIZES options page (ToyBridge 1.5.2)."""
    hyper_anchor = 'comment = "lover sizes";'
    hyper_toggle = """var _tc_hx = options_x + 58;
var _tc_hy = options_y + 12;
var _tc_hh = point_in_rectangle(mouse_x, mouse_y, _tc_hx - 28, _tc_hy + 1, _tc_hx + 28, _tc_hy + 9);
draw_sprite_ext(sButtonBack, 1, _tc_hx, _tc_hy + 5, 4.2, 1, 0, tc_hyper ? 65535 : 16777215, 0.5 + (0.5 * _tc_hh) + (0.5 * tc_hyper));
draw_set_halign(1);
draw_set_valign(0);
draw_text_ext_transformed(_tc_hx, _tc_hy, tc_hyper ? "HYPER: ON" : "HYPER: OFF", 12, 100, 0.5, 0.5, 0);
if (mouse_check_button_pressed(1) && _tc_hh && title == false)
{
    tc_hyper = !tc_hyper;
    if (tc_hyper)
    {
        var _tc_f = file_text_open_write(game_save_id + "hyper_sizes.on");
        file_text_write_string(_tc_f, "1");
        file_text_close(_tc_f);
    }
    else
    {
        file_delete(game_save_id + "hyper_sizes.on");
    }
}
"""
    if hyper_anchor in code and "_tc_hx" not in code:
        code = code.replace(hyper_anchor, hyper_anchor + "\n" + hyper_toggle, 1)
        LOGGER.log("Draw_0: Added ToyBridge SIZES page HYPER toggle (2.5x range).", prefix="[+]")
    return code

def patch_draw_code(code, enable_toy_telemetry=False, opts=None):
    if opts is None: opts = {}
    code = apply_hyper_sizes(code)

    """Patches Draw_0 with crash prevention, unlinked panels, gameplay unlocks, and mobile overlay."""

    if "Master Modal Supremacy" not in code:
        code = '''// Master Modal Supremacy & Total Input Isolation Shield
if (variable_instance_exists(id, "futa_selector_open") && futa_selector_open)
{
    pill_menu_toggle = false;
    newlover_menu_toggle = false;
    newwife_menu_toggle = false;
    options_toggle = false;
    actions_menu_toggle = false;
    in_action_menu = false;
    radio_toggle = false;
    cs_toggle = false;
    position_menu_toggle = false;
    background_menu_toggle = false;
    radial_menu_open = false;
    radial_sub_menu = "";
    mob_expanded = false;
    penis_grab = false;
    kiss_box = false;
    headpat_press = false;
    futa_boob_press = false;
    wife_boob_press = false;
}
else if (variable_instance_exists(id, "mob_expanded") && mob_expanded)
{
    pill_menu_toggle = false;
    newlover_menu_toggle = false;
    newwife_menu_toggle = false;
    options_toggle = false;
    actions_menu_toggle = false;
    in_action_menu = false;
    radio_toggle = false;
    cs_toggle = false;
    position_menu_toggle = false;
    background_menu_toggle = false;
    radial_menu_open = false;
    radial_sub_menu = "";
    penis_grab = false;
    kiss_box = false;
    headpat_press = false;
    futa_boob_press = false;
    wife_boob_press = false;
}
''' + code
        LOGGER.log("Draw_0: Injected Master Modal Supremacy Shield.", prefix="[+]")
    
    if 'if (!variable_instance_exists(id, "boob_box")) boob_box = false;' not in code:
        code = 'if (!variable_instance_exists(id, "boob_box")) boob_box = false;\n' + code
        LOGGER.log("Draw_0: Initialized boob_box safety check upfront.", prefix="[+]")

    code = code.replace(
        "if (manual_mode == 0 && mouse_check_button_pressed(mb_right) && !hover_portrait && !boob_box && title == false)",
        "if (manual_mode == 0 && mouse_check_button_pressed(mb_right) && !hover_portrait && (!variable_instance_exists(id, \"boob_box\") || !boob_box) && title == false)"
    )
    code = code.replace(
        "else if (mouse_check_button_pressed(mb_right) && !hover_portrait && !boob_box && manual_mode == 0)",
        "else if (mouse_check_button_pressed(mb_right) && !hover_portrait && (!variable_instance_exists(id, \"boob_box\") || !boob_box) && manual_mode == 0)"
    )

    old_mob_init = '''if (!variable_instance_exists(id, "mob_touching_menu"))
{
    mob_touching_menu = false;
}
if (!variable_instance_exists(id, "mob_drag_last_y"))
{
    mob_drag_last_y = 0;
}
if (!variable_instance_exists(id, "mob_init"))
{
    mob_init = true;
    mob_expanded = false;
    mob_hitbox_active = false;
    mob_release_key = -1;
    mob_scroll_y = 0;
    mob_drag_start_y = 0;
    mob_drag_last_y = 0;
    mob_is_dragging = false;
    mob_touching_menu = false;
    mob_lp_timer = 0;
    mob_lp_start_x = 0;
    mob_lp_start_y = 0;
}'''

    new_mob_init = '''if (!variable_instance_exists(id, "mob_touching_menu"))
{
    mob_touching_menu = false;
}
if (!variable_instance_exists(id, "mob_drag_last_y"))
{
    mob_drag_last_y = 0;
}
if (!variable_instance_exists(id, "mob_init"))
{
    mob_init = true;
    mob_expanded = false;
    mob_hitbox_active = false;
    mob_release_key = -1;
    mob_scroll_y = 0;
    mob_drag_start_y = 0;
    mob_drag_last_y = 0;
    mob_is_dragging = false;
    mob_touching_menu = false;
    mob_lp_timer = 0;
    mob_lp_start_x = 0;
    mob_lp_start_y = 0;

    // Keep phone display awake while game is open
    if (os_type == os_android || os_type == os_ios)
    {
        os_powersave_enable(false);
    }
}

// Auto-save basic settings when closing options menu
if (!variable_instance_exists(id, "_last_opt_tog"))
    _last_opt_tog = options_toggle;
if (_last_opt_tog == true && options_toggle == false)
    func_save_settings();
_last_opt_tog = options_toggle;

// Exit all right-side menus when entering manual mode
if (!variable_instance_exists(id, "_prev_manual_mode"))
    _prev_manual_mode = manual_mode;
if (_prev_manual_mode == 0 && manual_mode > 0)
{
    background_menu_toggle = false;
    position_menu_toggle = false;
    pill_menu_toggle = false;
    dialogue_menu_toggle = false;
    radio_toggle = false;
    tab_quicknav_open = false;
    options_toggle = false;
    actions_menu_toggle = false;
    color_picker_active = false;
    futa_selector_open = false;
    if (os_type == os_android || os_type == os_ios)
        keyboard_virtual_hide();
    selector_search_focused = false;
}
_prev_manual_mode = manual_mode;'''

    if old_mob_init in code:
        code = code.replace(old_mob_init, new_mob_init, 1)
        LOGGER.log("Draw_0: Injected screen wake-lock, auto-save, and manual mode right-side menus exit check.", prefix="[+]")

    if "options_page = qi; func_save_settings();" not in code:
        code = code.replace("options_page = qi;", "options_page = qi; func_save_settings();")
        code = code.replace("options_page = _next_page;", "options_page = _next_page; func_save_settings();")

    if "continuous_toggle = !continuous_toggle; func_save_settings();" not in code:
        code = code.replace("continuous_toggle = !continuous_toggle;", "continuous_toggle = !continuous_toggle; func_save_settings();")

    # Standardize runtime anatomy_sprite and xray_sprite resizers against base reference
    old_anat = "var anatomy_sprite = (wife_xray == -1) ? xray_sprite : wife_xray;"
    new_anat = '''var anatomy_sprite = (wife_xray == -1) ? xray_sprite : wife_xray;
    if (sprite_exists(anatomy_sprite))
    {
        var _aw = sprite_get_width(anatomy_sprite);
        if (_aw > 0 && _aw != 160)
        {
            var _asc = 160 / _aw;
            sprite_set_offset(anatomy_sprite, 80 / _asc, 84 / _asc);
        }
        else
        {
            var _ax_off = sprite_get_xoffset(anatomy_sprite);
            var _ay_off = sprite_get_yoffset(anatomy_sprite);
            if (_ax_off > 120 || _ax_off < 40 || _ay_off > 120 || _ay_off < 40)
                sprite_set_offset(anatomy_sprite, 80, 84);
        }
    }
    if (sprite_exists(xray_sprite))
    {
        var _xw = sprite_get_width(xray_sprite);
        if (_xw > 0 && _xw != 160)
        {
            var _xsc = 160 / _xw;
            sprite_set_offset(xray_sprite, 80 / _xsc, 84 / _xsc);
        }
        else
        {
            var _xx_off = sprite_get_xoffset(xray_sprite);
            var _xy_off = sprite_get_yoffset(xray_sprite);
            if (_xx_off > 120 || _xx_off < 40 || _xy_off > 120 || _xy_off < 40)
                sprite_set_offset(xray_sprite, 80, 84);
        }
    }'''
    if old_anat in code and "sprite_get_xoffset(anatomy_sprite)" not in code:
        code = code.replace(old_anat, new_anat, 1)
        LOGGER.log("Draw_0: Standardized runtime anatomy and partner xray resizers to base (80, 84).", prefix="[+]")

    # Crash Prevention: Guards for custom_portrait draws (cures requested -1 crash)
    old_cp_boobs = 'else if (top_sprite == custom_mating_press)\n    {\n        draw_sprite_ext(custom_portrait, 2, portrait_x, _boob_y, _boob_xscale * custom_portrait_scale, _boob_yscale * custom_portrait_scale, 0, top_skin, 1);\n    }'
    new_cp_boobs = 'else if (top_sprite == custom_mating_press && sprite_exists(custom_portrait) && custom_portrait != -1)\n    {\n        draw_sprite_ext(custom_portrait, 2, portrait_x, _boob_y, _boob_xscale * custom_portrait_scale, _boob_yscale * custom_portrait_scale, 0, top_skin, 1);\n    }'
    if old_cp_boobs in code:
        code = code.replace(old_cp_boobs, new_cp_boobs, 1)

    old_cp_blush = 'if (top_sprite == custom_mating_press)\n    {\n        draw_sprite_ext(custom_portrait, 14 + blush_id, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, c_white, 1);\n    }'
    new_cp_blush = 'if (top_sprite == custom_mating_press && sprite_exists(custom_portrait) && custom_portrait != -1)\n    {\n        draw_sprite_ext(custom_portrait, 14 + blush_id, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, c_white, 1);\n    }'
    if old_cp_blush in code:
        code = code.replace(old_cp_blush, new_cp_blush, 1)

    old_cp_mouth = 'if (top_sprite == custom_mating_press)\n    {\n        draw_sprite_ext(custom_portrait, custom_mouth_id, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);\n    }'
    new_cp_mouth = 'if (top_sprite == custom_mating_press && sprite_exists(custom_portrait) && custom_portrait != -1)\n    {\n        draw_sprite_ext(custom_portrait, custom_mouth_id, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);\n    }'
    if old_cp_mouth in code:
        code = code.replace(old_cp_mouth, new_cp_mouth, 1)

    old_cp_eye = 'draw_sprite_ext(custom_portrait, 7 + eye_id, eye_x, eye_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, c_white, 1);'
    new_cp_eye = 'if (sprite_exists(custom_portrait) && custom_portrait != -1) draw_sprite_ext(custom_portrait, 7 + eye_id, eye_x, eye_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, c_white, 1);'
    if old_cp_eye in code:
        code = code.replace(old_cp_eye, new_cp_eye, 1)
    old_lcp_boobs = 'else if (top_sprite == legacy_custom_mating_press)\n    {\n        draw_sprite_ext(legacy_custom_portrait, 2, portrait_x, _boob_y, _boob_xscale * custom_portrait_scale, _boob_yscale * custom_portrait_scale, 0, top_skin, 1);\n    }'
    new_lcp_boobs = 'else if (top_sprite == legacy_custom_mating_press && sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1)\n    {\n        draw_sprite_ext(legacy_custom_portrait, 2, portrait_x, _boob_y, _boob_xscale * custom_portrait_scale, _boob_yscale * custom_portrait_scale, 0, top_skin, 1);\n    }'
    if old_lcp_boobs in code:
        code = code.replace(old_lcp_boobs, new_lcp_boobs, 1)

    old_lcp_mouth = 'else if (top_sprite == legacy_custom_mating_press)\n    {\n        draw_sprite_ext(legacy_custom_portrait, custom_mouth_id, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);\n    }'
    new_lcp_mouth = 'else if (top_sprite == legacy_custom_mating_press && sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1)\n    {\n        draw_sprite_ext(legacy_custom_portrait, custom_mouth_id, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);\n    }'
    if old_lcp_mouth in code:
        code = code.replace(old_lcp_mouth, new_lcp_mouth, 1)

    old_lcp_eyes = 'else if (top_sprite == legacy_custom_mating_press)\n    {\n        draw_sprite_ext(legacy_custom_portrait, 7 + eye_id, eye_x, eye_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, c_white, 1);\n    }'
    new_lcp_eyes = 'else if (top_sprite == legacy_custom_mating_press && sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1)\n    {\n        draw_sprite_ext(legacy_custom_portrait, 7 + eye_id, eye_x, eye_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, c_white, 1);\n    }'
    if old_lcp_eyes in code:
        code = code.replace(old_lcp_eyes, new_lcp_eyes, 1)

        # Extra sprite existence guards for legacy_custom_portrait and bangs_sprite
    old_lcp_boob2 = '''    else if (top_sprite == legacy_custom_mating_press)
    {
        if (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) draw_sprite_ext(legacy_custom_portrait, 2, portrait_x, _boob_y, _boob_xscale * custom_portrait_scale, _boob_yscale * custom_portrait_scale, 0, top_skin, 1);
    }'''
    new_lcp_boob2 = '''    else if (top_sprite == legacy_custom_mating_press && sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1)
    {
        draw_sprite_ext(legacy_custom_portrait, 2, portrait_x, _boob_y, _boob_xscale * custom_portrait_scale, _boob_yscale * custom_portrait_scale, 0, top_skin, 1);
    }'''
    if old_lcp_boob2 in code:
        code = code.replace(old_lcp_boob2, new_lcp_boob2, 1)

    old_lcp_mouth2 = '''    else if (top_sprite == legacy_custom_mating_press)
    {
        if (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) draw_sprite_ext(legacy_custom_portrait, custom_mouth_id, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);    
    }'''
    new_lcp_mouth2 = '''    else if (top_sprite == legacy_custom_mating_press && sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1)
    {
        draw_sprite_ext(legacy_custom_portrait, custom_mouth_id, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);    
    }'''
    if old_lcp_mouth2 in code:
        code = code.replace(old_lcp_mouth2, new_lcp_mouth2, 1)

    # Safe point-of-use guards for bangs and custom portraits in Draw_0
    old_bs_6_raw = """    comment = "layer 6: side bangs";
    draw_sprite_ext(bangs_sprite, 6, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);"""
    new_bs_6_guard = """    comment = "layer 6: side bangs";
    if (sprite_exists(bangs_sprite) && bangs_sprite != -1)
    {
        draw_sprite_ext(bangs_sprite, 6, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);
    }"""
    if old_bs_6_raw in code:
        code = code.replace(old_bs_6_raw, new_bs_6_guard, 1)

    old_bs_13_raw = """    comment = "layer 13: fore bangs (mapped to vanilla index 9)";
    draw_sprite_ext(bangs_sprite, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 13 : 9, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);"""
    new_bs_13_guard = """    comment = "layer 13: fore bangs (mapped to vanilla index 9)";
    if (sprite_exists(bangs_sprite) && bangs_sprite != -1)
    {
        draw_sprite_ext(bangs_sprite, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 13 : 9, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);
    }"""
    if old_bs_13_raw in code:
        code = code.replace(old_bs_13_raw, new_bs_13_guard, 1)

    old_lpe = '''    face_x += ((face_x_set - face_x) * 0.1);
    face_y += ((face_y_set - face_y) * 0.1);
    comment = "layer 0: hair (back)";
    draw_sprite_ext(func_get_portrait(hair_sprite, 0), 0, portrait_x - face_x, (portrait_y - face_y) + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);
    comment = "layer 1: torso";
    draw_sprite_ext(func_get_portrait(top_sprite, 0), 1, portrait_x, portrait_y + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);'''
    new_lpe = '''    face_x += ((face_x_set - face_x) * 0.1);
    face_y += ((face_y_set - face_y) * 0.1);
    var _is_custom_lover = (custom_lover_toggle == true || top_sprite == legacy_custom_mating_press || top_sprite == custom_mating_press);
    var _spr_custom_lover_portrait = _is_custom_lover && (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1);
    var _spr_custom_lover_portrait_new = _is_custom_lover && (sprite_exists(custom_portrait) && custom_portrait != -1);
    var _lover_base_portrait = _spr_custom_lover_portrait ? legacy_custom_portrait : (_spr_custom_lover_portrait_new ? custom_portrait : func_get_portrait(top_sprite, 0));
    if (!sprite_exists(_lover_base_portrait) || _lover_base_portrait == -1) _lover_base_portrait = sFutaPortrait1;
    var _lover_hair_base = (sprite_exists(hair_sprite) && hair_sprite != -1) ? func_get_portrait(hair_sprite, 0) : _lover_base_portrait;
    if (!sprite_exists(_lover_hair_base) || _lover_hair_base == -1) _lover_hair_base = _lover_base_portrait;
    comment = "layer 0: hair (back)";
    draw_sprite_ext(_lover_hair_base, 0, portrait_x - face_x, (portrait_y - face_y) + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);
    comment = "layer 1: torso";
    draw_sprite_ext(_lover_base_portrait, 1, portrait_x, portrait_y + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);'''
    if old_lpe in code:
        code = code.replace(old_lpe, new_lpe, 1)

    # Safe fallbacks for boobs, face, mouth, bangs in Lover portrait
    code = code.replace(
        "draw_sprite_ext(func_get_portrait_boobs(top_sprite, 0), 2, portrait_x, _boob_y, _boob_xscale, _boob_yscale, 0, top_skin, 1);",
        "var _lb_boob = func_get_portrait_boobs(top_sprite, 0); if (!sprite_exists(_lb_boob) || _lb_boob == -1) _lb_boob = _lover_base_portrait; draw_sprite_ext(_lb_boob, 2, portrait_x, _boob_y, _boob_xscale, _boob_yscale, 0, top_skin, 1);"
    )
    code = code.replace(
        "draw_sprite_ext(func_get_portrait(top_sprite, 0), 3, portrait_x, portrait_y + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);",
        "draw_sprite_ext(_lover_base_portrait, 3, portrait_x, portrait_y + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);"
    )
    code = code.replace(
        "draw_sprite_ext(func_get_portrait(top_sprite, 0), (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 12 : 8,",
        "draw_sprite_ext(_lover_base_portrait, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 12 : 8,"
    )

    # Fix all c_sprite and dt_c_sprite assignments without string collision
    code = code.replace("dt_c_sprite = legacy_custom_condom;", "if (sprite_exists(legacy_custom_condom) && legacy_custom_condom != -1) dt_c_sprite = legacy_custom_condom;")
    code = code.replace(" c_sprite = legacy_custom_condom;", " if (sprite_exists(legacy_custom_condom) && legacy_custom_condom != -1) c_sprite = legacy_custom_condom;")
    code = code.replace("draw_sprite_ext(legacy_xray_sprite", "var _lx = (sprite_exists(legacy_xray_sprite) && legacy_xray_sprite != -1) ? legacy_xray_sprite : sFutaXray; draw_sprite_ext(_lx")

    # Safety before drawing condoms in mating press (around line 1770)
    code = code.replace(
        "draw_sprite_ext(c_sprite, p_condom,",
        "if (!sprite_exists(c_sprite) || c_sprite == -1) c_sprite = sFutaCondom; draw_sprite_ext(c_sprite, p_condom,"
    )
    code = code.replace(
        "draw_sprite_ext(c_sprite, p_broken,",
        "if (!sprite_exists(c_sprite) || c_sprite == -1) c_sprite = sFutaCondom; draw_sprite_ext(c_sprite, p_broken,"
    )

    LOGGER.log("Draw_0: Injected sprite existence guards on custom_portrait draws (cures requested -1 crash).", prefix="[+]")

    # Unlock ALL 8 gameplay mechanics with open panels
    code = code.replace(
        "if (futa_selector_open == true || newlover_menu_toggle == true || newwife_menu_toggle == true || radio_toggle == true || futa_selector_close_timer > 0)\n{\n    penis_grab = false;\n}",
        "if (futa_selector_open == true || radio_toggle == true || futa_selector_close_timer > 0)\n{\n    penis_grab = false;\n}"
    )

    old_targets = [
        ("if (radial_menu_open == false && futa_selector_open == false && radial_manual_ui_mode == false && newlover_menu_toggle == false && newwife_menu_toggle == false)",
         "if (radial_menu_open == false && futa_selector_open == false && radial_manual_ui_mode == false)"),

        ("if (manual_mode > 0 && manual_cursor_free == false && radial_menu_open == false && futa_selector_open == false && radial_manual_ui_mode == false && newlover_menu_toggle == false && newwife_menu_toggle == false)",
         "if (manual_mode > 0 && manual_cursor_free == false && radial_menu_open == false && futa_selector_open == false && radial_manual_ui_mode == false)"),

        ("else if (manual_mode > 0 && (radial_menu_open == true || futa_selector_open == true || newlover_menu_toggle == true || newwife_menu_toggle == true))",
         "else if (manual_mode > 0 && (radial_menu_open == true || futa_selector_open == true))"),

        ("if (manual_mode == 2 && orgasm == false && manual_full_orgasm_cooldown <= 0 && options_toggle == false && in_action_menu == false && !(hearts_toggle == true && loads >= max_loads) && radial_menu_open == false && futa_selector_open == false && newlover_menu_toggle == false && newwife_menu_toggle == false && radial_lc_close_grace <= 0 && radial_manual_ui_mode == false)",
         "if (manual_mode == 2 && orgasm == false && manual_full_orgasm_cooldown <= 0 && options_toggle == false && in_action_menu == false && !(hearts_toggle == true && loads >= max_loads) && radial_menu_open == false && futa_selector_open == false && radial_lc_close_grace <= 0 && radial_manual_ui_mode == false)"),

        ("if (mouse_check_button_pressed(mb_left) && manual_pump_cooldown <= 0 && options_toggle == false && in_action_menu == false && orgasm == true && radial_menu_open == false && futa_selector_open == false && newlover_menu_toggle == false && newwife_menu_toggle == false && shot_queue <= 0)",
         "if (mouse_check_button_pressed(mb_left) && manual_pump_cooldown <= 0 && options_toggle == false && in_action_menu == false && orgasm == true && radial_menu_open == false && futa_selector_open == false && shot_queue <= 0)"),

        ("if (mouse_mode == 1 && title == false && (manual_mode == 0 || manual_cursor_free == true) && futa_selector_open == false && futa_selector_close_timer <= 0 && newlover_menu_toggle == false && newwife_menu_toggle == false && radio_toggle == false)",
         "if (mouse_mode == 1 && title == false && (manual_mode == 0 || manual_cursor_free == true) && futa_selector_open == false && futa_selector_close_timer <= 0 && radio_toggle == false)"),

        ("if (mouse_mode == 2 && (manual_mode == 0 || manual_cursor_free == true) && futa_selector_open == false && futa_selector_close_timer <= 0 && newlover_menu_toggle == false && newwife_menu_toggle == false && radio_toggle == false)",
         "if (mouse_mode == 2 && (manual_mode == 0 || manual_cursor_free == true) && futa_selector_open == false && futa_selector_close_timer <= 0 && radio_toggle == false)"),

        ("if (manual_mode > 0 && radial_menu_open == false && radial_manual_ui_mode == false && newlover_menu_toggle == false && newwife_menu_toggle == false)",
         "if (manual_mode > 0 && radial_menu_open == false && radial_manual_ui_mode == false)")
    ]

    for old_t, new_t in old_targets:
        if old_t in code:
            code = code.replace(old_t, new_t, 1)

    LOGGER.log("Draw_0: Unlocked ALL 8 gameplay mechanics to work continuously while UI panels are open.", prefix="[+]")

    # Hitboxes & accessibility for New Lover and New Wife
    old_nl_cond = "if (insert == false && orgasm == false && newwife_menu_toggle == false && title == false && start_timer < 1 && (manual_mode == 0 || radial_manual_ui_mode == true || radial_panel_from_radial == true))"
    new_nl_cond = "if (title == false && start_timer < 1)"
    if old_nl_cond in code:
        code = code.replace(old_nl_cond, new_nl_cond, 1)


    old_nl_btn = '''    button_newlover_press = point_in_rectangle(mouse_x, mouse_y, portrait_x - 35, portrait_y + 52, portrait_x + 35, portrait_y + 69);'''
    new_nl_btn = '''    var _mob_touch_nl = false;
    for (var _d = 0; _d < 3; _d++)
    {
        if (device_mouse_check_button_pressed(_d, mb_left))
        {
            var _dx = device_mouse_x(_d);
            var _dy = device_mouse_y(_d);
            if (_dx >= (portrait_x - 36) && _dx <= (portrait_x + 36) && _dy >= (portrait_y + 48) && _dy <= (portrait_y + 72))
                _mob_touch_nl = true;
        }
    }
    var _mouse_hit_nl = point_in_rectangle(mouse_x, mouse_y, portrait_x - 36, portrait_y + 48, portrait_x + 36, portrait_y + 72);
    button_newlover_press = (_mouse_hit_nl && mouse_check_button(mb_left)) || _mob_touch_nl;'''

    if old_nl_btn in code:
        code = code.replace(old_nl_btn, new_nl_btn, 1)

    old_nl_open_block = '''    if (newlover_menu_toggle == false)
    {
        if (button_newlover_press == true && mouse_check_button_pressed(mb_left))
        {
            newlover_menu_toggle = true;
            newwife_menu_toggle = false;
            if (oBackground.background_id == 3)
            {
                oAudioManager.play_sfx(asset_get_index("StarshipIN"), 1);
            }
            else if (oBackground.background_id == 2)
            {
                oAudioManager.play_sfx(asset_get_index("OfficeIN"), 1);
            }
            else if (oBackground.background_id == 5)
            {
                oAudioManager.play_sfx(asset_get_index("VipIN"), 1);
            }
            else if (oBackground.background_id == 1)
            {
                oAudioManager.play_sfx(asset_get_index("BeachIN"), 1);
            }
            else if (oBackground.background_id == 4)
            {
                oAudioManager.play_sfx(asset_get_index("DungeonIN"), 1);
            }
            else if (oBackground.background_id == 0)
            {
                oAudioManager.play_sfx(asset_get_index("BedroomIN"), 1);
            }
        }
        if (keyboard_check_pressed(ord("Q")) && options_toggle == false && selector_search_focused == false)
        {
            func_randomize_top();
            sex_progress = 0;
            edge_charge = 0;
            edge_snap_timer = 0;
            desperate_edge_state = 0;
            desperate_edge_timer = 0;
            edge_control_lock = false;
            futa_score = 0;
            loads = 0;
            wife_climax_counter = 0;
            impregnation_counter = 0;
            body_jiggle = 0.025;
            alarm[0] = 1;
            oAudioManager.play_sfx(sndCloth, 0, random_range(0.8, 1.2), 0.6);
        }
    }'''

    new_nl_open_block = '''    if (!futa_selector_open && !mob_expanded && ((_mouse_hit_nl && mouse_check_button_pressed(mb_left)) || _mob_touch_nl))
    {
        newlover_menu_toggle = !newlover_menu_toggle;
        if (newlover_menu_toggle) newwife_menu_toggle = false;
                if (newlover_menu_toggle)
        {
            if (oBackground.background_id == 3)
            {
                oAudioManager.play_sfx(asset_get_index("StarshipIN"), 1);
            }
            else if (oBackground.background_id == 2)
            {
                oAudioManager.play_sfx(asset_get_index("OfficeIN"), 1);
            }
            else if (oBackground.background_id == 5)
            {
                oAudioManager.play_sfx(asset_get_index("VipIN"), 1);
            }
            else if (oBackground.background_id == 1)
            {
                oAudioManager.play_sfx(asset_get_index("BeachIN"), 1);
            }
            else if (oBackground.background_id == 4)
            {
                oAudioManager.play_sfx(asset_get_index("DungeonIN"), 1);
            }
            else if (oBackground.background_id == 0)
            {
                oAudioManager.play_sfx(asset_get_index("BedroomIN"), 1);
            }
        }
        else
        {
            if (oBackground.background_id == 3)
            {
                oAudioManager.play_sfx(asset_get_index("StarshipOUT"), 1);
            }
            else if (oBackground.background_id == 2)
            {
                oAudioManager.play_sfx(asset_get_index("OfficeOUT"), 1);
            }
            else if (oBackground.background_id == 5)
            {
                oAudioManager.play_sfx(asset_get_index("VipOUT"), 1);
            }
            else if (oBackground.background_id == 1)
            {
                oAudioManager.play_sfx(asset_get_index("BeachOUT"), 1);
            }
            else if (oBackground.background_id == 4)
            {
                oAudioManager.play_sfx(asset_get_index("DungeonOUT"), 1);
            }
            else if (oBackground.background_id == 0)
            {
                oAudioManager.play_sfx(asset_get_index("BedroomOUT"), 1);
            }
        }
    }
    if (newlover_menu_toggle == false)
    {
        if (keyboard_check_pressed(ord("Q")) && options_toggle == false && selector_search_focused == false)
        {
            var _c_count = ds_list_size(custom_futas_folder);
            if (_c_count > 0 && random(1) < 0.85)
            {
                custom_lover_toggle = true;
                custom_futa_index = irandom(_c_count - 1);
                var _rf = ds_list_find_value(custom_futas_folder, custom_futa_index);
                var _alt_max = 1;
                while (file_exists(string(_rf) + "/custom_futa_mating_press_alt_" + string(_alt_max) + ".png"))
                {
                    _alt_max++;
                }
                custom_futa_alt_index = irandom(_alt_max - 1);
                func_load_custom_futa(_rf, custom_futa_alt_index);
                forced_sprite = is_legacy_custom ? legacy_custom_mating_press : custom_mating_press;
                top_sprite = forced_sprite;
                func_apply_custom_futa_stats();
            }
            else
            {
                custom_lover_toggle = false;
                func_randomize_top();
            }
            sex_progress = 0;
            edge_charge = 0;
            edge_snap_timer = 0;
            desperate_edge_state = 0;
            desperate_edge_timer = 0;
            edge_control_lock = false;
            futa_score = 0;
            loads = 0;
            wife_climax_counter = 0;
            impregnation_counter = 0;
            body_jiggle = 0.025;
            alarm[0] = 1;
            oAudioManager.play_sfx(sndCloth, 0, random_range(0.8, 1.2), 0.6);
        }
    }'''

    if old_nl_open_block in code:
        code = code.replace(old_nl_open_block, new_nl_open_block, 1)

    # Fluid boundary clamping and dragging for New Lover panel
    old_nl_drag = '''        var menu_cx = newlover_menu_cx;
        var menu_end_y = portrait_y - newlover_menu_cy_end_offset;
        var menu_start_y = menu_end_y - total_h;
        var menu_cy = (menu_start_y + menu_end_y) * 0.5;
        comment = "drag handle = title bar area";
        var can_drag_nl = point_in_rectangle(mouse_x, mouse_y, menu_cx - (menu_w_px * 0.5), menu_start_y, menu_cx + (menu_w_px * 0.5), menu_start_y + menu_pad + title_h + 4);
        if (mouse_check_button_pressed(mb_left) && can_drag_nl)
        {
            newlover_dragging = true;
            drag_offset_x = newlover_menu_cx - mouse_x;
            drag_offset_y = portrait_y - newlover_menu_cy_end_offset - mouse_y;
        }
        if (newlover_dragging)
        {
            newlover_menu_cx = mouse_x + drag_offset_x;
            newlover_menu_cy_end_offset = portrait_y - (mouse_y + drag_offset_y);
            menu_cx = newlover_menu_cx;
            menu_end_y = portrait_y - newlover_menu_cy_end_offset;
            menu_start_y = menu_end_y - total_h;
            menu_cy = (menu_start_y + menu_end_y) * 0.5;
            if (mouse_check_button_released(mb_left))
            {
                newlover_dragging = false;
            }
        }'''

    new_nl_drag = '''        // Fluid boundary clamping for New Lover panel
        newlover_menu_cx = clamp(newlover_menu_cx, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
        var _nl_min_offset = portrait_y - room_height + 4;
        var _nl_max_offset = portrait_y - total_h - 4;
        newlover_menu_cy_end_offset = clamp(newlover_menu_cy_end_offset, _nl_min_offset, _nl_max_offset);

        var menu_cx = newlover_menu_cx;
        var menu_end_y = portrait_y - newlover_menu_cy_end_offset;
        var menu_start_y = menu_end_y - total_h;
        var menu_cy = (menu_start_y + menu_end_y) * 0.5;

        comment = "drag handle = title bar area";
        var _close_nl_pre_x = menu_cx + (menu_w_px * 0.5) - 7;
        var _close_nl_pre_y = menu_start_y + menu_pad + 1;
        var _close_nl_pre_hover = point_in_rectangle(mouse_x, mouse_y, _close_nl_pre_x - 6, _close_nl_pre_y - 2, _close_nl_pre_x + 6, _close_nl_pre_y + 9);
        var can_drag_nl = point_in_rectangle(mouse_x, mouse_y, menu_cx - (menu_w_px * 0.5), menu_start_y - 2, menu_cx + (menu_w_px * 0.5), menu_start_y + menu_pad + title_h + 8);
        if (mouse_check_button_pressed(mb_left) && can_drag_nl && !_close_nl_pre_hover)
        {
            newlover_dragging = true;
            drag_offset_x = newlover_menu_cx - mouse_x;
            drag_offset_y = portrait_y - newlover_menu_cy_end_offset - mouse_y;
        }
        if (newlover_dragging)
        {
            newlover_menu_cx = clamp(mouse_x + drag_offset_x, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
            newlover_menu_cy_end_offset = clamp(portrait_y - (mouse_y + drag_offset_y), _nl_min_offset, _nl_max_offset);
            menu_cx = newlover_menu_cx;
            menu_end_y = portrait_y - newlover_menu_cy_end_offset;
            menu_start_y = menu_end_y - total_h;
            menu_cy = (menu_start_y + menu_end_y) * 0.5;
            if (mouse_check_button_released(mb_left))
            {
                newlover_dragging = false;
            }
        }
        var _close_nl_x = menu_cx + (menu_w_px * 0.5) - 7;
        var _close_nl_y = menu_start_y + menu_pad + 1;
        var _close_nl_hover = point_in_rectangle(mouse_x, mouse_y, _close_nl_x - 12, _close_nl_y - 6, _close_nl_x + 12, _close_nl_y + 14);'''

    if old_nl_drag in code:
        code = code.replace(old_nl_drag, new_nl_drag, 1)

    target_nl_title = 'draw_text_transformed(menu_cx, menu_start_y + menu_pad, "LOVER", 0.65, 0.65, 0);'
    new_nl_title = '''draw_text_transformed(menu_cx, menu_start_y + menu_pad, "LOVER", 0.65, 0.65, 0);
        draw_set_font(fntFontSmall);
        draw_set_color(_close_nl_hover ? make_color_rgb(255, 120, 120) : c_white);
        draw_text_transformed(_close_nl_x, _close_nl_y, "X", 0.6, 0.6, 0);
        draw_set_font(fntFontBig);
        if (_close_nl_hover && mouse_check_button_pressed(mb_left))
        {
            newlover_menu_toggle = false; 
        }'''
    if target_nl_title in code and "_close_nl_hover ? make_color_rgb" not in code:
        code = code.replace(target_nl_title, new_nl_title, 1)

    # Fluid boundary clamping and dragging for New Wife panel
    old_nw_drag = '''        var menu_cx = newwife_menu_x;
        var menu_cy = newwife_menu_y;
        var menu_start_y = menu_cy - (total_h * 0.5);
        var menu_end_y = menu_cy + (total_h * 0.5);
        comment = "drag handle = title bar";
        var can_drag_nw = point_in_rectangle(mouse_x, mouse_y, menu_cx - (menu_w_px * 0.5), menu_start_y, menu_cx + (menu_w_px * 0.5), menu_start_y + menu_pad + title_h + 4);
        if (mouse_check_button_pressed(mb_left) && can_drag_nw)
        {
            newwife_dragging = true;
            drag_offset_x = newwife_menu_x - mouse_x;
            drag_offset_y = newwife_menu_y - mouse_y;
        }
        if (newwife_dragging)
        {
            newwife_menu_x = mouse_x + drag_offset_x;
            newwife_menu_y = mouse_y + drag_offset_y;
            menu_cx = newwife_menu_x;
            menu_cy = newwife_menu_y;
            menu_start_y = menu_cy - (total_h * 0.5);
            menu_end_y = menu_cy + (total_h * 0.5);
            if (mouse_check_button_released(mb_left))
            {
                newwife_dragging = false;
            }
        }'''

    new_nw_drag = '''        // Fluid boundary clamping for New Wife panel
        newwife_menu_x = clamp(newwife_menu_x, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
        newwife_menu_y = clamp(newwife_menu_y, (total_h * 0.5) + 4, room_height - ((total_h * 0.5) + 4));

        var menu_cx = newwife_menu_x;
        var menu_cy = newwife_menu_y;
        var menu_start_y = menu_cy - (total_h * 0.5);
        var menu_end_y = menu_cy + (total_h * 0.5);

        comment = "drag handle = title bar";
        var _close_nw_pre_x = menu_cx + (menu_w_px * 0.5) - 7;
        var _close_nw_pre_y = menu_start_y + menu_pad + 1;
        var _close_nw_pre_hover = point_in_rectangle(mouse_x, mouse_y, _close_nw_pre_x - 6, _close_nw_pre_y - 2, _close_nw_pre_x + 6, _close_nw_pre_y + 9);
        var can_drag_nw = point_in_rectangle(mouse_x, mouse_y, menu_cx - (menu_w_px * 0.5), menu_start_y - 2, menu_cx + (menu_w_px * 0.5), menu_start_y + menu_pad + title_h + 8);
        if (mouse_check_button_pressed(mb_left) && can_drag_nw && !_close_nw_pre_hover)
        {
            newwife_dragging = true;
            drag_offset_x = newwife_menu_x - mouse_x;
            drag_offset_y = newwife_menu_y - mouse_y;
        }
        if (newwife_dragging)
        {
            newwife_menu_x = clamp(mouse_x + drag_offset_x, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
            newwife_menu_y = clamp(mouse_y + drag_offset_y, (total_h * 0.5) + 4, room_height - ((total_h * 0.5) + 4));
            menu_cx = newwife_menu_x;
            menu_cy = newwife_menu_y;
            menu_start_y = menu_cy - (total_h * 0.5);
            menu_end_y = menu_cy + (total_h * 0.5);
            if (mouse_check_button_released(mb_left))
            {
                newwife_dragging = false;
            }
        }
        var _close_nw_x = menu_cx + (menu_w_px * 0.5) - 7;
        var _close_nw_y = menu_start_y + menu_pad + 1;
        var _close_nw_hover = point_in_rectangle(mouse_x, mouse_y, _close_nw_x - 12, _close_nw_y - 6, _close_nw_x + 12, _close_nw_y + 14);'''

    if old_nw_drag in code:
        code = code.replace(old_nw_drag, new_nw_drag, 1)

    target_nw_title = 'draw_text_transformed(menu_cx, menu_start_y + menu_pad, "WIFE", 0.65, 0.65, 0);'
    new_nw_title = '''draw_text_transformed(menu_cx, menu_start_y + menu_pad, "WIFE", 0.65, 0.65, 0);
        draw_set_font(fntFontSmall);
        draw_set_color(_close_nw_hover ? make_color_rgb(255, 120, 120) : c_white);
        draw_text_transformed(_close_nw_x, _close_nw_y, "X", 0.6, 0.6, 0);
        draw_set_font(fntFontBig);
        if (_close_nw_hover && mouse_check_button_pressed(mb_left))
        {
            newwife_menu_toggle = false; 
        }'''
    if target_nw_title in code and "_close_nw_hover ? make_color_rgb" not in code:
        code = code.replace(target_nw_title, new_nw_title, 1)

    old_nl_outside = "if (mouse_check_button_pressed(mb_left) && !menu_bounds && !newlover_dragging && !mm_press5 && !in_action_menu)"
    new_nl_outside = "// Outside-click auto-close removed: menus remain open independently\n        if (false)"
    if old_nl_outside in code:
        code = code.replace(old_nl_outside, new_nl_outside, 1)

    old_nw_line_14135 = '''comment = "switch partner button";
mm_press4 = false;
if (title == false && start_timer < 1 && edge_snap_timer <= 0 && (manual_mode == 0 || radial_manual_ui_mode == true || radial_panel_from_radial == true))'''
    new_nw_line_14135 = '''comment = "switch partner button";
mm_press4 = false;
if (title == false && start_timer < 1)'''
    if old_nw_line_14135 in code:
        code = code.replace(old_nw_line_14135, new_nw_line_14135, 1)

    old_nw_btn = "mm_press4 = point_in_rectangle(mouse_x, mouse_y, mm_x4 - 6, mm_y4 - 6, mm_x4 + 5, mm_y4 + 5);"
    new_nw_btn = """var _mob_touch_nw = false;
    for (var _d = 0; _d < 3; _d++)
    {
        if (device_mouse_check_button_pressed(_d, mb_left))
        {
            var _dx = device_mouse_x(_d);
            var _dy = device_mouse_y(_d);
            if (_dx >= (mm_x4 - 14) && _dx <= (mm_x4 + 14) && _dy >= (mm_y4 - 10) && _dy <= (mm_y4 + 10))
                _mob_touch_nw = true;
        }
    }
    var _mouse_hit_nw = point_in_rectangle(mouse_x, mouse_y, mm_x4 - 14, mm_y4 - 10, mm_x4 + 14, mm_y4 + 10);
    mm_press4 = _mouse_hit_nw || _mob_touch_nw;"""
    if old_nw_btn in code:
        code = code.replace(old_nw_btn, new_nw_btn, 1)

    old_nw_click = "if (mm_press4 == true && mouse_check_button_pressed(mb_left) && title == false)"
    new_nw_click = "if (!futa_selector_open && !mob_expanded && ((_mouse_hit_nw && mouse_check_button_pressed(mb_left)) || _mob_touch_nw)) if (title == false)"
    if old_nw_click in code:
        code = code.replace(old_nw_click, new_nw_click, 1)

    old_nw_draw = "if (newlover_menu_toggle == false && button_newlover_press == false && orgasm == false && title == false && start_timer < 1)"
    new_nw_draw = "if (title == false && start_timer < 1)"
    if old_nw_draw in code:
        code = code.replace(old_nw_draw, new_nw_draw, 1)

    old_nw_menu = "if (newwife_menu_toggle == true && orgasm == false && button_newlover_press == false)"
    new_nw_menu = "if (newwife_menu_toggle == true && orgasm == false)"
    if old_nw_menu in code:
        code = code.replace(old_nw_menu, new_nw_menu, 1)

    old_nw_outside = "if (mouse_check_button_pressed(mb_left) && !menu_bounds_w && !newwife_dragging && !mm_press4 && !mm_press5 && !in_action_menu)"
    new_nw_outside = "// Outside-click auto-close removed: menus remain open independently\n        if (false)"
    if old_nw_outside in code:
        code = code.replace(old_nw_outside, new_nw_outside, 1)

    old_act_btn = "if (newlover_menu_toggle == false && button_newlover_press == false && newwife_menu_toggle == false && orgasm == false)"
    new_act_btn = "if (orgasm == false && title == false)"
    if old_act_btn in code:
        code = code.replace(old_act_btn, new_act_btn, 1)

    code = code.replace(
        "if (mouse_check_button_pressed(mb_right) || keyboard_check_pressed(vk_escape))\n        {\n            newlover_menu_toggle = false;",
        "if (keyboard_check_pressed(vk_escape))\n        {\n            newlover_menu_toggle = false;"
    )
    code = code.replace(
        "if (mouse_check_button_pressed(mb_right) || keyboard_check_pressed(vk_escape))\n        {\n            newwife_menu_toggle = false;",
        "if (keyboard_check_pressed(vk_escape))\n        {\n            newwife_menu_toggle = false;"
    )

    code = code.replace(
        "newlover_menu_toggle = true;\n            newwife_menu_toggle = false;\n            radial_panel_from_radial = true;",
        "newlover_menu_toggle = true;\n            radial_panel_from_radial = true;"
    )
    code = code.replace(
        "newwife_menu_toggle = true;\n            newlover_menu_toggle = false;\n            radial_panel_from_radial = true;",
        "newwife_menu_toggle = true;\n            radial_panel_from_radial = true;"
    )
    code = code.replace(
        "else if (newlover_menu_toggle == true || newwife_menu_toggle == true)\n    {\n        newlover_menu_toggle = false;\n        newwife_menu_toggle = false;\n    }",
        "// keep simultaneous menus open"
    )

    code = code.replace(
        "if (top_sprite == custom_mating_press)\n    {\n        penis_sprite = custom_mating_press;\n    }",
        "if (custom_lover_toggle == true || top_sprite == custom_mating_press || top_sprite == legacy_custom_mating_press)\n    {\n        penis_sprite = top_sprite;\n    }"
    )

    old_menu_trans = '''comment = "menu transition";
if (title == true && peek_closed_during_play == false)
{
    if (mouse_check_button_pressed(mb_left) && title_timer < 1)
    {
        if (disclaimer == false && title_from_hotkey == false && skip_disclaimer == false)
        {
            disclaimer = true;
        }
        else
        {
            title = false;'''

    new_menu_trans = '''comment = "menu transition - warning displays once on startup, peek mode unaffected";
if (title == true && peek_closed_during_play == false)
{
    if (mouse_check_button_pressed(mb_left) && title_timer < 1)
    {
        if (disclaimer == false && title_from_hotkey == false && skip_disclaimer == false)
        {
            disclaimer = true;
        }
        else
        {
            title = false;
            peek_closed_during_play = true; // Game started! Warning will never interrupt peek mode again
            disclaimer = false;'''

    if old_menu_trans in code:
        code = code.replace(old_menu_trans, new_menu_trans, 1)
        LOGGER.log("Draw_0: Title screen warning set to display ONCE only on startup (fixes peek mode).", prefix="[+]")

    old_hitbox_vis = '''    draw_set_color(_head_hover ? _col_hover : _col_idle);
    draw_rectangle(_head_x1, _head_y1, _head_x2, _head_y2, true);
    draw_set_color(c_white);
    draw_set_alpha(1);'''

    new_hitbox_vis = '''    draw_set_color(_head_hover ? _col_hover : _col_idle);
    draw_rectangle(_head_x1, _head_y1, _head_x2, _head_y2, true);
    // Debug hitboxes for Lover and Wife buttons
    draw_set_color(button_newlover_press ? _col_hover : _col_idle);
    draw_rectangle(portrait_x - 36, portrait_y + 48, portrait_x + 36, portrait_y + 72, true);
    draw_set_color(mm_press4 ? _col_hover : _col_idle);
    draw_rectangle((room_width - 332) - 14, (room_height - ui_y_offset) - 10, (room_width - 332) + 14, (room_height - ui_y_offset) + 10, true);
    draw_set_color(c_white);
    draw_set_alpha(1);'''

    if old_hitbox_vis in code:
        code = code.replace(old_hitbox_vis, new_hitbox_vis, 1)

    code = inject_virtual_keyboard_and_search(code)
    code = inject_lazy_thumbnails_into_draw(code)
    code = enforce_strict_custom_selection(code)

    old_skip = '''        var _cbx = (room_width / 2) - 170;
        var _cby = room_height - 52;
        var _cb_size = 8;
        var _cb_hover = point_in_rectangle(mouse_x, mouse_y, _cbx - _cb_size, _cby - _cb_size, _cbx + _cb_size, _cby + _cb_size);
        draw_set_alpha(disclaimer_scale * title_scale);
        draw_set_color(c_white);
        draw_rectangle(_cbx - _cb_size, _cby - _cb_size, _cbx + _cb_size, _cby + _cb_size, true);
        if (skip_disclaimer)
        {
            draw_line((_cbx - _cb_size) + 2, _cby, _cbx - 2, (_cby + _cb_size) - 2);
            draw_line(_cbx - 2, (_cby + _cb_size) - 2, (_cbx + _cb_size) - 2, (_cby - _cb_size) + 2);
        }
        draw_set_halign(fa_left);
        draw_text_transformed(_cbx + _cb_size + 4, _cby, "skip", 0.5, 0.5, 0);
        draw_set_halign(fa_center);
        draw_set_alpha(1);
        if (_cb_hover && mouse_check_button_pressed(mb_left) && disclaimer_scale > 0.9)
        {
            skip_disclaimer = !skip_disclaimer;
            func_save_settings();
        }'''
    if old_skip in code:
        code = code.replace(old_skip, '// Skip option removed by patcher', 1)

    code = inject_complete_overlay(code)


    if enable_toy_telemetry:
        bp_draw = """
if (variable_instance_exists(id, "buttplug_socket") && buttplug_socket >= 0)
{
    var _bp_now = current_time;
    if (_bp_now - buttplug_last_send >= 33)
    {
        buttplug_last_send = _bp_now;
        buffer_seek(buttplug_buffer, buffer_seek_start, 0);
        buffer_write(buttplug_buffer, buffer_string, string(thrust) + "," + string(thrust_prev) + "," + string(thrust_speed) + "," + string(thrust_strength) + "," + string(insert) + "," + string(orgasm));
        network_send_udp_raw(buttplug_socket, "127.0.0.1", buttplug_port, buttplug_buffer, buffer_tell(buttplug_buffer));
    }
}
"""
        code = code + bp_draw
        LOGGER.log("Draw_0: Enabled ToyBridge UDP thrust broadcast telemetry.", prefix="[+]")

    return code

def inject_virtual_keyboard_and_search(code):
    """Injects virtual keyboard on search focus, prioritized favorites filter button, and card badges."""
    if "_sel_jump_done" in code and "FAV: ALL" in code:
        return code
    # Header: [FAV: ALL/ON] on Left with absolute priority, Search Bar on Right
    old_search_focus = """    var _bar_x2 = room_width - 80;
    var _bar_y1 = 4;
    var _bar_y2 = 19;
    var _bar_hover = point_in_rectangle(mouse_x, mouse_y, _bar_x1, _bar_y1, _bar_x2, _bar_y2);
    if (mouse_check_button_pressed(mb_left))
    {
        if (_bar_hover)
        {
            if (selector_search_focused == false)
            {
                selector_search_focused = true;
                keyboard_string = selector_search_string;
            }
        }
        else
        {
            selector_search_focused = false;
        }
    }
    if (selector_search_focused)
    {
        selector_search_string = keyboard_string;
    }
    if (keyboard_check_pressed(vk_escape) && selector_search_focused)
    {
        selector_search_focused = false;
        selector_search_string = "";
        keyboard_string = "";
    }"""

    new_search_focus = """    var _fav_btn_x1 = 20;
    var _fav_btn_x2 = 95;
    var _bar_x1 = 102;
    var _bar_x2 = room_width - 60;
    var _bar_y1 = 4;
    var _bar_y2 = 20;
    var _fav_btn_hover = point_in_rectangle(mouse_x, mouse_y, _fav_btn_x1 - 2, _bar_y1 - 2, _fav_btn_x2 + 2, _bar_y2 + 2);
    var _bar_hover = point_in_rectangle(mouse_x, mouse_y, _bar_x1 - 2, _bar_y1 - 2, _bar_x2 + 2, _bar_y2 + 2);
    if (mouse_check_button_pressed(mb_left))
    {
        if (_fav_btn_hover)
        {
            selector_favs_only = !selector_favs_only;
            futa_selector_menu.scroll = 0;
            futa_selector_menu.scroll_lerp = 0;
            if (selector_search_focused && (os_type == os_android || os_type == os_ios))
            {
                keyboard_virtual_hide();
            }
            selector_search_focused = false;
        }
        else if (_bar_hover)
        {
            if (selector_search_focused == false)
            {
                selector_search_focused = true;
                keyboard_string = selector_search_string;
                if (os_type == os_android || os_type == os_ios)
                {
                    keyboard_virtual_show(0, 0, 0, false);
                }
            }
        }
        else
        {
            if (selector_search_focused && (os_type == os_android || os_type == os_ios))
            {
                keyboard_virtual_hide();
            }
            selector_search_focused = false;
        }
    }
    if (selector_search_focused)
    {
        selector_search_string = keyboard_string;
    }
    if ((keyboard_check_pressed(vk_escape) || keyboard_check_pressed(vk_enter)) && selector_search_focused)
    {
        if (os_type == os_android || os_type == os_ios)
        {
            keyboard_virtual_hide();
        }
        selector_search_focused = false;
        if (keyboard_check_pressed(vk_escape))
        {
            selector_search_string = "";
            keyboard_string = "";
        }
    }
    // Draw Favorite Filter Button
    draw_set_color(selector_favs_only ? make_color_rgb(255, 215, 0) : make_color_rgb(55, 55, 55));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, false);
    draw_set_color(selector_favs_only ? c_white : make_color_rgb(140, 140, 140));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, true);
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_set_color(selector_favs_only ? c_black : c_white);
    draw_text_transformed((_fav_btn_x1 + _fav_btn_x2) * 0.5, (_bar_y1 + _bar_y2) * 0.5, selector_favs_only ? "FAV: ON" : "FAV: ALL", 0.45, 0.45, 0);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);"""

    if old_search_focus in code:
        code = code.replace(old_search_focus, new_search_focus, 1)

    old_max_scroll_def = "var _max_scroll = max(0, _total_content_w - room_width);"
    new_max_scroll_def = """var _max_scroll = max(0, _total_content_w - room_width);
    if (!variable_instance_exists(id, "_sel_jump_done") || !_sel_jump_done)
    {
        _sel_jump_done = true;
        selector_favs_only = false;
        var _cur_idx = (selector_mode == 0) ? custom_futa_index : custom_wife_index;
        if (_cur_idx >= 0 && _cur_idx < _futa_count)
        {
            var _jump_pair = _cur_idx div 2;
            var _jump_scroll = clamp((_jump_pair * (_cell_w + _pad)) - (room_width * 0.5) + (_cell_w * 0.5), 0, _max_scroll);
            futa_selector_menu.scroll = _jump_scroll;
            futa_selector_menu.scroll_lerp = _jump_scroll;
        }
    }"""

    if old_max_scroll_def in code and "_sel_jump_done" not in code:
        code = code.replace(old_max_scroll_def, new_max_scroll_def, 1)

    code = code.replace("futa_selector_open = false;", "futa_selector_open = false; _sel_jump_done = false; selector_favs_only = false;")

    target_border_draw = "draw_set_color(_border_col);\n            draw_rectangle(_cx - 2, _cy - 2, _cx + _cell_w + 2, _cy + _cell_h + 2, true);"
    new_border_draw = """var _is_equipped = (_ci == ((selector_mode == 0) ? custom_futa_index : custom_wife_index));
            if (_is_equipped)
            {
                draw_set_alpha(0.35 + (0.15 * sin(current_time * 0.005)));
                draw_set_color(make_color_rgb(255, 215, 0));
                draw_rectangle(_cx - 4, _cy - 4, _cx + _cell_w + 4, _cy + _cell_h + 4, false);
                draw_set_alpha(1);
                draw_rectangle(_cx - 4, _cy - 4, _cx + _cell_w + 4, _cy + _cell_h + 4, true);
                draw_rectangle(_cx - 3, _cy - 3, _cx + _cell_w + 3, _cy + _cell_h + 3, true);
                draw_set_font(fntFontSmall);
                draw_set_halign(fa_center);
                draw_set_valign(fa_bottom);
                draw_set_color(make_color_rgb(255, 225, 60));
                draw_text(_cx + (_cell_w * 0.5), _cy - 4, "★ " + string(_fname));
                draw_set_valign(fa_top);
            }
            draw_set_color(_border_col);
            draw_rectangle(_cx - 2, _cy - 2, _cx + _cell_w + 2, _cy + _cell_h + 2, true);"""

    if target_border_draw in code and "_is_equipped" not in code:
        code = code.replace(target_border_draw, new_border_draw, 1)

    return code

def inject_lazy_thumbnails_into_draw(code):
    """Injects or enhances on-demand thumbnail loader with dynamic frame count fallback."""
    old_loader = '''                    else if (file_exists(_pb))
                    {
                        _spr = sprite_add(_pb, 10, false, false, (selector_mode == 0) ? 54 : 32, (selector_mode == 0) ? 82 : 48);
                    }'''
    new_loader = '''                    else if (file_exists(_pb))
                    {
                        _spr = sprite_add(_pb, 10, false, false, (selector_mode == 0) ? 54 : 32, (selector_mode == 0) ? 82 : 48);
                        if (_spr <= 0 || !sprite_exists(_spr))
                        {
                            var _test_p = sprite_add(_pb, 1, false, false, 0, 0);
                            if (_test_p > 0 && sprite_exists(_test_p))
                            {
                                var _pw = sprite_get_width(_test_p);
                                var _ph = sprite_get_height(_test_p);
                                sprite_delete(_test_p);
                                var _p_frames = max(1, round(_pw / _ph));
                                _spr = sprite_add(_pb, _p_frames, false, false, (selector_mode == 0) ? 54 : 32, (selector_mode == 0) ? 82 : 48);
                            }
                        }
                    }'''
    if old_loader in code:
        code = code.replace(old_loader, new_loader, 1)
        # Guard c_sprite and custom_lover_toggle execution in Draw_0
    old_c_spr = '''            if (top_sprite == legacy_custom_mating_press)
            {
                c_sprite = legacy_custom_condom;
            }'''

    new_c_spr = '''            if (top_sprite == legacy_custom_mating_press)
            {
                c_sprite = (sprite_exists(legacy_custom_condom) && legacy_custom_condom != -1) ? legacy_custom_condom : sFutaCondom;
            }'''

    if old_c_spr in code:
        code = code.replace(old_c_spr, new_c_spr, 1)





    old_cw_toggle = '''                    else
                    {
                        var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        func_load_custom_wife(selected_folder, custom_wife_alt_index);
                        func_validate_sex_position();
                        var forced_bottom = legacy_custom_wife_toggle ? legacy_custom_wife_mating_press : custom_wife_mating_press;
                        if (forced_bottom != -1 && sprite_exists(forced_bottom))
                        {
                            bottom_sprite = forced_bottom;
                            func_apply_custom_wife_stats();
                        }
                        else
                        {
                            func_randomize_bottom();
                        }
                    }'''
    new_cw_toggle = '''                    else
                    {
                        var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        func_load_custom_wife(selected_folder, custom_wife_alt_index);
                        func_validate_sex_position();
                        func_apply_custom_wife_stats();
                        var _fb = legacy_custom_wife_toggle ? legacy_custom_wife_mating_press : custom_wife_mating_press;
                        if (_fb != -1 && sprite_exists(_fb))
                        {
                            bottom_sprite = _fb;
                        }
                        else
                        {
                            bottom_sprite = sWifeMatingPress;
                        }
                    }'''
    if old_cw_toggle in code:
        code = code.replace(old_cw_toggle, new_cw_toggle, 1)





    # Fortify grid selector clicks for custom futas and custom wives
    old_futa_click = '''                    if (selector_mode == 0)
                    {
                        custom_futa_index = _ci;
                        custom_futa_alt_index = 0;
                        var _sel_folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
                        custom_default_moans = false;
                        ds_list_clear(custom_moan_slow_list);
                        ds_list_clear(custom_moan_fast_list);
                        ds_list_clear(custom_orgasm_list);
                        ds_list_clear(moan_slow_list);
                        ds_list_clear(moan_fast_list);
                        ds_list_clear(orgasm_list);
                        moan_previous = -1;
                        if (os_type == os_android || os_type == os_ios)
                        {
                            keyboard_virtual_hide();
                        }
                        selector_search_focused = false;
                        func_load_custom_futa(_sel_folder, custom_futa_alt_index);
                        custom_lover_toggle = true;
                        var forced_sprite = is_legacy_custom ? legacy_custom_mating_press : custom_mating_press;
                        top_sprite = forced_sprite;
                        func_apply_custom_futa_stats();
                        func_top_speak("intro");
                        loads = 0;
                        sex_progress = 0;
                    }'''
    new_futa_click = '''                    if (selector_mode == 0)
                    {
                        custom_futa_index = _ci;
                        custom_futa_alt_index = 0;
                        var _sel_folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
                        custom_default_moans = false;
                        ds_list_clear(custom_moan_slow_list);
                        ds_list_clear(custom_moan_fast_list);
                        ds_list_clear(custom_orgasm_list);
                        ds_list_clear(moan_slow_list);
                        ds_list_clear(moan_fast_list);
                        ds_list_clear(orgasm_list);
                        moan_previous = -1;
                        if (os_type == os_android || os_type == os_ios)
                        {
                            keyboard_virtual_hide();
                        }
                        selector_search_focused = false;
                        func_load_custom_futa(_sel_folder, custom_futa_alt_index);
                        func_apply_custom_futa_stats();
                        custom_lover_toggle = true;
                        top_sprite = (sprite_exists(custom_mating_press) && custom_mating_press != -1) ? custom_mating_press : ((sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press != -1) ? legacy_custom_mating_press : sFutaMatingPress);
                        if (!sprite_exists(penis_sprite) || penis_sprite == -1) penis_sprite = top_sprite;
                        if (!sprite_exists(hair_sprite) || hair_sprite == -1) hair_sprite = top_sprite;
                        func_top_speak("intro");
                        loads = 0;
                        sex_progress = 0;
                    }'''
    if old_futa_click in code: code = code.replace(old_futa_click, new_futa_click, 1)

    old_wife_click = '''                    else
                    {
                        if (os_type == os_android || os_type == os_ios)
                        {
                            keyboard_virtual_hide();
                        }
                        selector_search_focused = false;
                        custom_wife_index = _ci;
                        custom_wife_alt_index = 0;
                        var _sel_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        func_load_custom_wife(_sel_folder, custom_wife_alt_index);
                        custom_wife_toggle = true;
                        var forced_bottom = legacy_custom_wife_toggle ? legacy_custom_wife_mating_press : custom_wife_mating_press;
                        bottom_sprite = forced_bottom;
                        func_validate_sex_position();
                        func_apply_custom_wife_stats();
                        func_bottom_speak("intro");
                    }'''
    new_wife_click = '''                    else
                    {
                        if (os_type == os_android || os_type == os_ios)
                        {
                            keyboard_virtual_hide();
                        }
                        selector_search_focused = false;
                        custom_wife_index = _ci;
                        custom_wife_alt_index = 0;
                        var _sel_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        func_load_custom_wife(_sel_folder, custom_wife_alt_index);
                        func_validate_sex_position();
                        func_apply_custom_wife_stats();
                        custom_wife_toggle = true;
                        bottom_sprite = (sprite_exists(legacy_custom_wife_mating_press) && legacy_custom_wife_mating_press != -1) ? legacy_custom_wife_mating_press : ((sprite_exists(custom_wife_mating_press) && custom_wife_mating_press != -1) ? custom_wife_mating_press : sWifeMatingPress);
                        func_bottom_speak("intro");
                    }'''
    if old_wife_click in code: code = code.replace(old_wife_click, new_wife_click, 1)

    old_w_scale_def = '''        var wife_boob_scale_x = (image_xscale + bottom_breath) * (1 - (0.1 * insert_thrust)) * bottom_boob_size;
        var wife_boob_final_x = x + ((wife_boob_scale_x - 1) * 0.5);
        var wife_ass_scale_x = (image_xscale + bottom_breath) * (1 - (0.1 * insert_thrust)) * bottom_ass_size;'''
    new_w_scale_def = '''        var _w_cur_sc = (custom_wife_toggle && variable_instance_exists(id, "custom_wife_mating_press_scale") && custom_wife_mating_press_scale > 0) ? custom_wife_mating_press_scale : 1;
        var wife_boob_scale_x = (image_xscale + bottom_breath) * (1 - (0.1 * insert_thrust)) * bottom_boob_size * _w_cur_sc;
        var wife_boob_final_x = x + ((wife_boob_scale_x - 1) * 0.5);
        var wife_ass_scale_x = (image_xscale + bottom_breath) * (1 - (0.1 * insert_thrust)) * bottom_ass_size * _w_cur_sc;'''
    if old_w_scale_def in code:
        code = code.replace(old_w_scale_def, new_w_scale_def, 1)

    # Favorites / Bookmarks UI and filter logic in Draw_0
    old_sd = """    var _display_text = (selector_search_string == "") ? (selector_search_focused ? "" : "search...") : selector_search_string;
    if (selector_search_focused && (current_time % 1000) < 500)
    {
        _display_text += "|";
    }
    draw_text_transformed(_bar_x1 + 4, (_bar_y1 + _bar_y2) / 2, _display_text, 0.55, 0.55, 0);

    // Draw Favorite Filter Button to the right of search bar
    draw_set_color(selector_favs_only ? make_color_rgb(255, 215, 0) : make_color_rgb(45, 45, 45));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, false);
    draw_set_color(selector_favs_only ? c_white : make_color_rgb(140, 140, 140));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, true);
    draw_set_font(fntFontSmall);
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_set_color(selector_favs_only ? c_black : c_white);
    draw_text((_fav_btn_x1 + _fav_btn_x2) * 0.5, (_bar_y1 + _bar_y2) * 0.5, selector_favs_only ? "FAV: ON" : "FAV: ALL");
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);"""

    new_sd = """    var _display_text = (selector_search_string == "") ? (selector_search_focused ? "" : "search...") : selector_search_string;
    if (selector_search_focused && (current_time % 1000) < 500)
    {
        _display_text += "|";
    }
    draw_text_transformed(_bar_x1 + 4, (_bar_y1 + _bar_y2) / 2, _display_text, 0.55, 0.55, 0);
    var _fav_btn_x1 = _bar_x2 + 8;
    var _fav_btn_x2 = _fav_btn_x1 + 48;
    var _fmx = (os_type == os_android || os_type == os_ios) ? device_mouse_x(0) : mouse_x;
    var _fmy = (os_type == os_android || os_type == os_ios) ? device_mouse_y(0) : mouse_y;
    var _fav_btn_hover = point_in_rectangle(_fmx, _fmy, _fav_btn_x1 - 6, _bar_y1 - 6, _fav_btn_x2 + 6, _bar_y2 + 8);
    draw_set_color(selector_favs_only ? make_color_rgb(255, 215, 0) : make_color_rgb(70, 70, 70));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, false);
    draw_set_color(c_white);
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, true);
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_set_color(selector_favs_only ? c_black : c_white);
    draw_text_transformed((_fav_btn_x1 + _fav_btn_x2) * 0.5, (_bar_y1 + _bar_y2) * 0.5, "★ FAV", 0.5, 0.5, 0);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
    if ((mouse_check_button_pressed(mb_left) || device_mouse_check_button_pressed(0, mb_left)) && _fav_btn_hover)
    {
        selector_favs_only = !selector_favs_only;
        futa_selector_menu.scroll = 0;
        futa_selector_menu.scroll_lerp = 0;
    }"""
    if old_sd in code: code = code.replace(old_sd, new_sd, 1)

    old_ci_top = """        var _fname = ds_list_find_value(_sel_names, _ci);
        var _fav_map = (selector_mode == 0) ? global.favs_futa : global.favs_wife;
        var _is_fav = ds_map_exists(_fav_map, _fname);
        if (selector_favs_only && !_is_fav)
        {
            continue;
        }
        if (_search_lower != "" && string_pos(_search_lower, string_lower(_fname)) == 0)
        {
            continue;
        }"""
    new_ci_top = """        var _fname = ds_list_find_value(_sel_names, _ci);
        var _fav_map = (selector_mode == 0) ? global.favs_futa : global.favs_wife;
        var _is_fav = ds_map_exists(_fav_map, _fname);
        if (selector_favs_only && !_is_fav)
        {
            continue;
        }
        if (_search_lower != "" && string_pos(_search_lower, string_lower(_fname)) == 0)
        {
            continue;
        }"""
    if old_ci_top in code: code = code.replace(old_ci_top, new_ci_top, 1)

    old_draw_cell_end = """            comment = "hover detection — highlight and record name";"""
    new_draw_cell_end = """            var _star_hover = point_in_rectangle(mouse_x, mouse_y, _cx + _cell_w - 18, _cy + 2, _cx + _cell_w - 2, _cy + 18);
            draw_set_halign(fa_right);
            draw_set_valign(fa_top);
            draw_set_color(_is_fav ? make_color_rgb(255, 215, 0) : make_color_rgb(120, 120, 120));
            var _bx1 = (_cx + _cell_w) - 16;
            var _by1 = _cy + 2;
            var _bx2 = _bx1 + 14;
            var _by2 = _by1 + 14;
            draw_set_alpha(1);
            draw_set_color(_is_fav ? make_color_rgb(255, 215, 0) : make_color_rgb(35, 35, 35));
            draw_rectangle(_bx1, _by1, _bx2, _by2, false);
            draw_set_color(_is_fav ? c_white : make_color_rgb(120, 120, 120));
            draw_rectangle(_bx1, _by1, _bx2, _by2, true);
            draw_set_color(_is_fav ? c_black : c_white);
            var _bcx = _bx1 + 7;
            var _bcy = _by1 + 7;
            draw_line_width(_bcx - 4, _bcy, _bcx + 4, _bcy, 2);
            draw_line_width(_bcx, _bcy - 4, _bcx, _bcy + 4, 2);
            if ((mouse_check_button_pressed(mb_left) || device_mouse_check_button_pressed(0, mb_left)) && _star_hover && futa_selector_open_timer <= 0)
            {
                ini_open("setting_data.sav");
                var _sec = (selector_mode == 0) ? "favs_futa" : "favs_wife";
                if (_is_fav)
                {
                    ds_map_delete(_fav_map, _fname);
                    ini_key_delete(_sec, _fname);
                }
                else
                {
                    ds_map_add(_fav_map, _fname, 1);
                    ini_write_real(_sec, _fname, 1);
                }
                ini_close();
            }
            comment = "hover detection — highlight and record name";"""
    if old_draw_cell_end in code: code = code.replace(old_draw_cell_end, new_draw_cell_end, 1)

    old_cc = 'if (mouse_check_button_pressed(mb_left) && !title && futa_selector_open_timer <= 0)'
    new_cc = 'if ((mouse_check_button_pressed(mb_left) || device_mouse_check_button_pressed(0, mb_left)) && !title && futa_selector_open_timer <= 0 && !_star_hover)'
    if old_cc in code:
        code = code.replace(old_cc, new_cc, 1)

    old_fab_txt = 'draw_text((_fab_x1 + _fab_x2) * 0.5, (_fab_y1 + _fab_y2) * 0.5, mob_expanded ? "✕" : "≡");'
    new_fab_txt = '''if (mob_expanded)
{
    draw_set_color(c_white);
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_text((_fab_x1 + _fab_x2) * 0.5, (_fab_y1 + _fab_y2) * 0.5, "X");
}
else
{
    var _mid_x = (_fab_x1 + _fab_x2) * 0.5;
    var _mid_y = (_fab_y1 + _fab_y2) * 0.5;
    draw_set_color(c_white);
    draw_set_alpha(0.85);
    draw_rectangle(_mid_x - 7, _mid_y - 5, _mid_x + 7, _mid_y - 4, false);
    draw_rectangle(_mid_x - 7, _mid_y - 1, _mid_x + 7, _mid_y, false);
    draw_rectangle(_mid_x - 7, _mid_y + 3, _mid_x + 7, _mid_y + 4, false);
}'''
    if old_fab_txt in code:
        code = code.replace(old_fab_txt, new_fab_txt, 1)

    # Priority: Suppress background lover and wife buttons while character selector is open
    code = code.replace('comment = "futa ratings window";\nvar button_newlover_press = false;\nif (title == false && start_timer < 1)', 'comment = "futa ratings window";\nvar button_newlover_press = false;\nif (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)', 1)
    code = code.replace('comment = "switch partner button";\nmm_press4 = false;\nif (title == false && start_timer < 1)', 'comment = "switch partner button";\nmm_press4 = false;\nif (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)', 1)
    code = code.replace('if ((button_newlover_press == true || newlover_menu_toggle == true) && options_toggle == false && orgasm == false)', 'if (newlover_menu_toggle == true && newwife_menu_toggle == false && options_toggle == false && orgasm == false && futa_selector_open == false)', 1)
    code = code.replace('if (mm_press4 == true || newwife_menu_toggle == true)', 'if (newwife_menu_toggle == true && newlover_menu_toggle == false && options_toggle == false && futa_selector_open == false)', 1)


    # Keep overlay menu button behind CSS screens
    code = code.replace('var _fab_x_offset = round(room_width * 0.12);', 'if (futa_selector_open == false)\n{\nvar _fab_x_offset = round(room_width * 0.12);', 1)
    code = code.replace('''draw_set_font(_mob_prev_fnt);
draw_set_halign(_mob_prev_halign);
draw_set_valign(_mob_prev_valign);
draw_set_color(_mob_prev_col);
draw_set_alpha(_mob_prev_alp);''', '''draw_set_font(_mob_prev_fnt);
draw_set_halign(_mob_prev_halign);
draw_set_valign(_mob_prev_valign);
draw_set_color(_mob_prev_col);
draw_set_alpha(_mob_prev_alp);
}''', 1)
    # Subtle, unobtrusive opacity across mobile overlay
    code = code.replace('var _fab_alpha = (mob_expanded || _fab_over) ? 0.65 : 0.22;', 'var _fab_alpha = (mob_expanded || _fab_over) ? 0.40 : 0.12;', 1)
    code = code.replace('draw_set_alpha((_qb_over && _mob_touch_d) ? 0.85 : 0.65);', 'draw_set_alpha((_qb_over && _mob_touch_d) ? 0.45 : 0.25);', 1)
    code = code.replace('''draw_set_alpha(0.85);
        draw_set_color(_qb_col);''', '''draw_set_alpha(0.40);
        draw_set_color(_qb_col);''', 1)
    code = code.replace('''draw_set_color(c_white);
        draw_text((_qbx1 + _qbx2) * 0.5, (_qby1 + _qby2) * 0.5, _qb_lbl);''', '''draw_set_alpha(0.65);
        draw_set_color(c_white);
        draw_text((_qbx1 + _qbx2) * 0.5, (_qby1 + _qby2) * 0.5, _qb_lbl);''', 1)
    code = code.replace('''draw_set_alpha(0.58);
    draw_set_color(_c_mob_bg);''', '''draw_set_alpha(0.35);
    draw_set_color(_c_mob_bg);''', 1)
    code = code.replace('''draw_set_alpha(0.45);
    draw_set_color(_c_mob_border);''', '''draw_set_alpha(0.25);
    draw_set_color(_c_mob_border);''', 1)
    code = code.replace('''draw_set_alpha(0.85);
    draw_set_color(c_white);
    draw_text((_mx1 + _mx2) * 0.5, _my1 + 12, "CONTROLS");''', '''draw_set_alpha(0.55);
    draw_set_color(c_white);
    draw_text((_mx1 + _mx2) * 0.5, _my1 + 12, "CONTROLS");''', 1)
    code = code.replace('draw_set_alpha((_btog_val || (_btn_over && _mob_touch_d && !mob_is_dragging)) ? 0.7 : 0.42);', 'draw_set_alpha((_btog_val || (_btn_over && _mob_touch_d && !mob_is_dragging)) ? 0.45 : 0.20);', 1)
    code = code.replace('draw_set_alpha(_btog_val ? 0.8 : 0.35);', 'draw_set_alpha(_btog_val ? 0.50 : 0.20);', 1)
    code = code.replace('''draw_set_alpha(0.85);
        draw_set_color(_btog_val ? _b_accent : c_white);''', '''draw_set_alpha(0.60);
        draw_set_color(_btog_val ? _b_accent : c_white);''', 1)

    # Force close Lover/Wife panels and stat graphs during climax
    old_ostart = """comment = "orgasm start for all cases";
if (orgasm_start == true)
{
    orgasm_start = false;
    orgasm = true;"""
    new_ostart = """comment = "orgasm start for all cases";
if (orgasm_start == true)
{
    newlover_menu_toggle = false;
    newwife_menu_toggle = false;
    orgasm_start = false;
    orgasm = true;"""
    if old_ostart in code:
        code = code.replace(old_ostart, new_ostart, 1)

    code = code.replace(
        'comment = "orgasm start for all cases";',
        'if (orgasm == true) { newlover_menu_toggle = false; newwife_menu_toggle = false; }\ncomment = "orgasm start for all cases";'
    )




    LOGGER.log("Draw_0: Enhanced thumbnail loader with dynamic frame-count fallback.", prefix="[+]")
    return code

def enforce_strict_custom_selection(code):
    """Strictly loads and locks custom models on CUSTOM button press and swap grid click."""
    if "is_legacy_custom ? legacy_custom_mating_press : custom_mating_press" in code and "legacy_custom_wife_toggle ? legacy_custom_wife_mating_press : custom_wife_mating_press" in code:
        return code
    old_case8 = '''                    case 8:
                        var custom_count = ds_list_size(custom_futas_folder);
                        if (custom_count > 0)
                        {
                            custom_futa_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_futa_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_futa_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_futa(selected_folder, custom_futa_alt_index);
                            forced_sprite = custom_mating_press;
                            custom_lover_toggle = true;
                        }
                        break;
                    case 9:
                        var vanilla_futas = [sFutaMatingPress, sFutaMatingPressDevil, sFutaMatingFurry, sFutaMatingPressSlime, sFutaMatingPressAndroid, sFutaMatingPressAlien, sFutaMatingPressClown, sFutaMatingBunny];
                        forced_sprite = vanilla_futas[irandom(array_length(vanilla_futas) - 1)];
                        custom_lover_toggle = false;
                        break;
                }
                top_skin_color_val = item_hover_1 ? random_range(200, 500) : (item_hover_2 ? random_range(175, 200) : (item_hover_3 ? random_range(80, 150) : -1));
                func_randomize_top(forced_sprite, top_skin_color_val);'''

    new_case8 = '''                    case 8:
                        custom_lover_toggle = true;
                        var custom_count = ds_list_size(custom_futas_folder);
                        if (custom_count > 0)
                        {
                            custom_futa_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_futa_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_futa_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_futa(selected_folder, custom_futa_alt_index);
                            func_apply_custom_futa_stats();
                            forced_sprite = (sprite_exists(custom_mating_press) && custom_mating_press != -1) ? custom_mating_press : ((sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press != -1) ? legacy_custom_mating_press : sFutaMatingPress);
                            top_sprite = forced_sprite;
                        }
                        break;
                    case 9:
                        var vanilla_futas = [sFutaMatingPress, sFutaMatingPressDevil, sFutaMatingFurry, sFutaMatingPressSlime, sFutaMatingPressAndroid, sFutaMatingPressAlien, sFutaMatingPressClown, sFutaMatingBunny];
                        forced_sprite = vanilla_futas[irandom(array_length(vanilla_futas) - 1)];
                        custom_lover_toggle = false;
                        break;
                }
                top_skin_color_val = item_hover_1 ? random_range(200, 500) : (item_hover_2 ? random_range(175, 200) : (item_hover_3 ? random_range(80, 150) : -1));
                if (!custom_lover_toggle)
                {
                    func_randomize_top(forced_sprite, top_skin_color_val);
                }
                else
                {
                    top_sprite = forced_sprite;
                    func_apply_custom_futa_stats();
                }'''

    if old_case8 in code:
        code = code.replace(old_case8, new_case8, 1)

    old_case6 = '''                    case 6:
                        custom_wife_toggle = true;
                        var custom_count = ds_list_size(custom_wives_folder);
                        if (custom_count > 0)
                        {
                            custom_wife_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_wife_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_wife_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_wife(selected_folder, custom_wife_alt_index);
                            func_validate_sex_position();
                            forced_bottom = custom_wife_mating_press;
                        }
                        break;
                    case 7:
                        var vanilla_wives = [sWifeMatingPress, sWifeMatingPressDevil, sWifeMatingPressFurry, sWifeMatingPressSlime, sWifeMatingPressAndroid];
                        forced_bottom = vanilla_wives[irandom(array_length(vanilla_wives) - 1)];
                        custom_wife_toggle = false;
                        legacy_custom_wife_toggle = false;
                        break;
                }
                bottom_skin_color_val = witem_hover_1 ? random_range(200, 500) : (witem_hover_2 ? random_range(175, 200) : (witem_hover_3 ? random_range(80, 150) : -1));
                func_randomize_bottom(forced_bottom, bottom_skin_color_val);'''

    new_case6 = '''                    case 6:
                        custom_wife_toggle = true;
                        var custom_count = ds_list_size(custom_wives_folder);
                        if (custom_count > 0)
                        {
                            custom_wife_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_wife_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_wife_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_wife(selected_folder, custom_wife_alt_index);
                            func_validate_sex_position();
                            func_apply_custom_wife_stats();
                            forced_bottom = (sprite_exists(custom_wife_mating_press) && custom_wife_mating_press != -1) ? custom_wife_mating_press : ((sprite_exists(legacy_custom_wife_mating_press) && legacy_custom_wife_mating_press != -1) ? legacy_custom_wife_mating_press : sWifeMatingPress);
                            bottom_sprite = forced_bottom;
                        }
                        break;
                    case 7:
                        var vanilla_wives = [sWifeMatingPress, sWifeMatingPressDevil, sWifeMatingPressFurry, sWifeMatingPressSlime, sWifeMatingPressAndroid];
                        forced_bottom = vanilla_wives[irandom(array_length(vanilla_wives) - 1)];
                        custom_wife_toggle = false;
                        legacy_custom_wife_toggle = false;
                        break;
                }
                bottom_skin_color_val = witem_hover_1 ? random_range(200, 500) : (witem_hover_2 ? random_range(175, 200) : (witem_hover_3 ? random_range(80, 150) : -1));
                if (!custom_wife_toggle)
                {
                    func_randomize_bottom(forced_bottom, bottom_skin_color_val);
                }
                else
                {
                    bottom_sprite = forced_bottom;
                    func_apply_custom_wife_stats();
                }'''

    if old_case6 in code:
        code = code.replace(old_case6, new_case6, 1)

    old_swap_click = '''                        func_load_custom_futa(_sel_folder, custom_futa_alt_index);
                        func_apply_custom_futa_stats();
                        func_top_speak("intro");
                        loads = 0;
                        sex_progress = 0;
                    }
                    else
                    {
                        custom_wife_index = _ci;
                        custom_wife_alt_index = 0;
                        var _sel_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        func_load_custom_wife(_sel_folder, custom_wife_alt_index);
                        func_apply_custom_wife_stats();'''

    new_swap_click = '''                        if (os_type == os_android || os_type == os_ios)
                        {
                            keyboard_virtual_hide();
                        }
                        selector_search_focused = false;
                        var _is_legacy_futa = file_exists(_sel_folder + "/custom_data.futa") && !file_exists(_sel_folder + "/custom_futa_mating_press_0.png");
                        is_legacy_custom = _is_legacy_futa;
                        func_load_custom_futa(_sel_folder, custom_futa_alt_index);
                        custom_lover_toggle = true;
                        forced_sprite = is_legacy_custom ? legacy_custom_mating_press : custom_mating_press;
                        if (forced_sprite != -1 && sprite_exists(forced_sprite))
                        {
                            top_sprite = forced_sprite;
                            func_apply_custom_futa_stats();
                        }
                        else
                        {
                            top_sprite = sFutaMatingPress;
                        }
                        func_top_speak("intro");
                        loads = 0;
                        sex_progress = 0;
                    }
                    else
                    {
                        if (os_type == os_android || os_type == os_ios)
                        {
                            keyboard_virtual_hide();
                        }
                        selector_search_focused = false;
                        custom_wife_index = _ci;
                        custom_wife_alt_index = 0;
                        var _sel_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        var _is_legacy_spouse = file_exists(_sel_folder + "/custom_data.spouse") || file_exists(_sel_folder + "/custom_mating_press.png");
                        if (_is_legacy_spouse)
                        {
                            func_load_custom_spouse(_sel_folder);
                            legacy_custom_wife_toggle = true;
                            custom_wife_toggle = true;
                            forced_bottom = legacy_custom_wife_mating_press;
                        }
                        else
                        {
                            func_load_custom_wife(_sel_folder, custom_wife_alt_index);
                            legacy_custom_wife_toggle = false;
                            custom_wife_toggle = true;
                            forced_bottom = custom_wife_mating_press;
                        }
                        if (forced_bottom != -1 && sprite_exists(forced_bottom))
                        {
                            bottom_sprite = forced_bottom;
                            func_apply_custom_wife_stats();
                        }
                        else
                        {
                            bottom_sprite = sWifeMatingPress;
                        }
                        func_validate_sex_position();'''

# Clean stat graph logic preserved: 100% natural hover and panel binding


    # Layering & Drawing Safety Guards against -1 crashes
    old_bs = '''var bottom_sprite;
if (custom_wife_toggle == true && legacy_custom_wife_toggle)
{
    bottom_sprite = legacy_custom_wife_mating_press;
}
else if (_spr_custom_wife_mp)
{
    bottom_sprite = custom_wife_mating_press;
}'''

    new_bs = '''var bottom_sprite = sWifeMatingPress;
if (custom_wife_toggle == true && legacy_custom_wife_toggle && sprite_exists(legacy_custom_wife_mating_press) && legacy_custom_wife_mating_press != -1)
{
    bottom_sprite = legacy_custom_wife_mating_press;
}
else if (custom_wife_toggle == true && sprite_exists(custom_wife_mating_press) && custom_wife_mating_press != -1)
{
    bottom_sprite = custom_wife_mating_press;
}'''
    if old_bs in code:
        code = code.replace(old_bs, new_bs, 1)

    old_bangs = '''    draw_sprite_ext(bangs_sprite, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 13 : 9, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);'''
    new_bangs = '''    if (bangs_sprite != -1 && sprite_exists(bangs_sprite))
        draw_sprite_ext(bangs_sprite, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 13 : 9, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);'''
    if old_bangs in code:
        code = code.replace(old_bangs, new_bangs, 1)

    old_w_bangs6 = '''    else
    {
        draw_sprite_ext(wife_bangs_sprite, 6, portrait_x + face_x, portrait_y + (bottom_breath * 64) + face_y, 1 * custom_wife_portrait_scale, 1 * custom_wife_portrait_scale, 0, bottom_hair, 1);
    }'''
    new_w_bangs6 = '''    else
    {
        if (wife_bangs_sprite != -1 && sprite_exists(wife_bangs_sprite))
            draw_sprite_ext(wife_bangs_sprite, 6, portrait_x + face_x, portrait_y + (bottom_breath * 64) + face_y, 1 * custom_wife_portrait_scale, 1 * custom_wife_portrait_scale, 0, bottom_hair, 1);
    }'''
    if old_w_bangs6 in code:
        code = code.replace(old_w_bangs6, new_w_bangs6, 1)

    old_w_bangs9 = '''    else
    {
        draw_sprite_ext(wife_bangs_sprite, 9, portrait_x + face_x, portrait_y + (bottom_breath * 64) + face_y, 1 * custom_wife_portrait_scale, 1 * custom_wife_portrait_scale, 0, bottom_hair, 1);
    }'''
    new_w_bangs9 = '''    else
    {
        if (wife_bangs_sprite != -1 && sprite_exists(wife_bangs_sprite))
            draw_sprite_ext(wife_bangs_sprite, 9, portrait_x + face_x, portrait_y + (bottom_breath * 64) + face_y, 1 * custom_wife_portrait_scale, 1 * custom_wife_portrait_scale, 0, bottom_hair, 1);
    }'''
    if old_w_bangs9 in code:
        code = code.replace(old_w_bangs9, new_w_bangs9, 1)

    old_w_eyes = '''    else if (!legacy_custom_wife_toggle)
    {
        draw_sprite_ext(func_get_portrait_iris(wife_eye_sprite), eye_id, eye_x, eye_y, 1, 1, 0, wife_eye_color, 1);
        draw_sprite(wife_eye_sprite, eye_id, eye_x, eye_y);
    }'''
    new_w_eyes = '''    else if (!legacy_custom_wife_toggle)
    {
        var _w_iris = func_get_portrait_iris(wife_eye_sprite);
        if (_w_iris != -1 && sprite_exists(_w_iris))
            draw_sprite_ext(_w_iris, eye_id, eye_x, eye_y, 1, 1, 0, wife_eye_color, 1);
        if (wife_eye_sprite != -1 && sprite_exists(wife_eye_sprite))
            draw_sprite(wife_eye_sprite, eye_id, eye_x, eye_y);
    }'''

    

    if old_swap_click in code:
        code = code.replace(old_swap_click, new_swap_click, 1)

    # Fix UI panel CUSTOM buttons for both Lover (case 8) and Wife (case 6)
    old_nl_custom = '''                    case 8:
                        var custom_count = ds_list_size(custom_futas_folder);
                        if (custom_count > 0)
                        {
                            custom_futa_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_futa_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_futa_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_futa(selected_folder, custom_futa_alt_index);
                            forced_sprite = custom_mating_press;
                            custom_lover_toggle = true;
                        }
                        break;'''

    new_nl_custom = '''                    case 8:
                        var custom_count = ds_list_size(custom_futas_folder);
                        if (custom_count > 0)
                        {
                            custom_futa_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_futa_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_futa_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_futa(selected_folder, custom_futa_alt_index);
                            func_apply_custom_futa_stats();
                            forced_sprite = (sprite_exists(custom_mating_press) && custom_mating_press != -1) ? custom_mating_press : ((sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press != -1) ? legacy_custom_mating_press : sFutaMatingPress);
                            top_sprite = forced_sprite;
                            custom_lover_toggle = true;
                        }
                        break;'''
    if old_nl_custom in code:
        code = code.replace(old_nl_custom, new_nl_custom, 1)

    old_nw_custom = '''                    case 6:
                        custom_wife_toggle = true;
                        var custom_count = ds_list_size(custom_wives_folder);
                        if (custom_count > 0)
                        {
                            custom_wife_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_wife_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_wife_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_wife(selected_folder, custom_wife_alt_index);
                            func_validate_sex_position();
                            forced_bottom = custom_wife_mating_press;
                        }
                        break;'''

    new_nw_custom = '''                    case 6:
                        custom_wife_toggle = true;
                        var custom_count = ds_list_size(custom_wives_folder);
                        if (custom_count > 0)
                        {
                            custom_wife_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_wife_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_wife_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_wife(selected_folder, custom_wife_alt_index);
                            func_validate_sex_position();
                            func_apply_custom_wife_stats();
                            forced_bottom = (sprite_exists(custom_wife_mating_press) && custom_wife_mating_press != -1) ? custom_wife_mating_press : ((sprite_exists(legacy_custom_wife_mating_press) && legacy_custom_wife_mating_press != -1) ? legacy_custom_wife_mating_press : sWifeMatingPress);
                            bottom_sprite = forced_bottom;
                        }
                        break;'''
    if old_nw_custom in code:
        code = code.replace(old_nw_custom, new_nw_custom, 1)

    return code

def inject_complete_overlay(code):
    """Injects or updates the mobile touch overlay FAB, quick bar, drawer, and command execution."""
    target_fab = 'if (_fab_over && _mob_touch_p)\n{\n    mob_expanded = !mob_expanded;\n    mob_scroll_y = 0;\n    mob_is_dragging = false;\n}'
    quick_r_n_c_o = '''if (_fab_over && _mob_touch_p)
{
    mob_expanded = !mob_expanded;
    mob_scroll_y = 0;
    mob_is_dragging = false;
}

// Quick Access Buttons: [R] [N] [C] [O] displayed to the left of the main overlay button
if (mob_expanded)
{
    var _qb_w = 32;
    var _qb_h = 26;
    var _qb_gap = 5;
    var _qbtns = [
        ["R", ord("R"), make_color_rgb(220, 60, 60)],      // Reset
        ["N", ord("N"), _c_mob_accent],                    // Climax
        ["C", ord("C"), make_color_rgb(180, 0, 255)],     // Wife Climax
        ["O", ord("O"), make_color_rgb(0, 210, 110)]       // Ovulate
    ];

    for (var _qi = 0; _qi < 4; _qi++)
    {
        var _qbx1 = _fab_x1 - ((4 - _qi) * (_qb_w + _qb_gap));
        var _qby1 = _fab_y1;
        var _qbx2 = _qbx1 + _qb_w;
        var _qby2 = _qby1 + _qb_h;
        
        var _qb_over = point_in_rectangle(_mob_tx, _mob_ty, _qbx1, _qby1, _qbx2, _qby2);
        var _qb_data = _qbtns[_qi];
        var _qb_lbl = _qb_data[0];
        var _qb_key = _qb_data[1];
        var _qb_col = _qb_data[2];

        draw_set_alpha((_qb_over && _mob_touch_d) ? 0.85 : 0.65);
        draw_set_color((_qb_over && _mob_touch_d) ? _c_mob_btn_press : _c_mob_bg);
        draw_roundrect_ext(_qbx1, _qby1, _qbx2, _qby2, 8, 8, false);

        draw_set_alpha(0.85);
        draw_set_color(_qb_col);
        draw_roundrect_ext(_qbx1, _qby1, _qbx2, _qby2, 8, 8, true);

        draw_set_color(c_white);
        draw_text((_qbx1 + _qbx2) * 0.5, (_qby1 + _qby2) * 0.5, _qb_lbl);

        if (_qb_over && _mob_touch_p)
        {
            if (_qb_key == ord("R"))
            {
                func_reset_sex_stats();
                sex_progress = 0;
                edge_charge = 0;
            }
            else if (_qb_key == ord("C"))
            {
                func_wife_climax();
            }
            else if (_qb_key == ord("O"))
            {
                func_ovulate();
            }
            else if (_qb_key == ord("N"))
            {
                orgasm_start = true;
                orgasm = true;
                keyboard_key_press(ord("N"));
                mob_release_key = ord("N");
            }
            else
            {
                keyboard_key_press(_qb_key);
                mob_release_key = _qb_key;
            }
        }
    }
}'''

    # Do not inject duplicate quick access bar (already present in base engine)
    # Just update the single existing quick bar's [N] button to force-close panels
    code = code.replace(
        'else if (_qb_key == 78)\n            {\n                orgasm_start = true;\n                orgasm = true;\n                keyboard_key_press(ord("N"));\n                mob_release_key = 78;\n            }',
        'else if (_qb_key == 78)\n            {\n                newlover_menu_toggle = false;\n                newwife_menu_toggle = false;\n                orgasm_start = true;\n                orgasm = true;\n                keyboard_key_press(ord("N"));\n                mob_release_key = 78;\n            }',
        1
    )

    old_btns_def = '    var _btns = [["[N] CLIMAX", 78, 0, 0, _c_mob_accent], ["[M] MAN:" + _man_status, 77, 1, manual_mode > 0, make_color_rgb(0, 210, 110)], ["[RADIAL MENU]", "RADIAL", 1, radial_menu_open, make_color_rgb(0, 180, 230)], ["[T] " + _peek_status, 84, 0, 0, 16777215], ["[C] WIFE CLIM", 67, 0, 0, 16777215], ["[O] OVULATE", 79, 0, 0, 16777215], ["[G] GHOST", 71, 1, futa_ghost_toggle, _c_mob_accent], ["[Q] REROLL", 81, 0, 0, 16777215], ["[H] HITBOX", 72, 1, mob_hitbox_active, make_color_rgb(160, 0, 220)], ["[R] RESET", 82, 0, 0, 16777215], ["[ESC] BACK", 27, 0, 0, make_color_rgb(220, 60, 60)], ["[ENTER] SET", 13, 0, 0, make_color_rgb(60, 180, 80)]];'
    new_btns_def = '''    var _btns = [
        ["[M] MAN:" + _man_status, 77, 1, manual_mode > 0, make_color_rgb(0, 210, 110)],
        ["[T] " + _peek_status, 84, 0, 0, 16777215],
        ["[G] GHOST", 71, 1, futa_ghost_toggle, _c_mob_accent],
        ["[Q] REROLL", 81, 0, 0, 16777215],
        ["[H] HITBOX", 72, 1, mob_hitbox_active, make_color_rgb(160, 0, 220)],
        ["[RESET OPTIONS]", "RESET_DEFAULTS", 0, 0, make_color_rgb(255, 140, 0)]
    ];
    if (variable_instance_exists(id, "manual_mode") && manual_mode > 0 && variable_instance_exists(id, "radial_menu_open"))
    {
        array_insert(_btns, 1, ["[RADIAL MENU]", "RADIAL", 1, radial_menu_open, make_color_rgb(0, 180, 230)]);
    }

    // Auto-close overlay menu if anywhere outside the overlay boxes is tapped
    var _in_quick_bar = point_in_rectangle(_mob_tx, _mob_ty, _fab_x1 - (4 * (32 + 5)), _fab_y1, _fab_x1, _fab_y2);
    if (_mob_touch_p && !_in_drawer && !_in_quick_bar && !_fab_over)
    {
        mob_expanded = false;
        mob_scroll_y = 0;
        mob_is_dragging = false;
    }'''

    if old_btns_def in code:
        code = code.replace(old_btns_def, new_btns_def, 1)

    code = code.replace(
        "if (mob_lp_timer == 22 && !radial_menu_open && title == false && orgasm == false)",
        "if (mob_lp_timer == 22 && !radial_menu_open && title == false && orgasm == false && variable_instance_exists(id, \"manual_mode\") && manual_mode > 0)"
    )

    old_btn_exec = """        if (_btn_over && _click_occurred)
        {
            if (_bkcode == "RADIAL")
            {
                if (variable_instance_exists(id, "radial_menu_open"))
                {
                    radial_menu_open = !radial_menu_open;
                    radial_sub_menu = "";
                }
                mob_expanded = false;
            }
            else if (_bkcode == 72)
            {
                mob_hitbox_active = !mob_hitbox_active;
            }
            else
            {
                keyboard_key_press(_bkcode);
                mob_release_key = _bkcode;
            }
        }"""

    new_btn_exec = """        if (_btn_over && _click_occurred)
        {
            if (_bkcode == "RADIAL")
            {
                if (variable_instance_exists(id, "radial_menu_open"))
                {
                    radial_menu_open = !radial_menu_open;
                    radial_sub_menu = "";
                }
                mob_expanded = false;
            }
            else if (_bkcode == 77) // [M] MAN - directly toggles manual mode WITHOUT closing drawer!
            {
                if (variable_instance_exists(id, "manual_mode"))
                {
                    manual_mode = (manual_mode == 0) ? 1 : ((manual_mode == 1) ? 2 : 0);
                    if (variable_instance_exists(id, "manual_ui_visible"))
                        manual_ui_visible = (manual_mode > 0);
                }
            }
            else if (_bkcode == 84) // [T] PEEK - directly toggles peek screen with zero warning interruption
            {
                title = !title;
                peek_closed_during_play = true;
                disclaimer = false;
                mob_expanded = false;
            }
            else if (_bkcode == 71) // [G] GHOST - directly toggles ghost mode WITHOUT closing drawer!
            {
                if (variable_instance_exists(id, "futa_ghost_toggle"))
                {
                    futa_ghost_toggle = !futa_ghost_toggle;
                    futa_ghost_alpha = futa_ghost_toggle ? 0.5 : 1;
                }
            }
            else if (_bkcode == 81) // [Q] REROLL - directly rerolls character favoring custom assets WITHOUT closing drawer!
            {
                var _c_count = ds_list_size(custom_futas_folder);
                if (_c_count > 0 && random(1) < 0.85)
                {
                    custom_lover_toggle = true;
                    custom_futa_index = irandom(_c_count - 1);
                    var _rf = ds_list_find_value(custom_futas_folder, custom_futa_index);
                    var _alt_max = 1;
                    while (file_exists(string(_rf) + "/custom_futa_mating_press_alt_" + string(_alt_max) + ".png"))
                    {
                        _alt_max++;
                    }
                    custom_futa_alt_index = irandom(_alt_max - 1);
                    func_load_custom_futa(_rf, custom_futa_alt_index);
                    forced_sprite = is_legacy_custom ? legacy_custom_mating_press : custom_mating_press;
                    top_sprite = forced_sprite;
                    func_apply_custom_futa_stats();
                }
                else
                {
                    custom_lover_toggle = false;
                    func_randomize_top();
                }
                sex_progress = 0;
                edge_charge = 0;
                loads = 0;
            }
            else if (_bkcode == 72) // [H] HITBOX - directly toggles hitbox AND closes overlay!
            {
                mob_hitbox_active = !mob_hitbox_active;
                mob_expanded = false;
            }
            else if (_bkcode == "RESET_DEFAULTS") // [RESET OPTIONS] - resets ALL options and non-default variables to defaults
            {
                // Audio
                global.vol_master = 1;
                global.vol_sfx = 1;
                global.vol_voice = 1;
                global.vol_ambient = 1;
                global.audio_master_on = true;
                global.audio_sfx_on = true;
                global.audio_voice_on = true;

                // Visuals & Types
                skip_disclaimer = false;
                xray = true;
                futa_pussy_toggle = true;
                futa_ghost_toggle = false;
                futa_ghost_alpha = 1;

                // Mechanics
                knotting_toggle = true;
                knotted_max_time = 600;
                womb_inflation_toggle = true;
                womb_inflation_scale = 1;
                slip_toggle = false;
                slip_chance = 1;
                reenter_toggle = false;
                reenter_max_timer = false;
                condom_break_toggle = false;
                condom_break_threshold = 10;

                // Values
                pump_delay = 90;
                cum_shot_mult = 1;
                stroke_depth = 1;
                stroke_speed = 1;

                // Features
                rand_pumps_toggle = false;
                hearts_toggle = true;
                frustration_toggle = true;
                global.pop_sound_toggle = true;
                kiss_toggle = 1;
                drip_toggle = true;
                cum_batching_toggle = false;
                custom_clench_toggle = 0;
                continuous_toggle = false;

                // Texture Pack
                if (chosen_texture_pack != "default")
                {
                    func_texture_pack_replace("default");
                    chosen_texture_pack = "default";
                }

                // Dialogue
                oDialogueManager.dialogue_toggle = true;
                char_dialogue_toggle = true;
                global.dialogue_display_index = 0;
                dialogue_display_index = 0;
                global.speaker_type_index = 0;
                oDialogueManager.dialogue_cooldown = 30;
                global.dialogue_additional_duration = 0;
                text_scale_l = 1;
                text_scale_w = 1;
                max_lover_dialogue_width = 200;
                max_wife_dialogue_width = 200;
                top_dlg_x = 0;
                top_dlg_y = 0;
                wife_dlg_x = 3;
                wife_dlg_y = 0;
                oDialogueManager.top_dialogue_color = 12976127;
                oDialogueManager.wife_dialogue_color = 13408767;
                oDialogueManager.current_top_color = 12976127;
                oDialogueManager.current_wife_color = 13408767;
                oDialogueManager.chosen_dialogue = "aathefintree.json";
                oDialogueManager.func_load_dialogue("aathefintree.json");

                // Bunny Panel
                bunny_panel_x_saved = 300;
                bunny_panel_y_saved = 30;
                bunny_small_x_saved = 300;
                bunny_small_y_saved = 25;

                // Custom Sounds
                cs_futa_pack_index = 0;
                cs_futa_alt_index = 0;
                cs_moan_chance_slow = 0.4;
                cs_moan_chance_fast = 0.55;
                cs_orgasm_grunt_chance = 0.45;
                cs_wife_pack_index = 0;
                cs_wife_alt_index = 0;
                cs_wife_moan_chance_slow = 0.35;
                cs_wife_moan_chance_fast = 0.55;
                cs_wife_kiss_enabled = true;

                // Background Colors
                bg_randomize_colors = true;
                saved_bg_wallpaper = -1;
                saved_bg_carpet = -1;
                saved_bg_trim = -1;
                saved_bg_dresser = -1;
                saved_bg_mattress = -1;
                saved_bg_frame = -1;
                saved_bg_ship = -1;
                saved_bg_console = -1;
                saved_bg_screen = -1;
                saved_bg_glass = -1;
                saved_bg_vip_wall = -1;
                saved_bg_vip_stage = -1;
                saved_bg_vip_pole = -1;
                saved_bg_vip_underwear = -1;
                saved_bg_vip_condoms = -1;
                saved_bg_vip_lotion = -1;
                saved_bg_vip_mattress = -1;
                saved_bg_vip_frame = -1;
                saved_bg_beach_water = -1;
                saved_bg_beach_sky = -1;
                saved_bg_beach_sun = -1;
                saved_bg_beach_clouds = -1;
                saved_bg_beach_sand = -1;
                saved_bg_beach_stuff = -1;
                saved_bg_office_wall = -1;
                saved_bg_office_floor = -1;
                saved_bg_office_desk = -1;
                saved_bg_dungeon_floor = -1;
                saved_bg_dungeon_wall = -1;
                saved_bg_dungeon_gate = -1;
                saved_bg_dungeon_chest = -1;
                saved_bg_dungeon_chesttrim = -1;
                saved_bg_dungeon_torch = -1;
                saved_bg_dungeon_flame = -1;

                // Radio
                radio_track_index = 0;
                radio_volume = 1;
                radio_shuffle = 0;

                // Manual Mode & Values2
                manual_mode = 0;
                manual_ui_visible = false;
                manual_pump_speed = 4;
                manual_thrust_sens = 0.05;
                manual_thrust_strength = 2;
                manual_hip_sens = 0.5;
                combo_text_max = 0;
                max_combo_display = 0;
                manual_last_mode = 1;
                manual_auto_pumps = false;
                machinegun_toggle = false;
                mg_interval_min = 4;
                mg_interval_max = 14;
                mg_spread = 0.2;
                mg_burst_min = 1;
                mg_burst_max = 2;
                overflow_delay = 0;

                // Responses
                wife_climax_stamina = 100;
                wife_pleasure_threshold = 100;
                wife_pleasure_max = 100;
                wife_womb_capacity = 20;
                fill_max = 20;

                // Gameplay State
                func_reset_sex_stats();
                sex_progress = 0;
                edge_charge = 0;
                loads = 0;
                wife_climax_counter = 0;
                impregnation_counter = 0;
                body_jiggle = 0;

                // Panel Positions & Menu States
                newlover_menu_cx = 65;
                newlover_menu_cy_end_offset = 50;
                newwife_menu_x = room_width - 260;
                newwife_menu_y = room_height - 100;
                options_toggle = false;
                radial_menu_open = false;
                radial_sub_menu = "";
                background_menu_toggle = false;
                position_menu_toggle = false;
                pill_menu_toggle = false;
                dialogue_menu_toggle = false;
                radio_toggle = false;
                tab_quicknav_open = false;
                actions_menu_toggle = false;
                color_picker_active = false;
                futa_selector_open = false;
                newlover_menu_toggle = false;
                newwife_menu_toggle = false;
                mob_hitbox_active = false;
                keyboard_key_release(ord("H"));
                mob_expanded = false;

                // Delete persisted settings file and save clean defaults
                if (file_exists("setting_data.sav"))
                    file_delete("setting_data.sav");
                if (file_exists(working_directory + "/setting_data.sav"))
                    file_delete(working_directory + "/setting_data.sav");
                func_save_settings();

                oAudioManager.play_sfx(asset_get_index("StarshipOUT"), 1);
            }
            else
            {
                keyboard_key_press(_bkcode);
                mob_release_key = _bkcode;
            }
        }"""

    if old_btn_exec in code:
        code = code.replace(old_btn_exec, new_btn_exec, 1)

    return code

# -----------------------------------------------------------------------------
# APK CRYPTOGRAPHIC SIGNING
# -----------------------------------------------------------------------------
def sign_apk_file(apk_path):
    apk_path = Path(apk_path).resolve()
    patcher_dir = Path(__file__).parent.resolve()
    core_dir = patcher_dir / "core"
    keystore = core_dir / "apkpatcher.keystore" if (core_dir / "apkpatcher.keystore").exists() else patcher_dir / "apkpatcher.keystore"
    pass_file = core_dir / "apkpatcher.keystore.pass" if (core_dir / "apkpatcher.keystore.pass").exists() else patcher_dir / "apkpatcher.keystore.pass"

    if not keystore.exists() or not pass_file.exists():
        LOGGER.error(f"Signing keystore not found at {keystore}.")
        return

    keystore_pass = pass_file.read_text(encoding="utf-8").strip()
    java = get_jdk_tool("java")
    uber_jar = find_uber_apk_signer()

    LOGGER.log(f"Aligning & signing APK: {apk_path.name}...")
    if uber_jar:
        cmd = [
            java, "-jar", uber_jar,
            "-a", str(apk_path),
            "--ks", str(keystore),
            "--ksAlias", "apkpatcherkey",
            "--ksPass", keystore_pass,
            "--ksKeyPass", keystore_pass,
            "--allowResign", "--overwrite"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            LOGGER.error(f"Signing failed:\n{res.stdout}\n{res.stderr}")
            raise RuntimeError("APK Signing failed.")
    else:
        LOGGER.error("uber-apk-signer.jar not found.")
        raise FileNotFoundError("uber-apk-signer.jar missing.")

    LOGGER.log("APK cryptographically aligned and signed with v1, v2, and v3 schemes!", prefix="[+]")

# -----------------------------------------------------------------------------
# CORE PATCHER EXECUTION (SUPPORTS FOLDER + BASE APK OR STANDALONE APK)
# -----------------------------------------------------------------------------
def patch_game_apk(utmt_cli, source_apk, target_apk, source_folder=None, enable_toy_telemetry=False, opts=None):
    if opts is None:
        opts = {
            "core_manifest": True,
            "scaling": True,
            "stability": True,
            "climax_and_panels": True,
            "css_and_favs": True,
            "phone_import": True,
            "toy_telemetry": enable_toy_telemetry
        }
    enable_toy_telemetry = opts.get("toy_telemetry", False)
    source_apk = Path(source_apk).resolve()
    target_apk = Path(target_apk).resolve()

    # Pristine base backup preserved in output/ without polluting input/
    output_dir = Path(__file__).parent.resolve() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    bak_apk = output_dir / f"{source_apk.stem}_base_backup.apk.bak"
    if not bak_apk.exists():
        shutil.copyfile(source_apk, bak_apk)

    LOGGER.log(f"Processing Game APK: {source_apk.name} -> {target_apk.name}")
    if source_folder:
        LOGGER.log(f"Merging custom assets from folder: {source_folder}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_droid = Path(tmpdir) / "game.droid"
        patched_droid = Path(tmpdir) / "game_final.droid"

        patcher_dir = Path(__file__).parent.resolve()
        core_dir = patcher_dir / "core"
        input_dir = patcher_dir / "input"
        bundle_file = core_dir / "mobile_engine.bundle"

        # 1. Extract default game.droid from base APK
        with zipfile.ZipFile(source_apk, "r") as zin:
            if "assets/game.droid" in zin.namelist():
                tmp_droid.write_bytes(zin.read("assets/game.droid"))

        # 2. Check if user provided PC mod folder containing data.win (e.g. Deeproom 4.0)
        has_deeproom4 = False
        found_data_win = None
        if source_folder:
            p_sf = Path(source_folder)
            cand = None
            if (p_sf / "data.win").exists():
                cand = p_sf / "data.win"
            else:
                for sub in p_sf.iterdir():
                    if sub.is_dir() and (sub / "data.win").exists():
                        cand = sub / "data.win"
                        break
            if cand and cand.is_file():
                # Only ingest PC data.win if it is Deeproom 4.0 (>40MB).
                # v1.5 data.win (23.5MB) lacks oDialogueManager and causes native runner crashes on boot.
                if cand.stat().st_size > 40 * 1024 * 1024:
                    found_data_win = cand
                else:
                    LOGGER.log(f"Notice: Found {cand.name} ({cand.stat().st_size/(1024*1024):.1f} MB) in {cand.parent.name}. Using mobile engine template for stability.", prefix="[*]")

        code_dir = Path(tmpdir) / "CodeEntries"
        code_dir.mkdir(parents=True, exist_ok=True)

        is_v15_target = False
        if source_folder:
            ver_det = detect_mod_engine_version(source_folder)
            is_v15_target = (ver_det == "1.5")
        elif "1_5" in source_apk.name or "1.5" in source_apk.name:
            is_v15_target = True

        if is_v15_target:
            LOGGER.log("Detected v1.5 architecture: applying native Android manifest streaming to v1.5 engine...", prefix="[*]")
            try:
                dump_res = subprocess.run([utmt_cli, "dump", str(tmp_droid), "-c", "gml_Object_oFutaMatingPress_Create_0", "-o", tmpdir], capture_output=True, text=True)
                c_target = code_dir / "gml_Object_oFutaMatingPress_Create_0.gml"
                if c_target.exists():
                    v15_code = c_target.read_text(encoding="utf-8")
                    old_scan = '    if (true && mobile == false)'
                    new_scan = '''    var _manifest_p = "custom/_manifest.txt";
    var _f_mani = file_text_open_read(_manifest_p);
    if (_f_mani == -1 && game_dir != "")
    {
        _f_mani = file_text_open_read(game_dir + "/custom/_manifest.txt");
    }
    if (_f_mani != -1)
    {
        while (!file_text_eof(_f_mani))
        {
            var _m_line = string_replace_all(string_replace_all(file_text_readln(_f_mani), "\\r", ""), "\\n", "");
            while (string_char_at(_m_line, 1) == " ") _m_line = string_delete(_m_line, 1, 1);
            while (string_char_at(_m_line, string_length(_m_line)) == " ") _m_line = string_delete(_m_line, string_length(_m_line), 1);
            if (_m_line != "" && _m_line != "_manifest.txt")
            {
                var _file = (os_type == os_android || os_type == os_ios) ? ("custom/" + _m_line) : (game_dir + "/custom/" + _m_line);
                if (file_exists(_file + "/custom_data.futa"))
                {
                    if (ds_list_find_index(custom_lover_folders, _file) == -1)
                    {
                        ds_list_add(custom_lover_folders, _file);
                    }
                }
                else if (file_exists(_file + "/custom_data.spouse"))
                {
                    if (ds_list_find_index(custom_partner_folders, _file) == -1)
                    {
                        ds_list_add(custom_partner_folders, _file);
                    }
                }
                else if (file_exists(_file + "/custom_data.bedroom"))
                {
                    if (ds_list_find_index(custom_bedroom_folders, _file) == -1)
                    {
                        ds_list_add(custom_bedroom_folders, _file);
                    }
                }
            }
        }
        file_text_close(_f_mani);
        if (ds_list_size(custom_lover_folders) > 0 || ds_list_size(custom_partner_folders) > 0 || ds_list_size(custom_bedroom_folders) > 0)
        {
            custom_sprite_loaded = true;
            tutorial = false;
        }
    }
    else if (true)'''
                    if old_scan in v15_code:
                        v15_code = v15_code.replace(old_scan, new_scan, 1)
                        c_target.write_text(v15_code, encoding="utf-8")
                        rep_res = subprocess.run([utmt_cli, "replace", str(tmp_droid), "-c", f"gml_Object_oFutaMatingPress_Create_0={c_target}", "-o", str(patched_droid)], capture_output=True, text=True)
                        if rep_res.returncode == 0:
                            has_deeproom4 = True
                            LOGGER.log("v1.5 native engine compiled with in-memory Android manifest streaming!", prefix="[+]")
            except Exception as e_v15:
                LOGGER.log(f"Notice: v1.5 native patch encountered: {e_v15}", prefix="[!]")

        elif bundle_file.exists():
            if found_data_win and found_data_win.exists():
                LOGGER.log(f"Found PC engine data in mods folder: {found_data_win.name} ({found_data_win.parent.name})", prefix="[+]")
                LOGGER.log("Upgrading PC data.win to mobile engine via mobile_engine.bundle...", prefix="[*]")
                shutil.copyfile(found_data_win, tmp_droid)
            else:
                LOGGER.log("Upgrading base APK game.droid to full mobile engine via mobile_engine.bundle...", prefix="[*]")

            try:
                payload = json.loads(zlib.decompress(bundle_file.read_bytes()).decode('utf-8'))
                rep_args = [utmt_cli, "replace", str(tmp_droid)]

                for e_name, script_content in payload.items():
                    c_target = code_dir / e_name
                    # Allow optional telemetry toggle override if requested
                    if not enable_toy_telemetry and "buttplug_socket = network_create_socket" in script_content:
                        script_content = script_content.replace("buttplug_socket = network_create_socket", "// buttplug_socket disabled")
                    c_target.write_text(script_content, encoding="utf-8")
                    entry_id = e_name.replace('.gml', '')
                    rep_args.extend(["-c", f"{entry_id}={c_target}"])

                rep_args.extend(["-o", str(patched_droid)])
                res_rep = subprocess.run(rep_args, capture_output=True, text=True)
                if res_rep.returncode == 0:
                    has_deeproom4 = True
                    LOGGER.log("Engine compiled to full mobile engine (in-memory manifests, CSS grid, and touch overlay active)!", prefix="[+]")
                else:
                    LOGGER.log(f"Notice: Bundle compile returned non-zero ({res_rep.stderr[:150]}). Falling back to dynamic patcher.", prefix="[!]")
            except Exception as b_err:
                LOGGER.log(f"Notice: Bundle application encountered: {b_err}. Falling back to dynamic patcher.", prefix="[!]")

        # 3. Fallback / Vanilla 1.4 compilation pipeline
        if not has_deeproom4:
            optional_droids = [f for f in input_dir.glob("*.droid") if f.is_file()]
            if optional_droids:
                LOGGER.log(f"Using optional test/verify engine data from input/: {optional_droids[0].name}", prefix="[*]")
                shutil.copyfile(optional_droids[0], tmp_droid)

            LOGGER.log("Dumping core game scripts with UndertaleModCli...")
            dump_cmd = [
                utmt_cli, "dump", str(tmp_droid),
                "-c", "gml_Object_oFutaMatingPress_Create_0",
                "-c", "gml_Object_oFutaMatingPress_Step_0",
                "-c", "gml_Object_oFutaMatingPress_Draw_0"
            ]
            chk = subprocess.run([utmt_cli, "dump", str(tmp_droid), "-c", "gml_Object_oDialogueManager_Create_0", "-o", tmpdir], capture_output=True)
            if (code_dir / "gml_Object_oDialogueManager_Create_0.gml").exists():
                has_deeproom4 = True
                dump_cmd.extend(["-c", "gml_Object_oBackground_Create_0", "-c", "gml_Object_oDialogueManager_Create_0"])
            dump_cmd.extend(["-o", tmpdir])
            subprocess.run(dump_cmd, check=True, capture_output=True)

            create_file = code_dir / "gml_Object_oFutaMatingPress_Create_0.gml"
            step_file = code_dir / "gml_Object_oFutaMatingPress_Step_0.gml"
            draw_file = code_dir / "gml_Object_oFutaMatingPress_Draw_0.gml"
            bg_file = code_dir / "gml_Object_oBackground_Create_0.gml"
            dlg_file = code_dir / "gml_Object_oDialogueManager_Create_0.gml"

            create_code = create_file.read_text(encoding="utf-8")
            create_code = patch_create_code(create_code, enable_toy_telemetry=enable_toy_telemetry, opts=opts)
            create_file.write_text(create_code, encoding="utf-8")

            step_code = step_file.read_text(encoding="utf-8")
            step_code = patch_step_code(step_code)
            step_file.write_text(step_code, encoding="utf-8")

            draw_code = draw_file.read_text(encoding="utf-8")
            draw_code = patch_draw_code(draw_code, enable_toy_telemetry=enable_toy_telemetry, opts=opts)
            draw_file.write_text(draw_code, encoding="utf-8")

            if bg_file.exists():
                bg_code = bg_file.read_text(encoding="utf-8")
                bg_code = patch_background_code(bg_code)
                bg_file.write_text(bg_code, encoding="utf-8")

            if dlg_file.exists():
                dlg_code = dlg_file.read_text(encoding="utf-8")
                dlg_code = patch_dialogue_code(dlg_code)
                dlg_file.write_text(dlg_code, encoding="utf-8")

            LOGGER.log("Recompiling patched scripts into game.droid...")
            rep_cmd = [
                utmt_cli, "replace", str(tmp_droid),
                "-c", f"gml_Object_oFutaMatingPress_Create_0={create_file}",
                "-c", f"gml_Object_oFutaMatingPress_Step_0={step_file}",
                "-c", f"gml_Object_oFutaMatingPress_Draw_0={draw_file}"
            ]
            if bg_file.exists():
                rep_cmd.extend(["-c", f"gml_Object_oBackground_Create_0={bg_file}"])
            if dlg_file.exists():
                rep_cmd.extend(["-c", f"gml_Object_oDialogueManager_Create_0={dlg_file}"])
            rep_cmd.extend(["-o", str(patched_droid)])
            subprocess.run(rep_cmd, check=True, capture_output=True)
            LOGGER.log("game.droid recompiled successfully!", prefix="[+]")

        # 5. Gather custom assets and manifests if source folder provided
        custom_assets = []
        manifest_map = {}
        if source_folder:
            quarantine_folder = Path(__file__).parent.resolve() / "output" / "quarantine"
            p_cnt, q_cnt, q_list = quarantine_incompatible_packs(source_folder, quarantine_folder)
            if q_cnt > 0:
                LOGGER.log(f"Pre-flight Pack Validation: Quarantined {q_cnt} incompatible/non-portable pack(s) into '{quarantine_folder}'.", prefix="[+]")
                LOGGER.log(f"Pre-flight Pack Validation: Retained {p_cnt} 100% portable ModRoomStyle pack(s).", prefix="[+]")
            else:
                LOGGER.log(f"Pre-flight Pack Validation: All {p_cnt} pack(s) verified 100% portable and compatible.", prefix="[+]")
            LOGGER.log(f"Scanning '{Path(source_folder).name}' for custom characters, sounds, music, and dialogues...")
            custom_assets = gather_custom_assets(source_folder, is_v15=is_v15_target)
            LOGGER.log(f"Discovered {len(custom_assets)} custom asset file(s).")
            manifest_map = generate_manifest_data(source_folder, is_v15=is_v15_target)
            LOGGER.log(f"Generated {len(manifest_map)} Android _manifest.txt index file(s).", prefix="[+]")

        # 6. Repackage into final APK
        if target_apk.exists():
            try:
                target_apk.unlink()
            except Exception:
                pass
        idsig = target_apk.with_suffix(".apk.idsig")
        if idsig.exists():
            try:
                idsig.unlink()
            except Exception:
                pass

        LOGGER.log(f"Repackaging into Final APK: {target_apk.name}...")
        written_paths = set()

        with zipfile.ZipFile(source_apk, "r") as zin:
            total_items = len(zin.infolist()) + len(custom_assets) + len(manifest_map)
            current = 0

            # Build a set of all lowercased paths that will be provided by custom assets or manifests
            override_paths = {apk_p.lower() for _, apk_p in custom_assets}
            override_paths.update({apk_p.lower() for apk_p in manifest_map})

            apk_comp = zipfile.ZIP_STORED if opts.get("fast_packaging") else zipfile.ZIP_DEFLATED
            with zipfile.ZipFile(target_apk, "w", compression=apk_comp) as zout:
                # 6a. Copy base APK contents (skipping signing, game.droid, and any overridden custom assets/manifests)
                for item in zin.infolist():
                    current += 1
                    if current % 400 == 0 or current >= total_items:
                        print_progress(current, total_items, prefix="Packaging Final APK")

                    fname_lower = item.filename.lower()
                    if fname_lower.startswith("meta-inf/"):
                        continue
                    if fname_lower in override_paths or fname_lower in written_paths:
                        continue

                    if fname_lower == "assets/game.droid":
                        zout.write(patched_droid, "assets/game.droid", compress_type=item.compress_type)
                        written_paths.add("assets/game.droid")
                    else:
                        zout.writestr(item, zin.read(item.filename), compress_type=item.compress_type)
                        written_paths.add(fname_lower)

                # 6b. Inject custom assets from folder
                if custom_assets:
                    LOGGER.log(f"Writing {len(custom_assets)} custom assets into APK assets/...")
                    for src_path, apk_path in custom_assets:
                        current += 1
                        if current % 400 == 0 or current >= total_items:
                            print_progress(current, total_items, prefix="Packaging Final APK")

                        apk_p_lower = apk_path.lower()
                        if apk_p_lower not in written_paths:
                            if src_path.suffix.lower() == ".json":
                                try:
                                    j_text = src_path.read_text(encoding="utf-8", errors="replace")
                                    j_clean = re.sub(r',\s*([\}\]])', r'\1', j_text)
                                    zout.writestr(apk_path, j_clean.encode("utf-8"))
                                except Exception:
                                    zout.write(src_path, apk_path)
                            else:
                                zout.write(src_path, apk_path)
                            written_paths.add(apk_p_lower)

                # 6c. Inject in-memory manifests without duplicate entries
                if manifest_map:
                    LOGGER.log(f"Writing {len(manifest_map)} _manifest.txt files into APK assets/...")
                    for apk_path, m_bytes in manifest_map.items():
                        current += 1
                        if current % 400 == 0 or current >= total_items:
                            print_progress(current, total_items, prefix="Packaging Final APK")

                        apk_p_lower = apk_path.lower()
                        if apk_p_lower not in written_paths:
                            zout.writestr(apk_path, m_bytes)
                            written_paths.add(apk_p_lower)

                print_progress(total_items, total_items, prefix="Packaging Complete ")

        # 7. Sign APK (allow 2s buffer for Windows NTFS disk flush on large archives)
        import time
        time.sleep(2.0)
        sign_apk_file(target_apk)

    LOGGER.log(f"Success! Finished modded APK ready to install: {target_apk}", prefix="[+]")

# -----------------------------------------------------------------------------
# MAIN CLI ENTRYPOINT
# -----------------------------------------------------------------------------
def prompt_install_options(args):
    """Interactive feature selector: prompts for default install or individual enhancement toggles."""
    clean_default = getattr(args, "clean", False)
    fast_default = getattr(args, "fast", False)
    toy_default = (getattr(args, "toy_integration", "n") == "y" or getattr(args, "enable_toy_telemetry", False))

    if args.yes or not (sys.stdin and sys.stdin.isatty()):
        return {
            "core_manifest": True,
            "scaling": True,
            "stability": True,
            "climax_and_panels": True,
            "css_and_favs": True,
            "phone_import": True,
            "toy_telemetry": toy_default,
            "clean_output": clean_default,
            "fast_packaging": fast_default
        }

    def ask(prompt_text, default_yes=True):
        hint = "[Y/n] (Default: Yes, press ENTER)" if default_yes else "[y/N] (Default: No, press ENTER)"
        try:
            res = input(f"{prompt_text} {hint}: ").strip().lower()
        except Exception:
            return default_yes
        if not res:
            return default_yes
        return res in ["y", "yes", "1", "true"]

    print("=" * 70)
    print("           WB MOBILE PATCHER v1.0 - INSTALLATION SETUP")
    print("=" * 70)
    print("Note: Pressing ENTER on any prompt automatically selects the DEFAULT")
    print("      choice shown in capital letters (e.g. [Y/n] = Yes, [y/N] = No).\n")
    print("Choose your installation mode:")
    print("  [Y] Default Install (RECOMMENDED) - Press ENTER or type 'y'")
    print("      Includes the complete mobile suite: Universal Scaling, Touch Controls,")
    print("      Modal Supremacy Shield, Character Selector, and Portability Fixes.")
    print("\n  [N] Custom Install - Type 'n'")
    print("      Granular menu to toggle each individual enhancement on or off.")

    try:
        ans = input("\nProceed with Default Installation? [Y/n] (Default: Yes, press ENTER): ").strip().lower()
    except Exception:
        ans = "y"

    if ans in ["", "y", "yes"]:
        print("\n[+] Default Installation selected (all core enhancements enabled).")
        clean_ans = clean_default or ask("\nClean previous APK builds from output folder?", default_yes=False)
        toy_ans = toy_default or ask("\nEnable external ToyBridge / Intiface Bluetooth toy telemetry?", default_yes=False)
        fast_ans = fast_default or ask("\nFast packaging mode (uncompressed for rapid testing)?", default_yes=False)
        opts = {
            "core_manifest": True,
            "scaling": True,
            "stability": True,
            "climax_and_panels": True,
            "css_and_favs": True,
            "phone_import": True,
            "toy_telemetry": toy_ans,
            "clean_output": clean_ans,
            "fast_packaging": fast_ans
        }
    else:
        print("\n" + "-" * 70)
        print("CUSTOM INSTALLATION: Select components to enable")
        print("Tip: Press ENTER on each line to accept its indicated default value")
        print("-" * 70)

        opts = {}
        opts["core_manifest"] = ask("\n1. Core Mobile Engine & Fast Manifest Optimization?", default_yes=True)
        opts["scaling"] = ask("\n2. Universal Origin-Based Model Scaling (160px normalization)?", default_yes=True)
        opts["stability"] = ask("\n3. Engine Stability & Portrait Parity (cures requested -1 crashes)?", default_yes=True)
        opts["climax_and_panels"] = ask("\n4. UI Polish & Climax Auto-Closing (force-close panels during climax)?", default_yes=True)
        opts["css_and_favs"] = ask("\n5. Character Selection Grid & Vector Star Bookmarks?", default_yes=True)
        opts["phone_import"] = ask("\n6. On-Device Phone Mod Sharing (open .zip mods directly on Android)?", default_yes=True)
        opts["toy_telemetry"] = toy_default or ask("\n7. External ToyBridge / Intiface Telemetry (port 45735)?", default_yes=False)
        opts["clean_output"] = clean_default or ask("\n8. Clean previous APK builds from output folder?", default_yes=False)
        opts["fast_packaging"] = fast_default or ask("\n9. Fast packaging mode (uncompressed for rapid testing)?", default_yes=False)

    print("\n" + "-" * 70)
    print("Installation configuration confirmed:")
    print(f"  - Core Mobile Engine & Fast Manifests : {'ENABLED' if opts.get('core_manifest') else 'DISABLED'}")
    print(f"  - Universal Model Scaling (160px)     : {'ENABLED' if opts.get('scaling') else 'DISABLED'}")
    print(f"  - Engine Stability & Crash Shields    : {'ENABLED' if opts.get('stability') else 'DISABLED'}")
    print(f"  - UI Polish & Climax Auto-Closing     : {'ENABLED' if opts.get('climax_and_panels') else 'DISABLED'}")
    print(f"  - Character Grid & Star Bookmarks     : {'ENABLED' if opts.get('css_and_favs') else 'DISABLED'}")
    print(f"  - On-Device Phone Mod Sharing (.zip)  : {'ENABLED' if opts.get('phone_import') else 'DISABLED'}")
    print(f"  - Bluetooth Toy Telemetry             : {'ENABLED' if opts.get('toy_telemetry') else 'DISABLED'}")
    print(f"  - Fast Packaging (Uncompressed)       : {'ENABLED' if opts.get('fast_packaging') else 'DISABLED'}")
    print(f"  - Output Folder Housekeeping (Clean)  : {'ENABLED' if opts.get('clean_output') else 'DISABLED'}")
    print("-" * 70)
    return opts

def main():
    parser = argparse.ArgumentParser(
        description="WB_Mobile_Patcher: Universal Mobile Touch Overlay Patcher & APK Builder for GameMaker"
    )
    parser.add_argument("inputs", nargs="*", help="Input path(s): .apk, PC game folder, or folder + apk dragged together")
    parser.add_argument("-b", "--base-apk", help="Explicit Base APK template to use")
    parser.add_argument("-o", "--output", help="Output file path (default: output/<input_name>_modded.apk)")
    parser.add_argument("-y", "--yes", action="store_true", help="Proceed automatically with default settings without interactive prompts")
    parser.add_argument("--clean", action="store_true", help="Clean previous APK builds from output/ folder before building")
    parser.add_argument("--fast", action="store_true", help="Fast packaging mode (uncompressed for rapid testing and emulation)")
    parser.add_argument("--validate-only", action="store_true", help="Dry-run audit: validate and test portability of mod folders without building APK")
    parser.add_argument("--toy-integration", choices=["y", "n"], default="n", help="Enable external toy/buttplug integration (y/n, default: n)")
    parser.add_argument("--enable-toy-telemetry", action="store_true", default=False, help=argparse.SUPPRESS)

    args = parser.parse_args()
    patcher_dir = Path(__file__).parent.resolve()
    current_stage = "Initialization"

    try:
        current_stage = "Input Validation"
        utmt_cli = get_utmt_cli()
        LOGGER.log(f"Using UndertaleModCli: {utmt_cli}")

        source_folder = None
        source_apk = None

        input_dir = patcher_dir / "input"
        mod_subdirs = ["custom", "custom_futas", "custom_wives", "custom_bedrooms", "dialogue_packs", "texture_packs", "custom_sounds", "custom_music", "dialogue", "custom_dialogues"]

        # Check input folder if no arguments passed or if "input" is specified
        if not args.inputs or (len(args.inputs) == 1 and Path(args.inputs[0]).name.lower() == "input"):
            if input_dir.exists():
                cand_zips = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".zip" and not p.name.lower().endswith(".apk")]
                cand_dirs = [p for p in input_dir.iterdir() if p.is_dir() and not p.name.startswith(".") and any((p / sd).exists() for sd in mod_subdirs)]

                # Check if input/ has loose mod pack directories (e.g. input/ankha/custom_data.futa)
                loose_packs = []
                for p in input_dir.iterdir():
                    if p.is_dir() and not p.name.startswith(".") and p not in cand_dirs:
                        if any(p.glob("custom_data.*")) or (p / "custom_portrait.png").exists() or (p / "custom_mating_press.png").exists():
                            loose_packs.append(p)

                all_candidates = cand_dirs + cand_zips

                if len(all_candidates) > 1:
                    print("\n" + "=" * 70)
                    print("        MULTIPLE MOD PACKAGES DETECTED IN 'input/'")
                    print("=" * 70)
                    for c_idx, c_p in enumerate(all_candidates, 1):
                        c_ver = detect_mod_engine_version(c_p) if c_p.is_dir() else "Archive"
                        c_tag = f"Version {c_ver}" if c_ver != "Archive" else "Mod .zip"
                        print(f"  [{c_idx}] {c_p.name:45s} ({c_tag})")
                    print("-" * 70)

                    selected_p = all_candidates[0]
                    if not args.yes and sys.stdin and sys.stdin.isatty():
                        try:
                            c_sel = input(f"Select package to build [1-{len(all_candidates)}] (Default: 1, press ENTER): ").strip()
                            if c_sel.isdigit():
                                val = int(c_sel)
                                if 1 <= val <= len(all_candidates):
                                    selected_p = all_candidates[val - 1]
                        except Exception:
                            pass
                    LOGGER.log(f"Building selected package: {selected_p.name}", prefix="[+]")
                    args.inputs = [str(selected_p)]

                elif len(all_candidates) == 1:
                    args.inputs = [str(all_candidates[0])]

                elif loose_packs:
                    LOGGER.log(f"Found {len(loose_packs)} loose mod pack(s) in input/. Ingesting together...", prefix="[+]")
                    args.inputs = [str(input_dir)]

                elif any((input_dir / sd).exists() for sd in mod_subdirs):
                    args.inputs = [str(input_dir)]

        original_mod_name = None
        if args.inputs:
            input_paths = list(dict.fromkeys([Path(p).resolve() for p in args.inputs]))
            mod_sources = []

            for p_in in input_paths:
                if p_in.is_file() and p_in.suffix.lower() == ".apk":
                    if not source_apk:
                        source_apk = p_in
                elif p_in.is_file() and p_in.suffix.lower() == ".zip" and not p_in.name.lower().endswith(".apk"):
                    mod_sources.append(p_in)
                elif p_in.is_dir():
                    mod_sources.append(p_in)

            if len(mod_sources) == 1:
                s = mod_sources[0]
                if s.is_file() and s.suffix.lower() == ".zip":
                    tmp_extract = Path(tempfile.mkdtemp(prefix="wb_mods_zip_"))
                    with zipfile.ZipFile(s, 'r') as z_mods:
                        members = z_mods.infolist()
                        total_m = len(members)
                        LOGGER.log(f"Extracting mods archive: {s.name} ({total_m} items)...", prefix="[*]")
                        for m_idx, m_info in enumerate(members):
                            z_mods.extract(m_info, tmp_extract)
                            if (m_idx + 1) % 500 == 0 or (m_idx + 1) == total_m:
                                print_progress(m_idx + 1, total_m, prefix="Unpacking Archive")
                    source_folder = tmp_extract
                    original_mod_name = s.stem
                else:
                    source_folder = s
                    original_mod_name = s.name

            elif len(mod_sources) > 1:
                combined_staging = Path(tempfile.mkdtemp(prefix="wb_combined_mods_"))
                LOGGER.log(f"Multi-input detected: Combining {len(mod_sources)} mod sources into a single build...", prefix="[*]")
                for m_src in mod_sources:
                    if m_src.is_file() and m_src.suffix.lower() == ".zip":
                        with zipfile.ZipFile(m_src, 'r') as z_mods:
                            z_mods.extractall(combined_staging)
                    elif m_src.is_dir():
                        for child in m_src.iterdir():
                            dest_c = combined_staging / child.name
                            if child.is_dir():
                                if not dest_c.exists():
                                    shutil.copytree(child, dest_c)
                                else:
                                    for sub_f in child.rglob("*"):
                                        if sub_f.is_file():
                                            rel_f = sub_f.relative_to(child)
                                            target_f = dest_c / rel_f
                                            target_f.parent.mkdir(parents=True, exist_ok=True)
                                            shutil.copy2(sub_f, target_f)
                            elif child.is_file() and not dest_c.exists():
                                shutil.copy2(child, dest_c)

                source_folder = combined_staging
                original_mod_name = f"{mod_sources[0].stem}_and_{len(mod_sources)-1}_more_modded" 

        # Detect mods automatically in the provided folder/zip
        has_mods = False
        if source_folder and source_folder.exists():
            mod_subdirs = ["custom", "custom_futas", "custom_wives", "custom_bedrooms", "dialogue_packs", "texture_packs", "custom_sounds", "custom_music", "dialogue", "custom_dialogues"]
            for sd in mod_subdirs:
                if (source_folder / sd).exists():
                    has_mods = True
                    break
            if not has_mods:
                # Check for single nested subfolder (e.g. inside an extracted zip)
                for child in source_folder.iterdir():
                    if child.is_dir():
                        for sd in mod_subdirs:
                            if (child / sd).exists():
                                source_folder = child
                                has_mods = True
                                break
                    if has_mods:
                        break

        if args.validate_only:
            LOGGER.log("Mode: Validate-Only (Pre-flight Mod Portability Audit)", prefix="[*]")
            target_audit = source_folder or input_dir
            if not target_audit or not target_audit.exists():
                LOGGER.error("Validate-only requires a valid mod folder input.")
                return
            LOGGER.log(f"Auditing custom asset folder: {target_audit}...")
            quarantine_dir = patcher_dir / "output" / "quarantine"
            p_cnt, q_cnt, q_list = quarantine_incompatible_packs(target_audit, quarantine_dir)
            if q_cnt > 0:
                LOGGER.log(f"Pre-flight Pack Validation: Quarantined {q_cnt} incompatible/non-portable pack(s) into '{quarantine_dir}'.", prefix="[+]")
            LOGGER.log(f"Pre-flight Pack Validation: Verified {p_cnt} 100% portable pack(s).", prefix="[+]")
            custom_assets = gather_custom_assets(target_audit)
            LOGGER.log(f"Discovered {len(custom_assets)} custom asset file(s).")
            manifest_map = generate_manifest_data(target_audit)
            LOGGER.log(f"Generated {len(manifest_map)} Android _manifest.txt index file(s).")
            LOGGER.log("Audit complete: Mod folder is 100% portable and ready for compilation!", prefix="[+]")
            return

        if not has_mods:
            if source_folder:
                LOGGER.log(f"No custom mods found in provided input: {source_folder}", prefix="[!]")
            else:
                LOGGER.log("No custom mods folder or .zip was provided.", prefix="[!]")

            # Ask user whether to proceed with building without mods
            if args.yes:
                proceed = "y"
            elif sys.stdin and sys.stdin.isatty():
                try:
                    proceed = input("\n[?] No custom mods were found. Proceed with building APK without mods? [Y/n]: ").strip().lower()
                except Exception:
                    proceed = "y"
                if proceed == "":
                    proceed = "y"
            else:
                proceed = "n"

            if proceed not in ["y", "yes"]:
                LOGGER.log("Build cancelled by user. Please provide a folder or .zip containing your custom mods.", prefix="[*]")
                sys.exit(0)
            else:
                LOGGER.log("Proceeding with clean mobile build without custom mods...", prefix="[*]")
                source_folder = None
        else:
            LOGGER.log(f"Auto-detected custom mods in: {source_folder}", prefix="[+]")

        target_version = detect_mod_engine_version(source_folder)
        engine_label = "Wife's Bedroom v1.5" if target_version == "1.5" else "Deeproom 4.0 / v1.4"
        LOGGER.log(f"Target engine detected: Version {target_version} ({engine_label})", prefix="[*]")

        if args.base_apk:
            source_apk = Path(args.base_apk).resolve()

        if not source_apk:
            source_apk = find_matching_base_apk(input_dir, patcher_dir, target_version=target_version)

        if not source_apk or not source_apk.exists():
            req_apk = f"wifes_bedroom{target_version.replace('.', '_')}.apk"
            raise FileNotFoundError(f"Base APK not found for {engine_label}. Please place {req_apk} (or base.apk) in the input/ folder.")

        LOGGER.log(f"Matched Base APK: {source_apk.name}", prefix="[+]")
        if target_version == "1.5" and ("1_4" in source_apk.name or "1.4" in source_apk.name or source_apk.name == "base.apk"):
            LOGGER.log("Notice: Compiling v1.5 mods using a v1.4 base APK. For full native v1.5 stability, place wifes_bedroom1_5.apk in the input/ folder.", prefix="[!]")

        output_dir = patcher_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        if args.output:
            output_apk = Path(args.output).resolve()
        else:
            # Dynamically derive APK filename from mod folder/zip name or base APK name
            naming_source = original_mod_name or (Path(source_folder).name if source_folder else Path(source_apk).stem)
            clean_name = re.sub(r"\.(zip|apk|7z|rar)$", "", str(naming_source), flags=re.I).strip()
            clean_name = re.sub(r'[\/:*?"<>|]', "_", clean_name).strip()
            if not clean_name.lower().endswith("_modded"):
                clean_name = f"{clean_name}_modded"
            output_apk = output_dir / f"{clean_name}.apk"

        current_stage = "Applying Mobile Enhancements & Building APK"
        install_opts = prompt_install_options(args)
        patch_game_apk(utmt_cli, source_apk, output_apk, source_folder=source_folder, opts=install_opts)

    except Exception as exc:
        LOGGER.error(f"Process failed during [{current_stage}]: {exc}")
        LOGGER.write_error_report(exc, current_stage)
        sys.exit(1)

if __name__ == "__main__":
    main()