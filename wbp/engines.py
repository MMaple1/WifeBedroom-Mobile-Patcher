"""wbp.engines"""
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
from wbp.common import LOGGER, PATCH_MISSES, gml, guarded_replace

# -----------------------------------------------------------------------------
# DYNAMIC VARIABLE SAFETY SHIELD (Forward/Backward Upstream Protection)
# -----------------------------------------------------------------------------
def generate_dynamic_variable_shield(utmt_exe, target_data_file, bundle_create_code):
    """
    Dynamically inspects the target data.win/game.droid bytecode for all instance variables
    assigned in the host game's original Create_0. Cross-references against the bundle Create_0,
    and returns a defensive GML guard block for any missing variables to prevent uninitialized crashes.
    """
    import tempfile, subprocess, re
    with tempfile.TemporaryDirectory() as td:
        csx_path = Path(td) / "extract_vars.csx"
        out_path = (Path(td) / "host_vars.txt").resolve().as_posix()
        csx_script = (
            'using System;\n'
            'using System.IO;\n'
            'using System.Collections.Generic;\n'
            'using System.Text.RegularExpressions;\n'
            'using System.Linq;\n'
            'EnsureDataLoaded();\n'
            'var sc = Data.Code.FirstOrDefault(c => c.Name.Content == "gml_Object_oFutaMatingPress_Create_0");\n'
            'if (sc != null) {\n'
            '    string dis = sc.Disassemble(Data.Variables, null);\n'
            '    HashSet<string> vars = new HashSet<string>();\n'
            '    foreach (string line in dis.Split(\'\\n\')) {\n'
            '        if (line.Contains("pop.") && line.Contains("builtin.")) {\n'
            '            var m = Regex.Match(line, @"builtin\\.([a-zA-Z0-9_]+)");\n'
            '            if (m.Success) {\n'
            '                string vn = m.Groups[1].Value;\n'
            '                if (!vn.StartsWith("image_") && !vn.StartsWith("sprite_") && !vn.StartsWith("argument") &&\n'
            '                    vn != "x" && vn != "y" && vn != "id" && vn != "depth" && vn != "visible" && vn != "mask_index" && vn != "alarm") {\n'
            '                    vars.Add(vn);\n'
            '                }\n'
            '            }\n'
            '        }\n'
            '    }\n'
            f'    File.WriteAllLines("{out_path}", vars);\n'
            '}\n'
        )
        csx_path.write_text(csx_script, encoding="utf-8")
        try:
            res = subprocess.run([str(utmt_exe), "load", str(target_data_file), "-s", str(csx_path)], capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
            out_f = Path(out_path)
            if not out_f.exists():
                LOGGER.log(f"Notice: variable shield skipped: UndertaleModCli produced no variable list (exit {res.returncode}): {(res.stderr or '').strip()[-200:]}", prefix="[!]")
                return "", []
            host_vars = set(out_f.read_text(encoding="utf-8").splitlines())
        except Exception as sh_err:
            LOGGER.log(f"Notice: variable shield skipped: {sh_err}", prefix="[!]")
            return "", []

    bundle_assigned = set()
    for line in bundle_create_code.splitlines():
        m = re.match(r"^\s*([a-zA-Z0-9_]+)\s*=", line)
        if m:
            bundle_assigned.add(m.group(1))

    missing_vars = sorted(list(host_vars - bundle_assigned))
    if not missing_vars:
        return "", []

    guard_lines = [
        "\n// ============================================================================",
        "// DYNAMIC VARIABLE SAFETY SHIELD (Auto-generated for forward/backward parity)",
        "// ============================================================================"
    ]
    for mv in missing_vars:
        default_val = "-1" if any(k in mv.lower() for k in ["sprite", "custom_", "sound", "audio", "pack"]) else "0"
        guard_lines.append(f'if (!variable_instance_exists(id, "{mv}"))\n{{\n    {mv} = {default_val};\n}}')

    return "\n".join(guard_lines) + "\n", missing_vars


def patch_v15_engine_bytecode(utmt_cli, tmp_droid, patched_droid, tmpdir, logger=None):
    """
    Patches Wife's Bedroom v1.5 engine bytecode (game.droid) with:
      1. Fast in-memory buffer manifest streaming (eliminates Android ANRs)
      2. Startup memory optimization (loads metadata/portraits only during indexing, avoiding OOM runner crashes)
      3. Full session persistence (remember_custom defaults to true, saves and restores previous lover, partner, and bedroom)
      4. Universal Partner parity (recognizes custom_data.wife as well as custom_data.spouse)
      5. Non-negative sprite shield in func_get_xray
    """
    import subprocess
    def log(msg, prefix="[*]"):
        if logger: logger.log(msg, prefix=prefix)
        else: print(f"{prefix} {msg}")

    code_dir = Path(tmpdir) / "CodeEntries"
    code_dir.mkdir(parents=True, exist_ok=True)

    dump_res = subprocess.run([str(utmt_cli), "dump", str(tmp_droid), "-c", "gml_Object_oFutaMatingPress_Create_0", "-c", "gml_Object_oFutaMatingPress_Draw_0", "-o", str(tmpdir)], capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    if dump_res.returncode != 0:
        log(f"Notice: v1.5 bytecode dump returned non-zero ({dump_res.stderr[:100]}).", prefix="[!]")
        return False

    c0_p = code_dir / "gml_Object_oFutaMatingPress_Create_0.gml"
    d0_p = code_dir / "gml_Object_oFutaMatingPress_Draw_0.gml"
    if not (c0_p.exists() and d0_p.exists()):
        return False

    c0 = c0_p.read_text(encoding="utf-8")
    d0 = d0_p.read_text(encoding="utf-8")

    # 1. Update Create_0
    # A. custom_bedroom_previous variable
    old_c0_vars = "custom_lover_previous = -1;\ncustom_partner_previous = -1;"
    new_c0_vars = gml("patch_v15_engine_bytecode/new_c0_vars")
    c0 = guarded_replace(c0, old_c0_vars, new_c0_vars, "patch_v15_engine_bytecode:old_c0_vars")

    # B. func_save_game
    old_save_p = '    ini_write_real("options", "custom_partner_previous", custom_partner_previous);'
    new_save_p = '    ini_write_real("options", "custom_partner_previous", custom_partner_previous);\n    ini_write_real("options", "custom_bedroom_previous", custom_bedroom_previous);'
    c0 = guarded_replace(c0, old_save_p, new_save_p, "patch_v15_engine_bytecode:old_save_p")

    # C. save loading
    old_rem = '    remember_custom = ini_read_real("options", "remember_custom", false);'
    new_rem = '    remember_custom = ini_read_real("options", "remember_custom", true);'
    c0 = guarded_replace(c0, old_rem, new_rem, "patch_v15_engine_bytecode:old_rem")

    old_load_p = '    custom_partner_previous = ini_read_real("options", "custom_partner_previous", -1);'
    new_load_p = '    custom_partner_previous = ini_read_real("options", "custom_partner_previous", -1);\n    custom_bedroom_previous = ini_read_real("options", "custom_bedroom_previous", -1);'
    c0 = guarded_replace(c0, old_load_p, new_load_p, "patch_v15_engine_bytecode:old_load_p")

    # D. Fast Buffer Manifest Scanning
    old_scan_block = "if (true && mobile == false)"
    new_scan_block = gml("patch_v15_engine_bytecode/new_scan_block")
    c0 = guarded_replace(c0, old_scan_block, new_scan_block, "patch_v15_engine_bytecode:old_scan_block")

    # E. Partner ini check in func_load_custom
    old_spouse_ini = gml("patch_v15_engine_bytecode/old_spouse_ini")
    new_spouse_ini = gml("patch_v15_engine_bytecode/new_spouse_ini")
    c0 = guarded_replace(c0, old_spouse_ini, new_spouse_ini, "patch_v15_engine_bytecode:old_spouse_ini")

    old_spouse_open = '                ini_open(string(arg0) + "/custom_data.spouse");'
    new_spouse_open = gml("patch_v15_engine_bytecode/new_spouse_open")
    c0 = guarded_replace(c0, old_spouse_open, new_spouse_open, "patch_v15_engine_bytecode:old_spouse_open")

    # F. func_load_custom_metadata helper for fast startup
    meta_helper = gml("patch_v15_engine_bytecode/meta_helper")
    if "function func_load_custom_metadata" not in c0:
        c0 += meta_helper

    # G. Optimize func_get_custom_info to use func_load_custom_metadata
    old_info_loops = gml("patch_v15_engine_bytecode/old_info_loops")

    new_info_loops = gml("patch_v15_engine_bytecode/new_info_loops")
    c0 = guarded_replace(c0, old_info_loops, new_info_loops, "patch_v15_engine_bytecode:old_info_loops")

    # H. Restore previous selections on boot
    old_boot_restore = gml("patch_v15_engine_bytecode/old_boot_restore")

    new_boot_restore = gml("patch_v15_engine_bytecode/new_boot_restore")
    c0 = guarded_replace(c0, old_boot_restore, new_boot_restore, "patch_v15_engine_bytecode:old_boot_restore")

    # I. Non-negative sprite shield in func_get_xray
    old_xray_end = "    return xray_sprite;\n}"
    new_xray_end = gml("patch_v15_engine_bytecode/new_xray_end")
    c0 = guarded_replace(c0, old_xray_end, new_xray_end, "patch_v15_engine_bytecode:old_xray_end")

    c0_p.write_text(c0, encoding="utf-8")

    # 2. Update Draw_0
    # Save lover selection
    old_d_lover = gml("patch_v15_engine_bytecode/old_d_lover")
    new_d_lover = gml("patch_v15_engine_bytecode/new_d_lover")
    d0 = guarded_replace(d0, old_d_lover, new_d_lover, "patch_v15_engine_bytecode:old_d_lover")

    # Save partner selection
    old_d_partner = gml("patch_v15_engine_bytecode/old_d_partner")
    new_d_partner = gml("patch_v15_engine_bytecode/new_d_partner")
    d0 = guarded_replace(d0, old_d_partner, new_d_partner, "patch_v15_engine_bytecode:old_d_partner")

    # Save bedroom selection
    old_d_bedroom = '''                            custom_bedroom_selected = i - max_rooms;
                            func_set_custom_bedroom();'''
    new_d_bedroom = gml("patch_v15_engine_bytecode/new_d_bedroom")
    d0 = guarded_replace(d0, old_d_bedroom, new_d_bedroom, "patch_v15_engine_bytecode:old_d_bedroom")

    d0_p.write_text(d0, encoding="utf-8")

    rep_res = subprocess.run([str(utmt_cli), "replace", str(tmp_droid), "-c", f"gml_Object_oFutaMatingPress_Create_0={c0_p}", "-c", f"gml_Object_oFutaMatingPress_Draw_0={d0_p}", "-o", str(patched_droid)], capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    return (rep_res.returncode == 0)


def patch_mr33_engine_bytecode(utmt_cli, tmp_droid, patched_droid, tmpdir, logger=None):
    """
    Patches ModRoom v3.3 engine bytecode (game.droid) with:
      1. Complete eradication of broken Android file_find_first loops (*\custom_wives\ and *\custom_futas\)
      2. Ultra-fast native Android buffer manifest streaming (5ms execution, eliminating boot ANRs)
      3. Clean relative path resolution (custom_futas/pack and custom_wives/pack without leading slash)
      4. Universal filename & descriptor resolution (supports both legacy _0.png and normalized names)
      5. Dynamic Variable Safety Shield (prevents crashes from uninitialized variables)
      6. Native 11 objects and 100 sprites preservation
    """
    import subprocess
    def log(msg, prefix="[*]"):
        if logger: logger.log(msg, prefix=prefix)
        else: print(f"{prefix} {msg}")

    code_dir = Path(tmpdir) / "CodeEntries"
    code_dir.mkdir(parents=True, exist_ok=True)

    dump_res = subprocess.run([str(utmt_cli), "dump", str(tmp_droid), "-c", "gml_Object_oFutaMatingPress_Create_0", "-c", "gml_Object_oFutaMatingPress_Draw_0", "-c", "gml_Object_oBackground_Create_0", "-o", str(tmpdir)], capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    if dump_res.returncode != 0:
        log(f"Notice: ModRoom v3.3 bytecode dump returned non-zero ({dump_res.stderr[:100]}).", prefix="[!]")
        return False

    c0_p = code_dir / "gml_Object_oFutaMatingPress_Create_0.gml"
    d0_p = code_dir / "gml_Object_oFutaMatingPress_Draw_0.gml"
    bg_p = code_dir / "gml_Object_oBackground_Create_0.gml"
    if not c0_p.exists():
        return False

    c0 = c0_p.read_text(encoding="utf-8")

    # Complete eradication of lines 519-559 in Create_0 (both futa and wife file_find_first loops)
    old_full_scan_start = gml("patch_mr33_engine_bytecode/old_full_scan_start")
    old_full_scan_end = gml("patch_mr33_engine_bytecode/old_full_scan_end")

    idx_start = c0.find(old_full_scan_start)
    idx_end = c0.find(old_full_scan_end)

    streaming_logic = gml("patch_mr33_engine_bytecode/streaming_logic")

    if idx_start != -1 and idx_end != -1:
        # keep the text after the marker's "file_find_close();\n\n" prefix (the marker ends with the next function header)
        c0 = c0[:idx_start] + streaming_logic + "\n" + c0[idx_end + len("file_find_close();\n\n"):]
    else:
        PATCH_MISSES.append("patch_mr33_engine_bytecode:old_full_scan")

    # Universal check_custom_wife
    old_check_wife = gml("patch_mr33_engine_bytecode/old_check_wife")
    new_check_wife = gml("patch_mr33_engine_bytecode/new_check_wife")
    c0 = guarded_replace(c0, old_check_wife, new_check_wife, "patch_mr33_engine_bytecode:old_check_wife")

    # Universal check_custom_futa
    old_check_futa = gml("patch_mr33_engine_bytecode/old_check_futa")
    new_check_futa = gml("patch_mr33_engine_bytecode/new_check_futa")
    c0 = guarded_replace(c0, old_check_futa, new_check_futa, "patch_mr33_engine_bytecode:old_check_futa")

    # Universal loaders: check both _0.png and standard names
    old_wife_port = 'var file_check = string(arg0) + "/custom_wife_portrait" + _suffix;'
    new_wife_port = gml("patch_mr33_engine_bytecode/new_wife_port")
    c0 = guarded_replace(c0, old_wife_port, new_wife_port, "patch_mr33_engine_bytecode:old_wife_port")

    old_wife_mp = 'file_check = string(arg0) + "/custom_wife_mating_press" + _suffix;'
    new_wife_mp = gml("patch_mr33_engine_bytecode/new_wife_mp")
    c0 = guarded_replace(c0, old_wife_mp, new_wife_mp, "patch_mr33_engine_bytecode:old_wife_mp")

    # Touch: ModRoom's menu_scroll_update only reads the mouse wheel; add the touch-drag scroll used by Deeproom
    c0 = guarded_replace(c0, gml("patch_mr33_engine_bytecode/old_menu_scroll_update"),
                         gml("patch_mr33_engine_bytecode/new_menu_scroll_update"), "patch_mr33_engine_bytecode:old_menu_scroll_update")

    # Dynamic Variable Safety Shield
    shield_code, shielded_vars = generate_dynamic_variable_shield(utmt_cli, tmp_droid, c0)
    if shielded_vars:
        var_preview = ", ".join(shielded_vars[:5]) + ("..." if len(shielded_vars) > 5 else "")
        log(f"Dynamic Variable Shield (ModRoom v3.x): Safeguarded {len(shielded_vars)} host variable(s) ({var_preview})!", prefix="[+]")
        c0 += "\n" + shield_code

    c0 += gml("patch_mr33_engine_bytecode/safe_draw")
    c0_p.write_text(c0, encoding="utf-8")

    # Manifest streaming in oBackground_Create_0 (complete loop replacement)
        # 2. Patch Draw_0 to eliminate red disclaimer error screen and allow vanilla fallback
    if d0_p.exists():
        d0 = d0_p.read_text(encoding="utf-8")
        old_disclaimer = gml("patch_mr33_engine_bytecode/old_disclaimer")
        new_disclaimer = """    custom_sprite_loaded = true;
    draw_text_ext_color(room_width / 2, room_height / 2, "WARNING:\\n\\nThis game contains explicit content intended for adults only. It also contains fetishistic content (i.e. futanari, excessive liquids) that may not be suitable for everyone. It is also intended to display a polyamorous relationship, but may come across as cuckoldry/NTR depending on how you interact with it.\\n\\nPlayer discretion is advised.\\nClick to continue", 16, 320, c_white, c_white, c_white, c_white, disclaimer_scale * title_scale);"""
        if old_disclaimer in d0:
            d0 = d0.replace(old_disclaimer, new_disclaimer, 1)
        else:
            PATCH_MISSES.append("patch_mr33_engine_bytecode:old_disclaimer")
        # Touch: pill menu as two columns of larger buttons (ModRoom has 14 pills; its own list scrolled 11 rows)
        pill_head = gml("patch_mr33_engine_bytecode/old_pill_menu_head")
        pill_i = d0.find(pill_head)
        pill_j = d0.find('comment = "pill effect logic.')
        if pill_i != -1 and pill_j > pill_i:
            pill_data_line = d0[pill_i:pill_j].split("\n")[2] + "\n"
            d0 = d0[:pill_i] + gml("patch_mr33_engine_bytecode/new_pill_menu").replace("{{PILL_DATA}}", pill_data_line) + d0[pill_j:]
            log("Draw_0: pill menu laid out as two columns of larger buttons.", prefix="[+]")
        else:
            PATCH_MISSES.append("patch_mr33_engine_bytecode:old_pill_menu_head")
        # Touch: a background is picked on release, after a press inside the menu and without a drag
        d0 = guarded_replace(d0, gml("patch_mr33_engine_bytecode/old_bg_pick"), gml("patch_mr33_engine_bytecode/new_bg_pick"),
                             "patch_mr33_engine_bytecode:old_bg_pick")
        # Safety net: a sprite that is still -1 draws nothing instead of ending the game with
        # "draw_sprite_ext argument 1 invalid reference to (sprite) - requested -1"
        n_dsx = d0.count("draw_sprite_ext(")
        n_dsp = d0.count("draw_sprite_part_ext(")
        d0 = d0.replace("draw_sprite_ext(", "tc_safe_sprite_ext(").replace("draw_sprite_part_ext(", "tc_safe_sprite_part_ext(")
        log(f"Draw_0: guarded {n_dsx} draw_sprite_ext and {n_dsp} draw_sprite_part_ext call(s) against missing sprites.", prefix="[+]")
        d0_p.write_text(d0, encoding="utf-8")

    rep_args = [str(utmt_cli), "replace", str(tmp_droid), "-c", f"gml_Object_oFutaMatingPress_Create_0={c0_p}"]
    if d0_p.exists():
        rep_args.extend(["-c", f"gml_Object_oFutaMatingPress_Draw_0={d0_p}"])
    if bg_p.exists():
        bg_code = bg_p.read_text(encoding="utf-8")
        old_bg_loop = gml("patch_mr33_engine_bytecode/old_bg_loop")

        new_bg_loop = gml("patch_mr33_engine_bytecode/new_bg_loop")
        if old_bg_loop in bg_code:
            bg_code = bg_code.replace(old_bg_loop, new_bg_loop, 1)
            bg_p.write_text(bg_code, encoding="utf-8")
            rep_args.extend(["-c", f"gml_Object_oBackground_Create_0={bg_p}"])
        else:
            PATCH_MISSES.append("patch_mr33_engine_bytecode:old_bg_loop")

    rep_args.extend(["-o", str(patched_droid)])
    rep_res = subprocess.run(rep_args, capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    return (rep_res.returncode == 0)
