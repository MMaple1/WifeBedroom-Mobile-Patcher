"""wbp.toy"""
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
from wbp.toy_native import apply_native_toy
from wbp.common import LOGGER, gml, guarded_replace

# -----------------------------------------------------------------------------
# TOYBRIDGE 1.5.3 FULL SUITE & BLUETOOTH INTEGRATION
# -----------------------------------------------------------------------------
TOY_PROFILE_CHOICES = [
    ("Default (0-100%, full range)", "default", 0),
    ("Easy (0-30%, gentle)", "easy", 1),
    ("Mid (30-60%, moderate)", "mid", 2),
    ("Hard (60-100%, intense)", "hard", 3),
    ("Mid-Easy (0-50%)", "mideasy", 4),
    ("Mid-Hard (50-100%)", "midhard", 5),
]


TOY_LEAD_CHOICES = [
    ("0 ms (Off / Wired / Low Latency)", 0),
    ("50 ms", 50),
    ("100 ms", 100),
    ("150 ms", 150),
    ("200 ms (Recommended for Bluetooth Toys e.g. Lovense / Handy)", 200),
    ("250 ms", 250),
    ("300 ms", 300),
    ("400 ms", 400),
    ("500 ms", 500),
]


def probe_intiface_server(host="127.0.0.1", port=12345, max_attempts=3, timeout=0.4):
    """Checks if an Intiface Central server is active on host:port, limiting to max_attempts without hanging."""
    for attempt in range(1, max_attempts + 1):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
    return False


def export_toybridge_companion_suite(patcher_dir, output_dir):
    """Exports the complete ToyBridge 1.5.3 Companion Suite if external companion tools are present."""
    tools_src = patcher_dir / "tools" / "toybridge"
    launcher_src = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "Programs" / "ToyBridgeLauncher"
    if not tools_src.exists() and not launcher_src.exists():
        LOGGER.log("Notice: the ToyBridge companion apps are not installed (put them in tools/toybridge/ or install the ToyBridge launcher); skipping suite export. Direct mode does not need them.", prefix="[*]")
        return None
    suite_dest = output_dir / "Telemetry_Suite"
    suite_dest.mkdir(parents=True, exist_ok=True)

    copied = 0
    if tools_src.exists():
        for f in tools_src.iterdir():
            if f.is_file():
                shutil.copy2(f, suite_dest / f.name)
                copied += 1
        if (tools_src / "_internal").is_dir() and not (suite_dest / "_internal").exists():
            shutil.copytree(tools_src / "_internal", suite_dest / "_internal")

    if launcher_src.exists():
        for extra in ["ToyLauncher.exe", "HmvLive.exe", "launcher_settings.json"]:
            p = launcher_src / extra
            if p.exists() and not (suite_dest / extra).exists():
                shutil.copy2(p, suite_dest / extra)
                copied += 1
        if (launcher_src / "_internal").exists() and not (suite_dest / "_internal").exists():
            try:
                shutil.copytree(launcher_src / "_internal", suite_dest / "_internal")
            except Exception:
                pass

    LOGGER.log(f"Exported complete ToyBridge 1.5.3 Companion Suite ({copied} files) to '{suite_dest}'.", prefix="[+]")
    return suite_dest


