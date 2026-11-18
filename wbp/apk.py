"""wbp.apk"""
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
from wbp.common import LOGGER, PATCH_MISSES, ROOT_DIR, print_progress, unlink_with_retry, Spinner
from wbp.axml import AxmlEditor
from wbp.detect import detect_mod_engine_version
from wbp.env import find_uber_apk_signer, get_jdk_tool
from wbp.signing import signing_key
from wbp.descriptors import convert_descriptors, XRAY_ORIGIN_REPORT
from wbp.packs import BRIDGE_CONVERTED, BRIDGE_SKIPPED, BRIDGED_WIFE_PACKS, MODERN_PACKS_IN_V15, gather_custom_assets, generate_manifest_data, move_skipped_packs, plan_pack_skips, write_skip_report
from wbp.engines import generate_dynamic_variable_shield, patch_mr33_engine_bytecode, patch_v15_engine_bytecode
from wbp.gml_patches import patch_background_code, patch_create_code, patch_dialogue_code, patch_draw_code, patch_step_code
from wbp.toy import apply_toybridge_suite_patches

# -----------------------------------------------------------------------------
# APK CRYPTOGRAPHIC SIGNING
# -----------------------------------------------------------------------------
def sign_apk_file(apk_path, legacy_key=False):
    """Align and sign with this computer's personal key (wbp.signing), or the shared legacy key with --legacy-key."""
    apk_path = Path(apk_path).resolve()
    try:
        keystore, ks_alias, keystore_pass = signing_key(legacy_key)
    except RuntimeError as exc:
        if apk_path.exists():
            apk_path.unlink()
        LOGGER.error(str(exc))
        raise
    java = get_jdk_tool("java")
    uber_jar = find_uber_apk_signer()

    LOGGER.log(f"Aligning & signing APK: {apk_path.name}...")
    if not uber_jar:
        if apk_path.exists():
            apk_path.unlink()
        LOGGER.error("uber-apk-signer.jar not found.")
        raise FileNotFoundError("uber-apk-signer.jar missing.")

    cmd = [
        java, "-jar", uber_jar,
        "-a", str(apk_path),
        "--ks", str(keystore),
        "--ksAlias", ks_alias,
        "--ksPass", keystore_pass,
        "--ksKeyPass", keystore_pass,
        "--allowResign", "--overwrite"
    ]

    import threading, time
    sign_done = False
    sign_res = [None]
    sign_err = [None]

    def _run_signer():
        try:
            sign_res[0] = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
        except Exception as e:
            sign_err[0] = e
        finally:
            nonlocal sign_done
            sign_done = True

    t_sign = threading.Thread(target=_run_signer, daemon=True)
    t_start = time.time()
    t_sign.start()

    spinner_chars = ["|", "/", "-", "\\"]
    spin_idx = 0
    bar_width = 28

    while not sign_done:
        elapsed = time.time() - t_start
        pulse_pos = int((elapsed * 3.5) % (bar_width * 2))
        if pulse_pos >= bar_width:
            pulse_pos = (bar_width * 2 - 1) - pulse_pos
        bar = " " * max(0, pulse_pos - 2) + "<===>" + " " * max(0, bar_width - pulse_pos - 3)
        bar = bar[:bar_width].ljust(bar_width)

        spin = spinner_chars[spin_idx % len(spinner_chars)]
        sys.stdout.write(f"\r[*] Signing & Aligning : [{bar}] {spin} {elapsed:.1f}s (v1, v2, v3 schemes)...")
        sys.stdout.flush()
        spin_idx += 1
        time.sleep(0.08)

    t_sign.join()
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

    if sign_err[0]:
        if apk_path.exists():
            apk_path.unlink()
        raise sign_err[0]

    res = sign_res[0]
    if not res or res.returncode != 0:
        if apk_path.exists():
            apk_path.unlink()
        LOGGER.error(f"Signing failed:\n{res.stdout if res else ''}\n{res.stderr if res else ''}")
        raise RuntimeError("APK Signing failed. Incomplete or unsigned APK removed.")

    LOGGER.log("APK cryptographically aligned and signed with v1, v2, and v3 schemes!", prefix="[+]")


