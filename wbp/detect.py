"""wbp.detect"""
import sys
import atexit
import os
import re
import zlib
import struct
import glob
import json
import shutil
import io
import hashlib
import socket
import tempfile
import zipfile
import traceback
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from wbp.common import LOGGER, unlink_with_retry

def extract_pack_display_name(pack_path: Path) -> str:
    """
    Reads [info] name="..." from .futa, .spouse, .wife, .bedroom, or .txt INI files.
    Allows numeric Steam Workshop IDs (e.g. 3821177370) to automatically display
    their real character names (e.g. Ankha, Pomni, Miku) in the Character Selection Grid.
    """
    for df_name in ["custom_data.futa", "custom_data.spouse", "custom_data.wife", "custom_data.bedroom", "custom_data.txt"]:
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
    Detects whether a mod folder is designed for modern Wife's Bedroom (v1.5, v1.6, v2.0+),
    Deeproom 4.0/4.1+ Kiwami, or legacy ModRoom v3.3/v3.7+.
    Evaluates folder nomenclature, unified custom/ structure, and data.win binary characteristics.
    Returns '1.5', 'modroom33', or '1.4' (Deeproom).
    """
    if not folder or not folder.is_dir():
        return "1.4"

    # PRIORITY 1: Deeproom 4.0.3+ Kiwami always has custom_stuff/ container
    if (folder / "custom_stuff").is_dir():
        return "1.4"

    # PRIORITY 2: Inspect PC data.win binary characteristics if present
    dwin = folder / "data.win"
    if dwin.is_file():
        dwin_head = dwin.read_bytes()[:15 * 1024 * 1024] if dwin.stat().st_size > 0 else b""
        if dwin.stat().st_size < 25 * 1024 * 1024 and (b"custom_wives_folder" in dwin_head or b"custom_futas_folder" in dwin_head):
            return "modroom33"
        if dwin.stat().st_size > 40 * 1024 * 1024 or b"oDialogueManager" in dwin_head or b"custom_wives" in dwin_head:
            return "1.4"
        if dwin.stat().st_size < 35 * 1024 * 1024:
            return "1.5"

    f_lower = folder.name.lower()
    # PRIORITY 3: Modern Wife's Bedroom naming: requires 'wife' or 'wb' in folder name
    if any(k in f_lower for k in ["wife", "wb"]) and re.search(r"(?:1[_.][5-9]|[2-9][_.]\d|v1[_.][5-9]|v[2-9])", f_lower):
        return "1.5"

    # PRIORITY 4: Modern unified custom/ folder
    if (folder / "custom").is_dir() and not (folder / "custom_futas").is_dir() and not (folder / "custom_wives").is_dir():
        return "1.5"

    # PRIORITY 5: Legacy ModRoom root-level custom_futas without custom_stuff/
    if (folder / "custom_futas").is_dir() and not (folder / "custom_stuff").is_dir():
        return "modroom33"

    return "1.4"


def find_matching_base_apk(input_dir: Path, patcher_dir: Path, target_version: str = "1.4") -> Path:
    """
    Finds the optimal base APK matching the target engine version.
    Supports fixed filenames as well as dynamic discovery of future version APKs
    (e.g. wifes_bedroom1_6.apk, wifes_bedroom2_0.apk, deeproom4_1.apk).
    """
    scan_dirs = [input_dir, patcher_dir, patcher_dir / "input"]

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

        for sd in scan_dirs:
            if sd.is_dir():
                for apk in sorted(sd.glob("*.apk")):
                    an = apk.name.lower()
                    if re.search(r"wifes?_bedroom.*(?:1[_.][5-9]|[2-9][_.]\d)", an):
                        return apk.resolve()

    v14_candidates = [
        input_dir / "wifes_bedroom1_4.apk",
        input_dir / "wifes_bedroom_1_4.apk",
        input_dir / "wifes_bedroom.apk",
        patcher_dir / "input" / "wifes_bedroom1_4.apk",
        patcher_dir / "input" / "wifes_bedroom_1_4.apk",
        patcher_dir / "input" / "wifes_bedroom.apk",
        patcher_dir / "wifes_bedroom1_4.apk",
        patcher_dir / "wifes_bedroom.apk",
        input_dir / "wifes_bedroom-toybridge.apk",
        input_dir / "base.apk",
        patcher_dir / "input" / "base.apk",
        patcher_dir / "base.apk"
    ]
    for c in v14_candidates:
        if c.is_file():
            return c.resolve()

    for sd in scan_dirs:
        if sd.is_dir():
            for apk in sorted(sd.glob("*.apk")):
                if "test" not in apk.name.lower() and "out" not in apk.name.lower():
                    return apk.resolve()

    return None


def clean_output_dir(output_dir, preserve_file=None):
    """Removes older .apk builds and .idsig signature files from output/. Base APK backups (.bak) are kept."""
    removed = 0
    locked = []
    preserve_resolved = Path(preserve_file).resolve() if preserve_file else None
    for p in output_dir.glob("*"):
        if p.is_file() and p.suffix.lower() in [".apk", ".idsig"]:
            if preserve_resolved and p.resolve() == preserve_resolved:
                continue
            if unlink_with_retry(p, tries=2):
                removed += 1
            else:
                locked.append(p.name)
    if removed > 0:
        LOGGER.log(f"Cleaned {removed} previous build file(s) from output/.", prefix="[+]")
    if locked:
        LOGGER.log(f"Could not remove {len(locked)} file(s) because another program has them open: {', '.join(locked[:3])}"
                   f"{'...' if len(locked) > 3 else ''}", prefix="[!]")
