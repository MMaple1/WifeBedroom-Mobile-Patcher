"""wbp.cli"""
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
from wbp.common import LOGGER, ROOT_DIR, print_progress
from wbp.detect import clean_output_dir, detect_mod_engine_version, find_matching_base_apk
from wbp.env import get_utmt_cli, verify_environment
from wbp.packs import gather_custom_assets, generate_manifest_data, plan_pack_skips, sanitize_apk_part, write_skip_report
from wbp.toy import TOY_PROFILE_CHOICES, probe_intiface_server
from wbp.apk import patch_game_apk

def prompt_toybridge_settings(args):
    """Interactive configuration for ToyBridge 1.5.3 suite, Bluetooth latency, profiles, and retry limits."""
    print("\n" + "=" * 70)
    print("        HARDWARE TELEMETRY & BLUETOOTH CONFIGURATION")
    print("=" * 70)

    # 1. Non-blocking probe for Intiface Central server
    print("[*] Probing for active local telemetry server on 127.0.0.1:12345 (max 3 attempts)...")
    is_up = probe_intiface_server(port=12345, max_attempts=3, timeout=0.4)
    if is_up:
        print("    [+] Active telemetry server detected on ws://127.0.0.1:12345!")
    else:
        print("    [!] Notice: Local telemetry server was not detected on port 12345 (3/3 attempts timed out).")
        try:
            keep = input("    Telemetry server is not currently running. Keep hardware integration enabled for later? [Y/n] (Default: Yes, press ENTER): ").strip().lower()
        except Exception:
            keep = "y"
        if keep not in ["", "y", "yes", "1", "true"]:
            print("    [-] Hardware integration disabled.")
            return {"enabled": False}

    # 2. Select Toy Operation Mode
    print("\nSelect Hardware Telemetry Operation Mode:")
    print("  [1] Direct Client (Standalone WebSocket - Recommended for Android, NO Termux needed) [DEFAULT]")
    print("  [2] External UDP Bridge (Port 45735 telemetry for PC ToyLauncher / Termux Linux)")
    print("  [3] Dual Mode (Both Direct Client + UDP Telemetry active)")
    mode_choice = "1"
    try:
        m_in = input("Selection [1-3] (Default: 1 - Direct Client, press ENTER): ").strip()
        if m_in in ["1", "2", "3"]:
            mode_choice = m_in
    except Exception:
        pass

    toy_mode_map = {"1": "direct", "2": "bridge", "3": "all"}
    chosen_mode = toy_mode_map[mode_choice]

    # 3. Bluetooth Latency Compensation (Delay Fix)
    print("\nSelect Bluetooth Latency Compensation (Delay Fix):")
    print("  Common Bluetooth devices respond ~100-300ms late.")
    print("  The setting is stored in toy_direct.ini.")
    print("  [1] 0 ms (Off / Wired / Low Latency)")
    print("  [2] 50 ms")
    print("  [3] 100 ms")
    print("  [4] 150 ms")
    print("  [5] 200 ms (RECOMMENDED for Bluetooth toys e.g. Lovense / Handy) [DEFAULT]")
    print("  [6] 250 ms")
    print("  [7] 300 ms")
    print("  [8] 400 ms")
    print("  [9] 500 ms")
    lead_choice = "5"
    try:
        l_in = input("Selection [1-9] (Default: 5 - 200ms, press ENTER): ").strip()
        if l_in in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            lead_choice = l_in
    except Exception:
        pass

    lead_map = {"1": 0, "2": 50, "3": 100, "4": 150, "5": 200, "6": 250, "7": 300, "8": 400, "9": 500}
    chosen_lead = lead_map[lead_choice]

    # 4. Intensity Profile
    print("\nSelect Default Intensity Profile (can also be tapped in-game):")
    print("  [1] Default (0-100%, full range) [DEFAULT]")
    print("  [2] Easy (0-30%, gentle)")
    print("  [3] Mid (30-60%, moderate)")
    print("  [4] Hard (60-100%, intense)")
    print("  [5] Mid-Easy (0-50%)")
    print("  [6] Mid-Hard (50-100%)")
    prof_choice = "1"
    try:
        p_in = input("Selection [1-6] (Default: 1 - Default 0-100%, press ENTER): ").strip()
        if p_in in ["1", "2", "3", "4", "5", "6"]:
            prof_choice = p_in
    except Exception:
        pass

    chosen_profile = int(prof_choice) - 1

    # 5. HMV Audio Beat-Sync Mode
    try:
        hmv_in = input("\nEnable HMV Audio Beat-Sync Mode (UDP port 45736 & clickable bed speakers)? [y/N] (Default: No, press ENTER): ").strip().lower()
    except Exception:
        hmv_in = "n"
    chosen_hmv = hmv_in in ["y", "yes", "1", "true"]

    # 6. Companion Tools Export
    try:
        exp_in = input("\nExport companion telemetry tools to output/? [y/N] (Default: No, press ENTER): ").strip().lower()
    except Exception:
        exp_in = "n"
    chosen_export = exp_in in ["y", "yes", "1", "true"]

    print("-" * 70)
    print("Hardware Telemetry Configuration Confirmed:")
    print(f"  - Operation Mode      : {chosen_mode.upper()}")
    print(f"  - Bluetooth Delay Fix : {chosen_lead} ms {'(Recommended for Bluetooth)' if chosen_lead == 200 else ''}")
    print(f"  - Default Profile     : {TOY_PROFILE_CHOICES[chosen_profile][0]}")
    print("  - Retry Limit         : 5 attempts before pause (with on-screen tap to retry)")
    print(f"  - HMV Beat-Sync Mode  : {'ENABLED' if chosen_hmv else 'DISABLED'}")
    print(f"  - Companion Suite     : {'EXPORT TO output/Telemetry_Suite/' if chosen_export else 'SKIP'}")
    print("-" * 70)

    return {
        "enabled": True,
        "toy_mode": chosen_mode,
        "toy_lead": chosen_lead,
        "toy_profile": chosen_profile,
        "toy_port": 12345,
        "toy_retries": 5,
        "hmv_mode": chosen_hmv,
        "export_toy_tools": chosen_export
    }