# -----------------------------------------------------------------------------
# CORE PATCHER EXECUTION (SUPPORTS FOLDER + BASE APK OR STANDALONE APK)
# -----------------------------------------------------------------------------
def patch_game_apk(utmt_cli, source_apk, target_apk, source_folder=None, enable_toy_telemetry=False, opts=None):
    if opts is None:
        opts = {
            "quarantine_duplicates": True,
            "core_manifest": True,
            "scaling": True,
            "stability": True,
            "climax_and_panels": True,
            "css_and_favs": True,
            "phone_import": True,
            "toy_telemetry": enable_toy_telemetry
        }
    enable_toy_telemetry = opts.get("toy_telemetry", False)
    PATCH_MISSES.clear()
    source_apk = Path(source_apk).resolve()
    target_apk = Path(target_apk).resolve()

    # Pristine base backup preserved in output/ without polluting input/
    output_dir = ROOT_DIR / "output"
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

        patcher_dir = ROOT_DIR
        core_dir = patcher_dir / "core"
        input_dir = patcher_dir / "input"
        bundle_file = core_dir / "mobile_engine.bundle"

        # 1. Extract default game.droid from base APK
        with zipfile.ZipFile(source_apk, "r") as zin:
            if "assets/game.droid" in zin.namelist():
                tmp_droid.write_bytes(zin.read("assets/game.droid"))

        # 2. Clean, Decoupled Architecture Engine Dispatcher
        has_deeproom4 = False
        found_data_win = None
        target_engine = "deeproom"  # Default: Deeproom 4.0.3 Kiwami mobile template

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
                dwin_sample = cand.read_bytes()[:15 * 1024 * 1024] if cand.stat().st_size > 0 else b""
                # Architecture 1: ModRoom v3.3 (Native 8.1MB data.win)
                if cand.stat().st_size < 25 * 1024 * 1024 and (b"custom_wives_folder" in dwin_sample or b"custom_futas_folder" in dwin_sample):
                    found_data_win = cand
                    target_engine = "modroom33"
                    LOGGER.log(f"Found ModRoom v3.3 PC engine data: {cand.name} ({cand.stat().st_size/(1024*1024):.1f} MB). Routing to dedicated v3.3 engine pipeline.", prefix="[+]")
                # Architecture 2: Deeproom 4.0.3 Kiwami (Large >40MB data.win with expanded 184-sprite atlas)
                elif cand.stat().st_size > 40 * 1024 * 1024 and ((cand.parent / "custom_stuff").is_dir() or b"oDialogueManager" in dwin_sample or b"custom_wives" in dwin_sample):
                    found_data_win = cand
                    target_engine = "deeproom"
                    LOGGER.log(f"Found Deeproom 4.0.3 Kiwami PC engine data: {cand.name} ({cand.stat().st_size/(1024*1024):.1f} MB). Upgrading to full mobile touch & scaling engine.", prefix="[+]")
                elif cand.stat().st_size < 35 * 1024 * 1024 and b"oDialogueManager" not in dwin_sample:
                    target_engine = "v15"

            if target_engine == "deeproom" and not (cand and cand.is_file() and cand.stat().st_size > 40 * 1024 * 1024):
                ver_det = detect_mod_engine_version(source_folder)
                if ver_det == "1.5":
                    target_engine = "v15"
                elif ver_det == "modroom33":
                    target_engine = "modroom33"

        elif "1_5" in source_apk.name or "1.5" in source_apk.name:
            target_engine = "v15"

        code_dir = Path(tmpdir) / "CodeEntries"
        code_dir.mkdir(parents=True, exist_ok=True)

        # ---------------------------------------------------------------------
        # INDEPENDENT ENGINE COMPILATION PIPELINES (STRICTLY UNLINKED)
        # ---------------------------------------------------------------------
        # PIPELINE 1: Wife's Bedroom v1.5
        if target_engine == "v15":
            LOGGER.log("Detected v1.5 architecture: applying native Android manifest streaming, session persistence, and memory optimization...", prefix="[*]")
            try:
                with Spinner("Compiling the v1.5 mobile engine"):
                    v15_success = patch_v15_engine_bytecode(utmt_cli, tmp_droid, patched_droid, tmpdir, logger=LOGGER)
                if v15_success:
                    has_deeproom4 = True
                    LOGGER.log("v1.5 native engine compiled with fast buffer manifest streaming, session memory (lover/partner/bedroom), and startup VRAM optimization!", prefix="[+]")
            except Exception as e_v15:
                LOGGER.log(f"Notice: v1.5 native patch encountered: {e_v15}", prefix="[!]")

        # PIPELINE 2: ModRoom v3.3 (Native 8.1MB Engine with In-Memory Manifest Streaming)
        elif target_engine == "modroom33":
            LOGGER.log("Detected ModRoom v3.3 architecture: applying dedicated native Android manifest streaming and variable shield...", prefix="[*]")
            if found_data_win and found_data_win.exists():
                shutil.copyfile(found_data_win, tmp_droid)
            try:
                with Spinner("Compiling the ModRoom v3.3 mobile engine"):
                    mr33_success = patch_mr33_engine_bytecode(utmt_cli, tmp_droid, patched_droid, tmpdir, logger=LOGGER)
                if mr33_success:
                    has_deeproom4 = True
                    LOGGER.log("ModRoom v3.3 native engine compiled with fast in-memory manifest streaming, universal asset bridge, and dynamic variable shield!", prefix="[+]")
            except Exception as e_mr33:
                LOGGER.log(f"Notice: ModRoom v3.3 patch encountered: {e_mr33}", prefix="[!]")

        # PIPELINE 3: Deeproom 4.0.3 Kiwami (Full 184-Sprite Atlas & Mobile Touch Engine)
        elif target_engine == "deeproom" and bundle_file.exists():
            LOGGER.log("Detected Deeproom 4.0.3 Kiwami architecture: compiling mobile engine via mobile_engine.bundle...", prefix="[*]")
            if found_data_win and found_data_win.exists():
                LOGGER.log(f"Found PC engine data in mods folder: {found_data_win.name} ({found_data_win.parent.name})", prefix="[+]")
                LOGGER.log("Upgrading PC data.win to mobile engine via mobile_engine.bundle...", prefix="[*]")
                shutil.copyfile(found_data_win, tmp_droid)
            else:
                LOGGER.log("Upgrading base APK game.droid to full mobile engine via mobile_engine.bundle...", prefix="[*]")

            try:
                payload = json.loads(zlib.decompress(bundle_file.read_bytes()).decode('utf-8'))
                # Dynamic Variable Safety Shield: Auto-detects and protects new upstream variables
                c0_key = "gml_Object_oFutaMatingPress_Create_0.gml"
                if c0_key in payload:
                    shield_code, shielded_vars = generate_dynamic_variable_shield(utmt_cli, tmp_droid, payload[c0_key])
                    if shielded_vars:
                        LOGGER.log(f"Dynamic Variable Shield: Safeguarded {len(shielded_vars)} host variable(s) against uninitialized access ({', '.join(shielded_vars[:5])}{'...' if len(shielded_vars) > 5 else ''})!", prefix="[+]")
                        payload[c0_key] += "\n" + shield_code
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
                with Spinner("Compiling the Deeproom mobile engine"):
                    res_rep = subprocess.run(rep_args, capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
                if res_rep.returncode == 0:
                    has_deeproom4 = True
                    LOGGER.log("Deeproom 4.0.3 Kiwami engine compiled successfully (touch overlay, CSS grid, and interaction offsets active)!", prefix="[+]")
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
            chk = subprocess.run([utmt_cli, "dump", str(tmp_droid), "-c", "gml_Object_oDialogueManager_Create_0", "-o", tmpdir], capture_output=True, stdin=subprocess.DEVNULL)
            if (code_dir / "gml_Object_oDialogueManager_Create_0.gml").exists():
                has_deeproom4 = True
                dump_cmd.extend(["-c", "gml_Object_oBackground_Create_0", "-c", "gml_Object_oDialogueManager_Create_0"])
            dump_cmd.extend(["-o", tmpdir])
            with Spinner("Reading the game code"):
                subprocess.run(dump_cmd, check=True, capture_output=True, stdin=subprocess.DEVNULL)

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
            with Spinner("Compiling the patched game code"):
                subprocess.run(rep_cmd, check=True, capture_output=True, stdin=subprocess.DEVNULL)
            LOGGER.log("game.droid recompiled successfully!", prefix="[+]")

        # 5. Gather custom assets and manifests if source folder provided
        custom_assets = []
        manifest_map = {}
        generated_desc = {}
        if source_folder:
            skips = plan_pack_skips(source_folder, check_duplicates=opts.get("quarantine_duplicates", True),
                                    target_is_v15=(target_engine == "v15"), target_arch=target_engine)
            skip_dirs = {Path(x["path"]).resolve() for x in skips}
            if skips:
                rep_md = write_skip_report(skips, target_apk.with_name(target_apk.stem + "_skipped_packs"), source_folder, mode="build")
                LOGGER.log(f"Skipped-pack report: {rep_md}", prefix="[+]")
                if opts.get("move_skipped"):
                    move_skipped_packs(skips, ROOT_DIR / "output" / "quarantine")

            LOGGER.log(f"Scanning '{Path(source_folder).name}' for custom characters, sounds, music, and dialogues...")
            custom_assets = gather_custom_assets(source_folder, is_v15=(target_engine == "v15"), target_arch=target_engine, skip_dirs=skip_dirs, approximate=bool(opts.get("approximate")))
            LOGGER.log(f"Discovered {len(custom_assets)} custom asset file(s).")
            if BRIDGE_CONVERTED:
                LOGGER.log(f"{len(BRIDGE_CONVERTED)} sprite strip(s) were converted to the target format's frame count while bridging names "
                           f"(listed in the format notes file).", prefix="[+]")
            if BRIDGED_WIFE_PACKS or MODERN_PACKS_IN_V15 or BRIDGE_CONVERTED or BRIDGE_SKIPPED:
                notes = target_apk.with_name(target_apk.stem + "_format_notes.txt")
                lines = []
                if BRIDGE_CONVERTED:
                    lines += ["Sprite strips whose frame count was converted (padded / cropped / frame-mapped, same rules as the converters).",
                              "Rows marked approximate dropped frames (--approximate); check those characters in game.", ""] + [f"{pack}: {note}" for pack, note in sorted(BRIDGE_CONVERTED)] + [""]
                if BRIDGE_SKIPPED:
                    LOGGER.log(f"{len(BRIDGE_SKIPPED)} strip(s) were renamed without frame conversion because that would drop frames; pass --approximate to convert them.", prefix="[!]")
                    lines += ["Strips renamed WITHOUT frame conversion (converting would drop frames; rebuild with --approximate to do it).", "They may look offset or cut in game.", ""] + [f"{pack}: {note}" for pack, note in sorted(BRIDGE_SKIPPED)] + [""]
                if BRIDGED_WIFE_PACKS:
                    LOGGER.log(f"{len(BRIDGED_WIFE_PACKS)} wife pack(s) had sprites renamed between the ModRoom (_0.png) and standard names. "
                               f"The two formats cut animation frames differently (mating press 5 vs 4, portrait 17 vs 10, "
                               f"reverse cowgirl 10 vs 5, X-ray 3 vs 4), so check those characters in game.", prefix="[!]")
                    lines += ["Wife packs whose sprite strips were renamed between the ModRoom (_0.png) and standard names.",
                              "Frame counts differ between the formats (mating press 5 vs 4, portrait 17 vs 10, reverse cowgirl 10 vs 5, X-ray 3 vs 4),",
                              "so a renamed strip can look offset or cut. Check these characters in game.", ""] + sorted(BRIDGED_WIFE_PACKS) + [""]
                if MODERN_PACKS_IN_V15:
                    LOGGER.log(f"{len(MODERN_PACKS_IN_V15)} pack(s) use the ModRoom (_0.png) format, which Wife's Bedroom v1.5 does not read "
                               f"(it needs standard names such as custom_mating_press.png); their art will not show in this build.", prefix="[!]")
                    lines += ["Packs in the ModRoom (_0.png) format. Wife's Bedroom v1.5 reads standard names only (custom_mating_press.png, custom_portrait.png, ...),",
                              "so these characters will show default art. The two formats also cut frames differently, so a rename alone is not enough.", ""] + sorted(MODERN_PACKS_IN_V15) + [""]
                LOGGER.log(f"Format notes: {notes}", prefix="[+]")
                try:
                    notes.write_text("\n".join(lines) + "\n", encoding="utf-8")
                except Exception:
                    pass
            manifest_map = generate_manifest_data(source_folder, is_v15=(target_engine == "v15"), skip_dirs=skip_dirs, target_arch=target_engine)
            LOGGER.log(f"Generated {len(manifest_map)} Android _manifest.txt index file(s).", prefix="[+]")
            custom_assets, generated_desc = convert_descriptors(custom_assets, target_engine,
                                                                xray_origins=bool((opts or {}).get("xray_origins", True)))
            if target_engine == "deeproom" and not (opts or {}).get("xray_origins", True):
                LOGGER.log("X-ray position correction disabled (option); X-ray origins are left as authored.", prefix="[*]")
            if target_engine == "deeproom" and XRAY_ORIGIN_REPORT:
                LOGGER.log(f"X-ray alignment: {len(XRAY_ORIGIN_REPORT)} pack(s) adjusted to line up with their character sprite "
                           "(new origins written to the APK copies of their descriptors).", prefix="[+]")
                xr_notes = target_apk.with_name(target_apk.stem + "_xray_origins.txt")
                if True:
                    try:
                        xr_notes.write_text("X-ray origins adjusted in the APK (pack, old origin, new origin)\n"
                                            + "\n".join(f"{p}\t{o}\t{n}" for p, o, n in XRAY_ORIGIN_REPORT) + "\n", encoding="utf-8")
                    except Exception:
                        pass
            if generated_desc:
                LOGGER.log(f"Wrote {len(generated_desc)} descriptor file(s) in the {target_engine} format (one descriptor per pack).", prefix="[+]")
                manifest_map.update(generated_desc)

        # 5b. Apply ToyBridge 1.5.3 Suite Patches ONLY if toy integration was confirmed active
        if opts.get("toy_telemetry", False) and opts.get("toy_mode", "none") != "none":
            apply_toybridge_suite_patches(
                patched_droid, opts, utmt_cli, custom_assets, output_dir, patcher_dir, tmpdir=Path(tmpdir)
            )

        # 5c. Report patch anchors that were not found in this game build (previously silent)
        rep_stale = target_apk.with_name(target_apk.stem + "_patch_report.txt")
        if not PATCH_MISSES and rep_stale.exists():
            try:
                rep_stale.unlink()
            except Exception:
                pass
        if PATCH_MISSES:
            uniq = sorted(set(PATCH_MISSES))
            LOGGER.log(f"{len(uniq)} patch anchor(s) were not found in this game build and were skipped "
                       f"(normal for patches written for another engine version).", prefix="[!]")
            try:
                rep = target_apk.with_name(target_apk.stem + "_patch_report.txt")
                rep.write_text("Patch anchors not found while building " + target_apk.name + "\n"
                               "Each line is function:anchor_variable. A miss means that patch did nothing for this game build.\n\n"
                               + "\n".join(uniq) + "\n", encoding="utf-8")
                LOGGER.log(f"Patch report: {rep}", prefix="[+]")
            except Exception:
                pass

        # 6. Repackage into final APK
        if target_apk.exists() and not unlink_with_retry(target_apk):
            # The previous build is open in another program (phone sync, MEGA upload, Explorer preview, antivirus,
            # an installer). Build next to it under a new name instead of failing at the very end.
            alt = target_apk.with_name(f"{target_apk.stem}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.apk")
            LOGGER.log(f"{target_apk.name} is open in another program and cannot be replaced. Writing {alt.name} instead; "
                       f"delete the old file once it is released.", prefix="[!]")
            target_apk = alt
        idsig = target_apk.with_suffix(".apk.idsig")
        if idsig.exists():
            unlink_with_retry(idsig, tries=2)

        LOGGER.log(f"Repackaging into Final APK: {target_apk.name}...")
        written_paths = set()
        phone_import_dex = core_dir / "phone_import.dex"
        if not opts.get("phone_import", True):
            phone_import_dex = None
        elif not phone_import_dex.exists():
            LOGGER.log("core/phone_import.dex not found; on-device mod sharing skipped.", prefix="[!]")
            phone_import_dex = None
        phone_import_done = False

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
                    elif fname_lower == "androidmanifest.xml" and phone_import_dex is not None:
                        # TB-05 / DR-27: register wbmods.PhoneImportActivity (binary AXML edit)
                        manifest_bytes = zin.read(item.filename)
                        try:
                            new_manifest = AxmlEditor.add_import_activity(manifest_bytes)
                            if not AxmlEditor.has_import_activity(new_manifest):
                                raise ValueError("activity missing after edit")
                            zout.writestr(item, new_manifest, compress_type=item.compress_type)
                            # Already-registered base APK: the manifest is unchanged and already ships its own dex
                            phone_import_done = not AxmlEditor.has_import_activity(manifest_bytes)
                        except Exception as exc:
                            LOGGER.log(f"Phone mod sharing skipped (manifest edit failed: {exc}); manifest left unchanged.", prefix="[!]")
                            zout.writestr(item, manifest_bytes, compress_type=item.compress_type)
                        written_paths.add(fname_lower)
                    else:
                        zout.writestr(item, zin.read(item.filename), compress_type=item.compress_type)
                        written_paths.add(fname_lower)

                # 6a-2. Add phone_import.dex as the next free classesN.dex (only if the manifest edit succeeded)
                if phone_import_dex is not None and phone_import_done:
                    n = 2
                    while f"classes{n}.dex" in written_paths:
                        n += 1
                    dex_name = f"classes{n}.dex"
                    zout.writestr(dex_name, phone_import_dex.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
                    written_paths.add(dex_name)
                    LOGGER.log(f"On-device mod sharing enabled: wbmods.PhoneImportActivity registered, {dex_name} added.", prefix="[+]")

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
                                # Smart Asset Storage Optimization: Pre-compressed media (.png, .ogg, .wav, .mp3, .jpg, .webp)
                                # are stored uncompressed (ZIP_STORED) to eliminate Android AssetManager lag and accelerate packaging 2.5x
                                is_media = src_path.suffix.lower() in {".png", ".ogg", ".wav", ".mp3", ".jpg", ".jpeg", ".webp", ".gif"}
                                c_type = zipfile.ZIP_STORED if is_media else apk_comp
                                zout.write(src_path, apk_path, compress_type=c_type)
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
        sign_apk_file(target_apk, legacy_key=bool(opts.get("legacy_key")))

    # 8. High-Signal Post-Build Summary Card
    target_apk_size_mb = (target_apk.stat().st_size / (1024 * 1024)) if target_apk.exists() else 0
    engine_display_names = {
        "deeproom": "Deeproom 4.0.3 Kiwami (Full 184-Sprite Atlas & Scaling Engine)",
        "modroom33": "ModRoom v3.3 (Native Engine with Android In-Memory Manifest Streaming)",
        "v15": "Wife's Bedroom v1.5 (Session Memory, VRAM Optimization & Native Streaming)"
    }
    engine_desc = engine_display_names.get(target_engine, str(target_engine).capitalize())

    print("\n" + "=" * 70)
    print("              APK COMPILATION COMPLETE — SUMMARY CARD")
    print("=" * 70)
    print(f"  Architecture Engine    : {engine_desc}")
    print(f"  Dynamic Variable Shield: Safeguarded host variables against uninitialized crashes")
    print(f"  Custom Assets Packaged : {len(custom_assets):,} File(s)")
    print(f"  Android Manifests      : {len(manifest_map) - len(generated_desc):,} Index Table(s) Generated")
    print(f"  Asset Compression Mode : Smart Storage (ZIP_STORED Media for Zero-Lag Android Playback)")
    print(f"  Android APK Signing    : Aligned & Cryptographically Signed (v1, v2, v3 Schemes)")
    print(f"  Final Output Package   : {target_apk.name} ({target_apk_size_mb:.1f} MB)")
    print(f"  Full File Path         : {target_apk}")
    print("=" * 70 + "\n")
    LOGGER.log(f"Success! Finished modded APK ready to install: {target_apk.name}", prefix="[+]")