def apply_toybridge_suite_patches(patched_droid, opts, utmt_cli, custom_assets, output_dir, patcher_dir, tmpdir=None):
    """
    Applies the full ToyBridge 1.5.3 suite to game.droid:
    1. Standalone Direct WebSocket Toy Client (--toy-direct) or UDP Telemetry
    2. Retry limiter (3-5 attempts) in GML to prevent infinite background polling
    3. Interactive Title Screen Toy HUD (Status, Profile Tap, Delay Fix Tap)
    4. Pre-seeds assets/toy_direct.ini with user-selected Bluetooth lead and profile
    5. HMV Audio Beat-Sync Mode if requested
    6. Exports ToyBridge Companion Suite to output/ToyBridge_Suite/ if requested
    """
    # Strict gating: never apply or inject any toy/bluetooth components unless toy integration is confirmed True
    if not opts or not opts.get("toy_telemetry", False):
        return
    toy_mode = opts.get("toy_mode", "direct")  # "direct", "bridge", "all"
    toy_profile = opts.get("toy_profile", 0)   # 0 to 5
    toy_lead = opts.get("toy_lead", 200)       # 0 to 500 ms
    toy_port = opts.get("toy_port", 12345)
    toy_retries = opts.get("toy_retries", 5)
    hmv_mode = opts.get("hmv_mode", False)
    export_tools = opts.get("export_toy_tools", False)

    work_dir = tmpdir if tmpdir is not None else Path(tempfile.gettempdir())

    # 1. Patch the game code natively (direct client, UDP telemetry, HMV): the same edits GamePatcher.exe made
    features = set()
    if toy_mode in ["direct", "all"]:
        features.add("direct")
    if toy_mode in ["bridge", "all"]:
        features.add("udp")
    if hmv_mode:
        features.add("hmv")
    if features:
        LOGGER.log(f"ToyBridge: applying {', '.join(sorted(features))} to game.droid...", prefix="[*]")
        if not apply_native_toy(patched_droid, utmt_cli, features, work_dir):
            return

    if toy_mode in ["direct", "all"]:
        # 2. Enhance Draw_0 with retry limiter & title screen tap handlers
        try:
            dump_dir = work_dir / "toy_dump"
            dump_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run([str(utmt_cli), "dump", str(patched_droid), "-o", str(dump_dir), "-c", "gml_Object_oFutaMatingPress_Draw_0"], check=True, capture_output=True, stdin=subprocess.DEVNULL)
            draw_f = dump_dir / "CodeEntries" / "gml_Object_oFutaMatingPress_Draw_0.gml"
            if draw_f.exists():
                draw_code = draw_f.read_text(encoding="utf-8")

                # Inject retry limit logic
                retry_old = gml("apply_toybridge_suite_patches/retry_old")
                retry_new = '    if (!variable_instance_exists(id, "tb_retry_count")) { tb_retry_count = 0; tb_retry_max = ' + str(toy_retries) + '; tb_paused_retry = false; }\n    if (tb_state == 0 && !tb_paused_retry && _tb_now >= tb_retry_at)\n    {\n        tb_retry_count += 1;\n        if (tb_retry_count > tb_retry_max)\n        {\n            tb_paused_retry = true;\n            tb_state = -1;\n        }\n        else\n        {\n            if (tb_sock >= 0)\n            {\n                network_destroy(tb_sock);\n            }\n            tb_running = false;\n            tb_ws_open = false;\n            tb_rx_len = 0;\n            tb_sock = network_create_socket(network_socket_tcp);\n            network_connect_raw_async(tb_sock, "127.0.0.1", tb_port);\n            tb_state = 1;\n            tb_retry_at = _tb_now + 6000;\n        }\n    }'
                draw_code = guarded_replace(draw_code, retry_old, retry_new, "apply_toybridge_suite_patches:retry_old")

                # Enhanced HUD label
                hud_old = '    var _tb_label = "TOY: OPEN INTIFACE CENTRAL";'
                hud_new = gml("apply_toybridge_suite_patches/hud_new")
                draw_code = guarded_replace(draw_code, hud_old, hud_new, "apply_toybridge_suite_patches:hud_old")

                # Add tap-to-retry on top line
                tap_old = gml("apply_toybridge_suite_patches/tap_old")
                tap_new = gml("apply_toybridge_suite_patches/tap_new")
                draw_code = guarded_replace(draw_code, tap_old, tap_new, "apply_toybridge_suite_patches:tap_old")

                draw_f.write_text(draw_code, encoding="utf-8")
                res_rep = subprocess.run([str(utmt_cli), "replace", str(patched_droid), "-c", f"gml_Object_oFutaMatingPress_Draw_0={draw_f}", "-o", str(patched_droid)], capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
                if res_rep.returncode == 0:
                    LOGGER.log(f"ToyBridge: Configured in-game connection retry limit ({toy_retries} attempts) & touch controls.", prefix="[+]")
        except Exception as ex_enh:
            LOGGER.log(f"Notice: Draw_0 retry enhancement encountered: {ex_enh}", prefix="[!]")

    # 5. Pre-seed toy_direct.ini into custom_assets for APK
    ini_content = f"""[toy]
profile={toy_profile}
lead={toy_lead}
port={toy_port}
retries={toy_retries}
"""
    ini_tmp = work_dir / "toy_direct.ini"
    ini_tmp.write_text(ini_content, encoding="utf-8")
    custom_assets.append((ini_tmp, "assets/toy_direct.ini"))
    LOGGER.log(f"ToyBridge: Pre-seeded toy_direct.ini (Profile: {toy_profile}, Delay Fix: {toy_lead}ms, Port: {toy_port}, Retries: {toy_retries}).", prefix="[+]")

    # 6. Companion Suite Export if requested
    if export_tools:
        export_toybridge_companion_suite(patcher_dir, output_dir)