# -----------------------------------------------------------------------------
# MAIN CLI ENTRYPOINT
# -----------------------------------------------------------------------------
def prompt_install_options(args):
    """Interactive feature selector: prompts for default install or individual enhancement toggles."""
    clean_default = getattr(args, "clean", False)
    fast_default = getattr(args, "fast", False)
    cli_toy = getattr(args, "toy_integration", None)
    cli_enable = getattr(args, "enable_toy_telemetry", False)

    if cli_toy == "y" or cli_enable:
        toy_flag = True
    elif cli_toy == "n":
        toy_flag = False
    else:
        toy_flag = None

    profile_map = {"default": 0, "easy": 1, "mid": 2, "hard": 3, "mideasy": 4, "midhard": 5}
    if args.yes or not (sys.stdin and sys.stdin.isatty()):
        is_toy_on = (toy_flag is True)
        return {
            "core_manifest": True,
            "scaling": True,
            "stability": True,
            "climax_and_panels": True,
            "css_and_favs": True,
            "phone_import": True,
            "toy_telemetry": is_toy_on,
            "toy_mode": getattr(args, "toy_mode", "direct") if is_toy_on else "none",
            "toy_profile": profile_map.get(getattr(args, "toy_profile", "default"), 0),
            "toy_lead": getattr(args, "toy_lead", 200),
            "toy_port": getattr(args, "toy_port", 12345),
            "toy_retries": getattr(args, "toy_retries", 5),
            "hmv_mode": getattr(args, "hmv_mode", False) if is_toy_on else False,
            "export_toy_tools": getattr(args, "export_toy_tools", False) if is_toy_on else False,
            "clean_output": clean_default,
            "fast_packaging": fast_default,
            "quarantine_duplicates": getattr(args, "quarantine_duplicates", True),
            "xray_origins": getattr(args, "xray_origins", True),
            "move_skipped": getattr(args, "move_skipped", False),
            "approximate": getattr(args, "approximate", False),
            "legacy_key": getattr(args, "legacy_key", False)
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
    print("           WB MOBILE PATCHER v1.2 - INSTALLATION SETUP")
    print("=" * 70)
    print("Required Base APK:")
    print("  - ModRoom v3.3 / Deeproom 4.0 (v1.4) : requires wifes_bedroom1_4.apk")
    print("  - Wife's Bedroom v1.5                : requires wifes_bedroom1_5.apk")
    print("Place your APK in the input/ folder or drag it alongside your mod folder.\n")
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
        quarantine_ans = getattr(args, "quarantine_duplicates", True) and ask("\nSkip duplicate mod packs (keep the best copy of each; your mod folder is not changed)?", default_yes=True)
        xray_ans = getattr(args, "xray_origins", True) and ask("\nAlign X-ray overlays with each character's sprite (Deeproom; measured per pack, your mod folder is not changed)?", default_yes=True)
        clean_ans = clean_default or ask("\nClean previous APK builds from output folder?", default_yes=False)
        fast_ans = fast_default or ask("\nFast packaging mode (uncompressed for rapid testing)?", default_yes=False)
        
        toy_settings = None
        if toy_flag is True:
            toy_settings = prompt_toybridge_settings(args)
        elif toy_flag is False:
            toy_settings = {"enabled": False}
        else:
            ask_toy = ask("\nEnable Bluetooth hardware telemetry integration?", default_yes=False)
            if ask_toy:
                toy_settings = prompt_toybridge_settings(args)
            else:
                toy_settings = {"enabled": False}

        is_toy_enabled = toy_settings.get("enabled", False) if toy_settings else False
        opts = {
            "core_manifest": True,
            "scaling": True,
            "stability": True,
            "climax_and_panels": True,
            "css_and_favs": True,
            "phone_import": True,
            "toy_telemetry": is_toy_enabled,
            "toy_mode": toy_settings.get("toy_mode", "direct") if is_toy_enabled else "none",
            "toy_lead": toy_settings.get("toy_lead", 200),
            "toy_profile": toy_settings.get("toy_profile", 0),
            "toy_port": toy_settings.get("toy_port", 12345),
            "toy_retries": toy_settings.get("toy_retries", 5),
            "hmv_mode": toy_settings.get("hmv_mode", False),
            "export_toy_tools": toy_settings.get("export_toy_tools", False),
            "clean_output": clean_ans,
            "fast_packaging": fast_ans,
            "quarantine_duplicates": quarantine_ans,
            "xray_origins": xray_ans,
            "move_skipped": getattr(args, "move_skipped", False),
            "approximate": getattr(args, "approximate", False),
            "legacy_key": getattr(args, "legacy_key", False)
        }
    else:
        print("\n" + "-" * 70)
        print("CUSTOM INSTALLATION: Select components to enable")
        print("Tip: Press ENTER on each line to accept its indicated default value")
        print("-" * 70)

        opts = {}
        opts["quarantine_duplicates"] = getattr(args, "quarantine_duplicates", True) and ask("\n1. Duplicate pack detection (skip duplicate packs; your mod folder is not changed)?", default_yes=True)
        opts["xray_origins"] = getattr(args, "xray_origins", True) and ask("\n1b. Align X-ray overlays with each character's sprite (Deeproom; measured per pack, your mod folder is not changed)?", default_yes=True)
        opts["move_skipped"] = getattr(args, "move_skipped", False)
        opts["approximate"] = getattr(args, "approximate", False)
        opts["legacy_key"] = getattr(args, "legacy_key", False)
        opts["core_manifest"] = ask("\n2. Core Mobile Engine & Fast Manifest Optimization?", default_yes=True)
        opts["scaling"] = ask("\n3. Universal Origin-Based Model Scaling (160px normalization)?", default_yes=True)
        opts["stability"] = ask("\n4. Engine Stability & Portrait Parity (cures requested -1 crashes)?", default_yes=True)
        opts["climax_and_panels"] = ask("\n5. UI Polish & Climax Auto-Closing (force-close panels during climax)?", default_yes=True)
        opts["css_and_favs"] = ask("\n6. Character Selection Grid & Vector Star Bookmarks?", default_yes=True)
        opts["phone_import"] = ask("\n7. On-Device Phone Mod Sharing (open .zip mods directly on Android)?", default_yes=True)

        toy_settings = None
        if toy_flag is True:
            toy_settings = prompt_toybridge_settings(args)
        elif toy_flag is False:
            toy_settings = {"enabled": False}
        else:
            ask_toy = ask("\n8. Bluetooth Hardware Telemetry Integration?", default_yes=False)
            if ask_toy:
                toy_settings = prompt_toybridge_settings(args)
            else:
                toy_settings = {"enabled": False}

        is_toy_enabled = toy_settings.get("enabled", False) if toy_settings else False
        opts["toy_telemetry"] = is_toy_enabled
        opts["toy_mode"] = toy_settings.get("toy_mode", "direct") if is_toy_enabled else "none"
        opts["toy_lead"] = toy_settings.get("toy_lead", 200)
        opts["toy_profile"] = toy_settings.get("toy_profile", 0)
        opts["toy_port"] = toy_settings.get("toy_port", 12345)
        opts["toy_retries"] = toy_settings.get("toy_retries", 5)
        opts["hmv_mode"] = toy_settings.get("hmv_mode", False)
        opts["export_toy_tools"] = toy_settings.get("export_toy_tools", False)

        opts["clean_output"] = clean_default or ask("\n9. Clean previous APK builds from output folder?", default_yes=False)
        opts["fast_packaging"] = fast_default or ask("\n10. Fast packaging mode (uncompressed for rapid testing)?", default_yes=False)

    print("\n" + "-" * 70)
    print("Installation configuration confirmed:")
    print(f"  - Duplicate Asset Detection/Removal   : {'ENABLED' if opts.get('quarantine_duplicates') else 'DISABLED'}")
    print(f"  - APK Signing Key                     : {'SHARED LEGACY KEY (--legacy-key)' if opts.get('legacy_key') else 'YOUR PERSONAL KEY'}")
    print(f"  - X-ray Overlay Alignment (Deeproom)  : {'ENABLED' if opts.get('xray_origins', True) else 'DISABLED'}")
    print(f"  - Core Mobile Engine & Fast Manifests : {'ENABLED' if opts.get('core_manifest') else 'DISABLED'}")
    print(f"  - Universal Model Scaling (160px)     : {'ENABLED' if opts.get('scaling') else 'DISABLED'}")
    print(f"  - Engine Stability & Crash Shields    : {'ENABLED' if opts.get('stability') else 'DISABLED'}")
    print(f"  - UI Polish & Climax Auto-Closing     : {'ENABLED' if opts.get('climax_and_panels') else 'DISABLED'}")
    print(f"  - Character Grid & Star Bookmarks     : {'ENABLED' if opts.get('css_and_favs') else 'DISABLED'}")
    print(f"  - On-Device Phone Mod Sharing (.zip)  : {'ENABLED' if opts.get('phone_import') else 'DISABLED'}")
    print(f"  - Hardware Telemetry & Bluetooth      : {'ENABLED (' + str(opts.get('toy_mode')).upper() + ', Delay: ' + str(opts.get('toy_lead')) + 'ms)' if opts.get('toy_telemetry') else 'DISABLED'}")
    if opts.get("toy_telemetry"):
        print(f"    * Power Profile                     : {TOY_PROFILE_CHOICES[opts.get('toy_profile', 0)][0]}")
        print(f"    * Retry Limiter                     : {opts.get('toy_retries', 5)} attempts (pause on title with tap to retry)")
        print(f"    * HMV Beat-Sync Mode                : {'ENABLED' if opts.get('hmv_mode') else 'DISABLED'}")
        print(f"    * Export Companion Suite            : {'YES (output/Telemetry_Suite/)' if opts.get('export_toy_tools') else 'NO'}")
    print(f"  - Fast Packaging (Uncompressed)       : {'ENABLED' if opts.get('fast_packaging') else 'DISABLED'}")
    print(f"  - Output Folder Housekeeping (Clean)  : {'ENABLED' if opts.get('clean_output') else 'DISABLED'}")
    print("-" * 70)
    return opts


def main():
    parser = argparse.ArgumentParser(
        description="WB_Mobile_Patcher: Universal Mobile Touch Overlay Patcher & APK Builder for GameMaker"
    )
    parser.add_argument("inputs", nargs="*", help="Input path(s): .apk, PC game folder, or mod folder + base APK dragged together (e.g. wifes_bedroom1_4.apk for ModRoom v3.3)")
    parser.add_argument("-b", "--base-apk", help="Explicit Base APK to use (e.g. -b wifes_bedroom1_4.apk or -b wifes_bedroom1_5.apk)")
    parser.add_argument("-o", "--output", help="Output file path (default: output/<input_name>_modded.apk)")
    parser.add_argument("-y", "--yes", action="store_true", help="Proceed automatically with default settings without interactive prompts")
    parser.add_argument("--clean", action="store_true", help="Clean previous APK builds from output/ folder before building")
    parser.add_argument("--fast", action="store_true", help="Fast packaging mode (uncompressed for rapid testing and emulation)")
    parser.add_argument("--validate-only", action="store_true", help="Dry-run audit: validate and test portability of mod folders without building APK")
    parser.add_argument("--quarantine-duplicates", action="store_true", default=True, help="Automatically detect and quarantine duplicate custom character/room folders (default: True)")
    parser.add_argument("--approximate", action="store_true", default=False, help="When bridging ModRoom (_0.png) and standard sprite names, also convert strips whose frame count must be reduced (drops frames; mappings learned from few packs). Default: only lossless padding and the safe partner X-ray crop; other strips are renamed unchanged")
    parser.add_argument("--legacy-key", action="store_true", default=False, help="Sign with the shared key that builds before 2026-11-18 used (public; only to keep updating an install made with an older build). Default: your personal key, made once in %%USERPROFILE%%\.wb_mobile_patcher")
    parser.add_argument("--move-skipped", action="store_true", default=False, help="Move skipped duplicate/incompatible packs into output/quarantine/<date-time>/ instead of only skipping them (never overwrites or deletes)")
    parser.add_argument("--no-quarantine-duplicates", action="store_false", dest="quarantine_duplicates", help="Disable duplicate custom folder quarantine")
    parser.add_argument("--no-xray-origins", action="store_false", dest="xray_origins", default=True,
                        help="Deeproom: do not align X-ray overlays with the character sprites (no [xray] mobile_origin_x/y is written)")
    parser.add_argument("--toy-integration", choices=["y", "n"], default=None, help="Enable Bluetooth hardware telemetry integration (y/n)")
    parser.add_argument("--toy-mode", choices=["direct", "bridge", "all", "none"], default="direct", help="Telemetry mode: 'direct' (standalone client), 'bridge' (UDP 45735 telemetry), 'all' (dual mode), 'none'")
    parser.add_argument("--toy-profile", choices=["default", "easy", "mid", "hard", "mideasy", "midhard"], default="default", help="Default toy intensity profile ('default', 'easy', 'mid', 'hard', 'mideasy', 'midhard')")
    parser.add_argument("--toy-lead", type=int, choices=[0, 50, 100, 150, 200, 250, 300, 400, 500], default=200, help="Bluetooth latency compensation in ms: the in-game client sends the predicted stroke position this far ahead (default: 200)")
    parser.add_argument("--toy-port", type=int, default=12345, help="Intiface Central WebSocket port (default: 12345)")
    parser.add_argument("--toy-retries", type=int, default=5, help="Maximum connection retry attempts before in-game pause (default: 5)")
    parser.add_argument("--hmv-mode", action="store_true", default=False, help="Enable HMV audio beat-sync mode (UDP port 45736 & clickable bed speakers)")
    parser.add_argument("--export-toy-tools", action="store_true", default=False, help="Export companion telemetry tools to output/Telemetry_Suite/")
    parser.add_argument("--enable-toy-telemetry", action="store_true", default=False, help=argparse.SUPPRESS)

    args = parser.parse_args()
    verify_environment()
    patcher_dir = ROOT_DIR
    current_stage = "Initialization"

    try:
        current_stage = "Input Validation"
        utmt_cli = get_utmt_cli()
        LOGGER.log(f"Using UndertaleModCli: {utmt_cli}")

        source_folder = None
        source_apk = None

        input_dir = patcher_dir / "input"
        mod_subdirs = ["custom", "custom_stuff", "custom_futas", "custom_wives", "custom_bedrooms", "dialogue_packs", "texture_packs", "custom_sounds", "custom_music", "dialogue", "custom_dialogues"]

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
                    atexit.register(shutil.rmtree, str(tmp_extract), True)
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
                atexit.register(shutil.rmtree, str(combined_staging), True)
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
            mod_subdirs = ["custom", "custom_stuff", "custom_futas", "custom_wives", "custom_bedrooms", "dialogue_packs", "texture_packs", "custom_sounds", "custom_music", "dialogue", "custom_dialogues"]
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
            audit_ver = detect_mod_engine_version(Path(target_audit))
            audit_arch = "v15" if audit_ver == "1.5" else ("modroom33" if audit_ver == "modroom33" else "deeproom")
            skips = plan_pack_skips(target_audit, check_duplicates=getattr(args, "quarantine_duplicates", True),
                                    target_is_v15=(audit_arch == "v15"), target_arch=audit_arch)
            skip_dirs = {Path(x["path"]).resolve() for x in skips}
            custom_assets = gather_custom_assets(target_audit, is_v15=(audit_arch == "v15"), target_arch=audit_arch, skip_dirs=skip_dirs)
            LOGGER.log(f"Discovered {len(custom_assets)} custom asset file(s).")
            manifest_map = generate_manifest_data(target_audit, is_v15=(audit_arch == "v15"), skip_dirs=skip_dirs, target_arch=audit_arch)
            LOGGER.log(f"Generated {len(manifest_map)} Android _manifest.txt index file(s).")
            if skips:
                rep_md = write_skip_report(skips, patcher_dir / "output" / f"{sanitize_apk_part(Path(target_audit).name)}_validation", target_audit, mode="validate")
                LOGGER.log(f"Audit complete (read-only, nothing moved): {len(skips)} pack(s) would be skipped. Report: {rep_md}", prefix="[!]")
                return
            LOGGER.log("Audit complete (read-only, nothing moved): mod folder is portable and ready for compilation.", prefix="[+]")
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
        engine_label = "Wife's Bedroom v1.5" if target_version == "1.5" else "ModRoom v3.3 / Deeproom 4.0 (v1.4)"
        req_apk = "wifes_bedroom1_5.apk" if target_version == "1.5" else "wifes_bedroom1_4.apk"
        LOGGER.log(f"Target engine detected: Version {target_version} ({engine_label})", prefix="[*]")

        if args.base_apk:
            source_apk = Path(args.base_apk).resolve()

        if not source_apk:
            source_apk = find_matching_base_apk(input_dir, patcher_dir, target_version=target_version)

        if not source_apk or not source_apk.exists():
            raise FileNotFoundError(f"Base APK not found for {engine_label}. Please provide {req_apk} in the input/ folder (or drag it alongside your mod folder).")

        LOGGER.log(f"Matched Base APK: {source_apk.name}", prefix="[+]")
        if target_version == "1.5" and ("1_4" in source_apk.name or "1.4" in source_apk.name):
            LOGGER.log("Notice: Compiling v1.5 mods using a v1.4 base APK. For full native v1.5 stability, provide wifes_bedroom1_5.apk in the input/ folder.", prefix="[!]")

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
        if install_opts.get("clean_output"):
            clean_output_dir(output_apk.parent)
        patch_game_apk(utmt_cli, source_apk, output_apk, source_folder=source_folder, opts=install_opts)

    except Exception as exc:
        LOGGER.error(f"Process failed during [{current_stage}]: {exc}")
        LOGGER.write_error_report(exc, current_stage)
        sys.exit(1)
