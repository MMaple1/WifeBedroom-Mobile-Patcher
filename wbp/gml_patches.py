"""wbp.gml_patches"""
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
# GML SCRIPT PATCHING ROUTINES (WITH VERSION REDUNDANCY)
# -----------------------------------------------------------------------------
def patch_common_tc_funcs(code):
    """Patches tc_norm_path and tc_ff_* using exact function boundaries to eliminate native loops on Android."""
    old_norm = gml("patch_common_tc_funcs/old_norm")

    new_norm = gml("patch_common_tc_funcs/new_norm")

    code = guarded_replace(code, old_norm, new_norm, "patch_common_tc_funcs:old_norm")

    old_tde = gml("patch_common_tc_funcs/old_tde")

    new_tde = gml("patch_common_tc_funcs/new_tde")
    code = guarded_replace(code, old_tde, new_tde, "patch_common_tc_funcs:old_tde")

    new_tc_all = gml("patch_common_tc_funcs/new_tc_all")

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
    old_bg_scan = gml("patch_background_code/old_bg_scan")

    new_bg_scan = gml("patch_background_code/new_bg_scan")
    code = guarded_replace(code, old_bg_scan, new_bg_scan, "patch_background_code:old_bg_scan")
    LOGGER.log("oBackground_Create_0: Neutralized native filesystem loops and scanned custom bedrooms.", prefix="[+]")
    return code


def patch_dialogue_code(code):
    """Patches oDialogueManager_Create_0 to eliminate dialogue manifest loop hangs on Android."""
    code = patch_common_tc_funcs(code)
    old_dlg_parse = gml("patch_dialogue_code/old_dlg_parse")

    new_dlg_parse = gml("patch_dialogue_code/new_dlg_parse")

    old_dlg_load_full = gml("patch_dialogue_code/old_dlg_load_full")

    new_dlg_load_full = gml("patch_dialogue_code/new_dlg_load_full")

    code = guarded_replace(code, old_dlg_load_full, new_dlg_load_full, "patch_dialogue_code:old_dlg_load_full")

    code = guarded_replace(code, old_dlg_parse, new_dlg_parse, "patch_dialogue_code:old_dlg_parse")
    # Dialogue Packs Precedence Over Character Dialogue
    old_top_dlg = gml("patch_dialogue_code/old_top_dlg")
    new_top_dlg = gml("patch_dialogue_code/new_top_dlg")
    code = guarded_replace(code, old_top_dlg, new_top_dlg, "patch_dialogue_code:old_top_dlg")

    LOGGER.log("oDialogueManager_Create_0: Neutralized native filesystem loops and protected dialogue JSON parsing.", prefix="[+]")
    return code


def patch_create_code(code, enable_toy_telemetry=False, opts=None):
    if opts is None: opts = {}
    """Patches Create_0 with variable safety, C ovulation disentanglement, and pill fallbacks."""
    code = patch_common_tc_funcs(code)
    if "boob_box = false;" not in code:
        code = "boob_box = false;\n" + code
        LOGGER.log("Create_0: Initialized boob_box = false upfront.", prefix="[+]")

    old_futa_origins = gml("patch_create_code/old_futa_origins")

    new_futa_origins = gml("patch_create_code/new_futa_origins")

    if old_futa_origins in code:
        code = code.replace(old_futa_origins, new_futa_origins, 1)
        LOGGER.log("Create_0: Initialized cowgirl_origin_y upfront.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_futa_origins")

    old_climax_ov = gml("patch_create_code/old_climax_ov")

    new_climax_ov = '''    // Ovulation separated from wife climax - triggered exclusively via [O] Ovulate button
    // (func_ovulate removed from func_wife_climax)'''

    if old_climax_ov in code:
        code = code.replace(old_climax_ov, new_climax_ov, 1)
        LOGGER.log("Create_0: Disentangled C from ovulation in func_wife_climax.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_climax_ov")

    if 'working_directory + "/setting_data.sav"' in code:
        code = code.replace('working_directory + "/setting_data.sav"', '"setting_data.sav"')
        LOGGER.log("Create_0: Replaced working_directory path with persistent sandboxed setting_data.sav.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:working_directory_setting_data_sav")

    old_legacy_shaft_0 = gml("patch_create_code/old_legacy_shaft_0")

    new_legacy_shaft_0 = gml("patch_create_code/new_legacy_shaft_0")

    code = guarded_replace(code, old_legacy_shaft_0, new_legacy_shaft_0, "patch_create_code:old_legacy_shaft_0")

    old_legacy_shaft_1 = gml("patch_create_code/old_legacy_shaft_1")

    new_legacy_shaft_1 = gml("patch_create_code/new_legacy_shaft_1")

    code = guarded_replace(code, old_legacy_shaft_1, new_legacy_shaft_1, "patch_create_code:old_legacy_shaft_1")

    old_mod_shaft_0 = gml("patch_create_code/old_mod_shaft_0")

    new_mod_shaft_0 = gml("patch_create_code/new_mod_shaft_0")

    if old_mod_shaft_0 in code:
        code = code.replace(old_mod_shaft_0, new_mod_shaft_0, 1)
        LOGGER.log("Create_0: Safe pill art asset fallback active in func_get_futa_frame.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_mod_shaft_0")

    # Persist continuous_toggle in setting_data.sav
    old_clench_save = 'ini_write_real("features", "custom_clench_toggle", custom_clench_toggle);'
    new_clench_save = '''ini_write_real("features", "custom_clench_toggle", custom_clench_toggle);
    ini_write_real("features", "continuous_toggle", continuous_toggle);'''
    if old_clench_save in code and 'ini_write_real("features", "continuous_toggle"' not in code:
        code = guarded_replace(code, old_clench_save, new_clench_save, "patch_create_code:old_clench_save", count=1)

    old_clench_load = 'custom_clench_toggle = ini_read_real("features", "custom_clench_toggle", 0);'
    new_clench_load = '''custom_clench_toggle = ini_read_real("features", "custom_clench_toggle", 0);
    continuous_toggle = bool(ini_read_real("features", "continuous_toggle", false));'''
    if old_clench_load in code and 'ini_read_real("features", "continuous_toggle"' not in code:
        code = guarded_replace(code, old_clench_load, new_clench_load, "patch_create_code:old_clench_load", count=1)
        LOGGER.log("Create_0: Added continuous_toggle persistence to setting_data.sav.", prefix="[+]")

    old_norm_find = gml("patch_create_code/old_norm_find")
    new_norm_find = gml("patch_create_code/new_norm_find")
    if old_norm_find in code:
        code = code.replace(old_norm_find, new_norm_find, 1)
        LOGGER.log("Create_0: Injected leading slash removal in tc_norm_path for Android asset loading.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_norm_find")

    old_tc_target = gml("patch_create_code/old_tc_target")
    new_tc_target = gml("patch_create_code/new_tc_target")
    if old_tc_target in code:
        code = code.replace(old_tc_target, new_tc_target, 1)
        LOGGER.log("Create_0: Neutralized native file_find_first loops in tc_ff_first to eliminate Android filesystem hangs.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_tc_target")

    old_next_find = gml("patch_create_code/old_next_find")
    new_next_find = gml("patch_create_code/new_next_find")
    if old_next_find in code:
        code = code.replace(old_next_find, new_next_find, 1)
        LOGGER.log("Create_0: Neutralized native file_find_next/close on mobile.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_next_find")

    # 1. Prevent Out-Of-Memory startup crash by skipping upfront thumbnail loading on mobile
    old_legacy_w_load = gml("patch_create_code/old_legacy_w_load")

    new_legacy_w_load = gml("patch_create_code/new_legacy_w_load")

    code = guarded_replace(code, old_legacy_w_load, new_legacy_w_load, "patch_create_code:old_legacy_w_load")

    old_cf_find = gml("patch_create_code/old_cf_find")

    new_cf_find = gml("patch_create_code/new_cf_find")

    if old_cf_find in code:
        code = code.replace(old_cf_find, new_cf_find, 1)
        LOGGER.log("Create_0: Eliminated check_custom_image_size blocking sprite_add startup hang.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_cf_find")

    # -------------------------------------------------------------
    # MOD COMPATIBILITY OVERHAUL: Radio, Voice Packs, Vanilla Dialogues, Texture Packs
    # -------------------------------------------------------------
    old_radio = gml("patch_create_code/old_radio")

    new_radio = gml("patch_create_code/new_radio")
    code = guarded_replace(code, old_radio, new_radio, "patch_create_code:old_radio")

    old_cs = gml("patch_create_code/old_cs")

    new_cs = gml("patch_create_code/new_cs")
    code = guarded_replace(code, old_cs, new_cs, "patch_create_code:old_cs")

    old_gca = gml("patch_create_code/old_gca")

    new_gca = gml("patch_create_code/new_gca")
    code = guarded_replace(code, old_gca, new_gca, "patch_create_code:old_gca")

    old_v_dlg = gml("patch_create_code/old_v_dlg")

    new_v_dlg = gml("patch_create_code/new_v_dlg")
    code = guarded_replace(code, old_v_dlg, new_v_dlg, "patch_create_code:old_v_dlg")

    old_tp_backup = gml("patch_create_code/old_tp_backup")

    new_tp_backup = gml("patch_create_code/new_tp_backup")
    code = guarded_replace(code, old_tp_backup, new_tp_backup, "patch_create_code:old_tp_backup")

    old_tp_replace = gml("patch_create_code/old_tp_replace")

    new_tp_replace = gml("patch_create_code/new_tp_replace")
    code = guarded_replace(code, old_tp_replace, new_tp_replace, "patch_create_code:old_tp_replace")

    old_futa_buf = gml("patch_create_code/old_futa_buf")
    new_futa_buf = gml("patch_create_code/new_futa_buf")
    if old_futa_buf in code:
        code = code.replace(old_futa_buf, new_futa_buf, 1)
        LOGGER.log("Create_0: Injected native text stream manifest reader for custom futas.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_futa_buf")

    old_wife_buf = gml("patch_create_code/old_wife_buf")
    new_wife_buf = gml("patch_create_code/new_wife_buf")
    if old_wife_buf in code:
        code = code.replace(old_wife_buf, new_wife_buf, 1)
        LOGGER.log("Create_0: Injected native text stream manifest reader for custom wives.", prefix="[+]")

        # Character Loader Fortification: Guarantee non-negative, valid sprites for custom lovers and wives
    else:
        PATCH_MISSES.append("patch_create_code:old_wife_buf")
    old_apply_futa = gml("patch_create_code/old_apply_futa")

    new_apply_futa = gml("patch_create_code/new_apply_futa")
    code = guarded_replace(code, old_apply_futa, new_apply_futa, "patch_create_code:old_apply_futa")

    old_apply_wife = '''    wife_bangs_sprite = custom_wife_portrait;
    wife_hair_sprite = custom_wife_mating_press;'''

    new_apply_wife = gml("patch_create_code/new_apply_wife")
    code = guarded_replace(code, old_apply_wife, new_apply_wife, "patch_create_code:old_apply_wife")

    old_get_port = gml("patch_create_code/old_get_port")

    new_get_port = gml("patch_create_code/new_get_port")
    code = guarded_replace(code, old_get_port, new_get_port, "patch_create_code:old_get_port")

    old_get_boobs = gml("patch_create_code/old_get_boobs")

    new_get_boobs = gml("patch_create_code/new_get_boobs")
    code = guarded_replace(code, old_get_boobs, new_get_boobs, "patch_create_code:old_get_boobs")

    old_cis = gml("patch_create_code/old_cis")

    new_cis = gml("patch_create_code/new_cis")

    code = guarded_replace(code, old_cis, new_cis, "patch_create_code:old_cis")

    # 2. Universal Modroom & Legacy Wife character support (checks both naming schemes)
    old_check_w = gml("patch_create_code/old_check_w")

    new_check_w = gml("patch_create_code/new_check_w")

    if old_check_w in code:
        code = code.replace(old_check_w, new_check_w, 1)
        LOGGER.log("Create_0: Enabled universal Modroom & Legacy format detection in check_custom_wife.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_check_w")

    old_lcw = gml("patch_create_code/old_lcw")
    new_lcw = gml("patch_create_code/new_lcw")
    if old_lcw in code:
        code = code.replace(old_lcw, new_lcw, 1)
        LOGGER.log("Create_0: Universal Legacy Spouse Detection in func_load_custom_wife enabled.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_lcw")

    # 3. Guard livestream JSON parsing against malformed JSON syntax crashes
    old_ls_json = '''    file_text_close(_ls_file);
    livestream_dialogue = json_parse(_ls_json_string);'''

    new_ls_json = gml("patch_create_code/new_ls_json")

    code = guarded_replace(code, old_ls_json, new_ls_json, "patch_create_code:old_ls_json")

        # 4. Instant In-Memory Manifest Indexing on Mobile (Eliminates 13,000+ synchronous file_exists JNI calls)
    old_futa_loop = gml("patch_create_code/old_futa_loop")

    new_futa_loop = gml("patch_create_code/new_futa_loop")

    code = guarded_replace(code, old_futa_loop, new_futa_loop, "patch_create_code:old_futa_loop")

    old_wife_loop = gml("patch_create_code/old_wife_loop")

    new_wife_loop = gml("patch_create_code/new_wife_loop")

    code = guarded_replace(code, old_wife_loop, new_wife_loop, "patch_create_code:old_wife_loop")

    # 5. Bypass recursive phone_mods BFS directory scanning on launch
    old_pm_scan = gml("patch_create_code/old_pm_scan")

    new_pm_scan = gml("patch_create_code/new_pm_scan")

    if old_pm_scan in code:
        code = code.replace(old_pm_scan, new_pm_scan, 1)
        LOGGER.log("Create_0: Injected instant manifest indexing and bypassed ANR startup hangs.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_pm_scan")

    # Standardize custom wife/partner xray origins & resizers against base models (160x168, origin 80, 84)
    old_legacy_xray_read = '''        xray_origin_x = ini_read_real("xray", "origin_x", sprite_origin_x);
        xray_origin_y = ini_read_real("xray", "origin_y", sprite_origin_y);'''
    new_legacy_xray_read = gml("patch_create_code/new_legacy_xray_read")
    code = guarded_replace(code, old_legacy_xray_read, new_legacy_xray_read, "patch_create_code:old_legacy_xray_read")

    old_legacy_xray_add = 'legacy_custom_wife_xray = sprite_add(f_xray, 4, false, false, xray_origin_x, xray_origin_y);'
    new_legacy_xray_add = gml("patch_create_code/new_legacy_xray_add")
    code = guarded_replace(code, old_legacy_xray_add, new_legacy_xray_add, "patch_create_code:old_legacy_xray_add")

    old_custom_wife_xray = 'custom_wife_xray = sprite_add(file_check, 3, false, false, sprite_origin_x, sprite_origin_y);'
    new_custom_wife_xray = gml("patch_create_code/new_custom_wife_xray")
    code = guarded_replace(code, old_custom_wife_xray, new_custom_wife_xray, "patch_create_code:old_custom_wife_xray")

    # Partner (Futa) X-ray resizer & origin scaling
    old_partner_xray_add = 'custom_xray = sprite_add(f_xray, 18, false, false, 80, (custom_xray_offset_y > 0) ? (84 - custom_xray_offset_y) : (84 + custom_xray_offset_y));'
    new_partner_xray_add = gml("patch_create_code/new_partner_xray_add")
    code = guarded_replace(code, old_partner_xray_add, new_partner_xray_add, "patch_create_code:old_partner_xray_add")

    old_legacy_futa_xray_add = 'legacy_custom_xray = sprite_add(f_xray, 3, false, false, 80, 84);'
    new_legacy_futa_xray_add = gml("patch_create_code/new_legacy_futa_xray_add")
    code = guarded_replace(code, old_legacy_futa_xray_add, new_legacy_futa_xray_add, "patch_create_code:old_legacy_futa_xray_add")
    old_wr = "else if (custom_wife_sprite_loaded == true && irandom(4) == 0)"
    new_wr = "else if (custom_wife_sprite_loaded == true && irandom(4) == 0 && title == false)"
    if old_wr in code:
        code = code.replace(old_wr, new_wr, 1)
        LOGGER.log("Create_0: Added title == false guard to custom wife randomizer on startup.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_wr")

    old_fb = gml("patch_create_code/old_fb")
    new_fb = gml("patch_create_code/new_fb")
    if old_fb in code:
        code = code.replace(old_fb, new_fb, 1)
        LOGGER.log("Create_0: Fortified func_wife_portrait_body with legacy spouse support and non-negative sprite guarantees.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_create_code:old_fb")

    old_facfs = gml("patch_create_code/old_facfs")
    new_facfs = gml("patch_create_code/new_facfs")
    code = guarded_replace(code, old_facfs, new_facfs, "patch_create_code:old_facfs", optional=True)

    # In func_get_portrait, ensure non-negative return for legacy_custom_mating_press
    old_fgp_case = gml("patch_create_code/old_fgp_case")
    new_fgp_case = gml("patch_create_code/new_fgp_case")
    code = guarded_replace(code, old_fgp_case, new_fgp_case, "patch_create_code:old_fgp_case")

    # In func_load_custom_futa, dynamic frame count fallback for legacy_custom_portrait
    old_flcf_port = gml("patch_create_code/old_flcf_port")

    new_flcf_port = gml("patch_create_code/new_flcf_port")
    code = guarded_replace(code, old_flcf_port, new_flcf_port, "patch_create_code:old_flcf_port")

    old_fgpb_ret = gml("patch_create_code/old_fgpb_ret")
    new_fgpb_ret = gml("patch_create_code/new_fgpb_ret")
    code = guarded_replace(code, old_fgpb_ret, new_fgpb_ret, "patch_create_code:old_fgpb_ret")

    # Universal Futa Detection and Direct Native Loaders (removes file_exists APK blockers)
    old_flcf_header = gml("patch_create_code/old_flcf_header")

    new_flcf_header = gml("patch_create_code/new_flcf_header")

    code = guarded_replace(code, old_flcf_header, new_flcf_header, "patch_create_code:old_flcf_header")

    old_f_mate_block = gml("patch_create_code/old_f_mate_block")

    new_f_mate_block = gml("patch_create_code/new_f_mate_block")

    code = guarded_replace(code, old_f_mate_block, new_f_mate_block, "patch_create_code:old_f_mate_block")

    old_f_condom_block = gml("patch_create_code/old_f_condom_block")

    new_f_condom_block = gml("patch_create_code/new_f_condom_block")

    code = guarded_replace(code, old_f_condom_block, new_f_condom_block, "patch_create_code:old_f_condom_block")

    old_spouse_load = gml("patch_create_code/old_spouse_load")
    new_spouse_load = gml("patch_create_code/new_spouse_load")
    code = guarded_replace(code, old_spouse_load, new_spouse_load, "patch_create_code:old_spouse_load")

    # Safe sprite_delete protection: NEVER delete built-in game assets (<= 189)
    old_port_del = gml("patch_create_code/old_port_del")
    new_port_del = gml("patch_create_code/new_port_del")
    code = guarded_replace(code, old_port_del, new_port_del, "patch_create_code:old_port_del", count=-1)

    old_wport_del = gml("patch_create_code/old_wport_del")
    new_wport_del = gml("patch_create_code/new_wport_del")
    code = guarded_replace(code, old_wport_del, new_wport_del, "patch_create_code:old_wport_del", count=-1)

    # Universal Futa detection and direct loader
    old_futa_hdr = gml("patch_create_code/old_futa_hdr")
    new_futa_hdr = gml("patch_create_code/new_futa_hdr")
    code = guarded_replace(code, old_futa_hdr, new_futa_hdr, "patch_create_code:old_futa_hdr", optional=True)


    # Initialize Favorites Maps in Create_0 cleanly without freezing
    favs_init_code = gml("patch_create_code/favs_init_code")
    code = code + favs_init_code

    old_bf = gml("patch_create_code/old_bf")
    new_bf = gml("patch_create_code/new_bf")
    code = guarded_replace(code, old_bf, new_bf, "patch_create_code:old_bf")

    old_bf_ret = gml("patch_create_code/old_bf_ret")

    new_bf_ret = gml("patch_create_code/new_bf_ret")
    code = guarded_replace(code, old_bf_ret, new_bf_ret, "patch_create_code:old_bf_ret")

    old_clf = gml("patch_create_code/old_clf")
    new_clf = gml("patch_create_code/new_clf")
    if old_clf in code: code = code.replace(old_clf, new_clf, 1)
    else:
        PATCH_MISSES.append("patch_create_code:old_clf")

    old_clw = gml("patch_create_code/old_clw")
    new_clw = gml("patch_create_code/new_clw")
    if old_clw in code: code = code.replace(old_clw, new_clw, 1)
    else:
        PATCH_MISSES.append("patch_create_code:old_clw")

    old_ret_boobs = gml("patch_create_code/old_ret_boobs")
    new_ret_boobs = gml("patch_create_code/new_ret_boobs")
    if old_ret_boobs in code: code = code.replace(old_ret_boobs, new_ret_boobs, 1)
    else:
        PATCH_MISSES.append("patch_create_code:old_ret_boobs")


    if enable_toy_telemetry:
        bp_create = gml("patch_create_code/bp_create")
        code = code + bp_create
        LOGGER.log("Create_0: Enabled ToyBridge UDP toy telemetry socket on port 45735.", prefix="[+]")

    # Initialize xray_origin_x and xray_origin_y in func_load_custom_spouse to prevent unset variable crash
    code = guarded_replace(code, '    var xray_origin_x, xray_origin_y;', '    var xray_origin_x = 80;\n    var xray_origin_y = 84;', "patch_create_code:var_xray_origin_x_xray_origin_y", count=1)
    code = guarded_replace(code, 'if (file_exists(string(arg0) + "/custom_data.spouse"))', 'if (file_exists(string(arg0) + "/custom_data.spouse") || file_exists(string(arg0) + "/custom_data.wife") || (os_type == os_android || os_type == os_ios))', "patch_create_code:if_file_exists_string_arg0_custom_data_s", count=1)

    LOGGER.log("Create_0: Standardized all partner & spouse xray assets to base reference (160x168, 80, 84).", prefix="[+]")

    return code


def patch_step_code(code):
    """Patches Step_0 to enable gameplay hovers/touch inputs while panels are open and remove Rickroll."""
    old_step_hovers = gml("patch_step_code/old_step_hovers")

    new_step_hovers = gml("patch_step_code/new_step_hovers")

    code = guarded_replace(code, old_step_hovers, new_step_hovers, "patch_step_code:old_step_hovers")

    old_step_headpat = 'if (title == false && start_timer < 1 && futa_selector_open == false && newlover_menu_toggle == false && newwife_menu_toggle == false)'
    new_step_headpat = 'if (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)'

    if old_step_headpat in code:
        code = code.replace(old_step_headpat, new_step_headpat, 1)
        LOGGER.log("Step_0: Enabled all touch inputs and hovers with open panels.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_step_code:old_step_headpat")

    pattern = r'if\s*\(\s*variable_global_exists\("rg_chosen_pill"\)\s*&&\s*global\.rg_chosen_pill\s*==\s*"Rick_Astley"\s*\)\s*\{.*?\n\}'
    if re.search(pattern, code, flags=re.DOTALL):
        code = re.sub(pattern, '// Rickroll easter egg neutralized by patcher', code, flags=re.DOTALL)
        LOGGER.log("Step_0: Neutralized Rickroll fake crash.", prefix="[+]")

    return code


def apply_hyper_sizes(code: str) -> str:
    """Optionally adds HYPER: ON/OFF toggle to SIZES options page (ToyBridge 1.5.2)."""
    hyper_anchor = 'comment = "lover sizes";'
    hyper_toggle = gml("apply_hyper_sizes/hyper_toggle")
    if hyper_anchor in code and "_tc_hx" not in code:
        code = guarded_replace(code, hyper_anchor, hyper_anchor + "\n" + hyper_toggle, "apply_hyper_sizes:hyper_anchor", count=1)
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

    code = guarded_replace(code, "if (manual_mode == 0 && mouse_check_button_pressed(mb_right) && !hover_portrait && !boob_box && title == false)", "if (manual_mode == 0 && mouse_check_button_pressed(mb_right) && !hover_portrait && (!variable_instance_exists(id, \"boob_box\") || !boob_box) && title == false)", "patch_draw_code:if_manual_mode_0_mouse_check_button_pres", count=-1)
    code = guarded_replace(code, "else if (mouse_check_button_pressed(mb_right) && !hover_portrait && !boob_box && manual_mode == 0)", "else if (mouse_check_button_pressed(mb_right) && !hover_portrait && (!variable_instance_exists(id, \"boob_box\") || !boob_box) && manual_mode == 0)", "patch_draw_code:else_if_mouse_check_button_pressed_mb_ri", count=-1)

    old_mob_init = gml("patch_draw_code/old_mob_init")

    new_mob_init = gml("patch_draw_code/new_mob_init")

    if old_mob_init in code:
        code = code.replace(old_mob_init, new_mob_init, 1)
        LOGGER.log("Draw_0: Injected screen wake-lock, auto-save, and manual mode right-side menus exit check.", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_draw_code:old_mob_init")

    if "options_page = qi; func_save_settings();" not in code:
        code = guarded_replace(code, "options_page = qi;", "options_page = qi; func_save_settings();", "patch_draw_code:options_page_qi", count=-1)
        code = guarded_replace(code, "options_page = _next_page;", "options_page = _next_page; func_save_settings();", "patch_draw_code:options_page_next_page", count=-1)

    if "continuous_toggle = !continuous_toggle; func_save_settings();" not in code:
        code = guarded_replace(code, "continuous_toggle = !continuous_toggle;", "continuous_toggle = !continuous_toggle; func_save_settings();", "patch_draw_code:continuous_toggle_continuous_toggle", count=-1)

    # Standardize runtime anatomy_sprite and xray_sprite resizers against base reference
    old_anat = "var anatomy_sprite = (wife_xray == -1) ? xray_sprite : wife_xray;"
    new_anat = gml("patch_draw_code/new_anat")
    if old_anat in code and "sprite_get_xoffset(anatomy_sprite)" not in code:
        code = guarded_replace(code, old_anat, new_anat, "patch_draw_code:old_anat", count=1)
        LOGGER.log("Draw_0: Standardized runtime anatomy and partner xray resizers to base (80, 84).", prefix="[+]")

    # Crash Prevention: Guards for custom_portrait draws (cures requested -1 crash)
    old_cp_boobs = gml("patch_draw_code/old_cp_boobs")
    new_cp_boobs = gml("patch_draw_code/new_cp_boobs")
    code = guarded_replace(code, old_cp_boobs, new_cp_boobs, "patch_draw_code:old_cp_boobs")

    old_cp_blush = gml("patch_draw_code/old_cp_blush")
    new_cp_blush = gml("patch_draw_code/new_cp_blush")
    code = guarded_replace(code, old_cp_blush, new_cp_blush, "patch_draw_code:old_cp_blush")

    old_cp_mouth = gml("patch_draw_code/old_cp_mouth")
    new_cp_mouth = gml("patch_draw_code/new_cp_mouth")
    code = guarded_replace(code, old_cp_mouth, new_cp_mouth, "patch_draw_code:old_cp_mouth")

    old_cp_eye = 'draw_sprite_ext(custom_portrait, 7 + eye_id, eye_x, eye_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, c_white, 1);'
    new_cp_eye = 'if (sprite_exists(custom_portrait) && custom_portrait != -1) draw_sprite_ext(custom_portrait, 7 + eye_id, eye_x, eye_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, c_white, 1);'
    code = guarded_replace(code, old_cp_eye, new_cp_eye, "patch_draw_code:old_cp_eye")
    old_lcp_boobs = gml("patch_draw_code/old_lcp_boobs")
    new_lcp_boobs = gml("patch_draw_code/new_lcp_boobs")
    code = guarded_replace(code, old_lcp_boobs, new_lcp_boobs, "patch_draw_code:old_lcp_boobs")

    old_lcp_mouth = gml("patch_draw_code/old_lcp_mouth")
    new_lcp_mouth = gml("patch_draw_code/new_lcp_mouth")
    code = guarded_replace(code, old_lcp_mouth, new_lcp_mouth, "patch_draw_code:old_lcp_mouth")

    old_lcp_eyes = gml("patch_draw_code/old_lcp_eyes")
    new_lcp_eyes = gml("patch_draw_code/new_lcp_eyes")
    code = guarded_replace(code, old_lcp_eyes, new_lcp_eyes, "patch_draw_code:old_lcp_eyes")

        # Extra sprite existence guards for legacy_custom_portrait and bangs_sprite
    old_lcp_boob2 = gml("patch_draw_code/old_lcp_boob2")
    new_lcp_boob2 = gml("patch_draw_code/new_lcp_boob2")
    code = guarded_replace(code, old_lcp_boob2, new_lcp_boob2, "patch_draw_code:old_lcp_boob2")

    old_lcp_mouth2 = gml("patch_draw_code/old_lcp_mouth2")
    new_lcp_mouth2 = gml("patch_draw_code/new_lcp_mouth2")
    code = guarded_replace(code, old_lcp_mouth2, new_lcp_mouth2, "patch_draw_code:old_lcp_mouth2")

    # Safe point-of-use guards for bangs and custom portraits in Draw_0
    old_bs_6_raw = """    comment = "layer 6: side bangs";
    draw_sprite_ext(bangs_sprite, 6, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);"""
    new_bs_6_guard = gml("patch_draw_code/new_bs_6_guard")
    code = guarded_replace(code, old_bs_6_raw, new_bs_6_guard, "patch_draw_code:old_bs_6_raw")

    old_bs_13_raw = """    comment = "layer 13: fore bangs (mapped to vanilla index 9)";
    draw_sprite_ext(bangs_sprite, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 13 : 9, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);"""
    new_bs_13_guard = gml("patch_draw_code/new_bs_13_guard")
    code = guarded_replace(code, old_bs_13_raw, new_bs_13_guard, "patch_draw_code:old_bs_13_raw")

    old_lpe = gml("patch_draw_code/old_lpe")
    new_lpe = gml("patch_draw_code/new_lpe")
    code = guarded_replace(code, old_lpe, new_lpe, "patch_draw_code:old_lpe")

    # Safe fallbacks for boobs, face, mouth, bangs in Lover portrait
    code = guarded_replace(code, "draw_sprite_ext(func_get_portrait_boobs(top_sprite, 0), 2, portrait_x, _boob_y, _boob_xscale, _boob_yscale, 0, top_skin, 1);", "var _lb_boob = func_get_portrait_boobs(top_sprite, 0); if (!sprite_exists(_lb_boob) || _lb_boob == -1) _lb_boob = _lover_base_portrait; draw_sprite_ext(_lb_boob, 2, portrait_x, _boob_y, _boob_xscale, _boob_yscale, 0, top_skin, 1);", "patch_draw_code:draw_sprite_ext_func_get_portrait_boobs_", count=-1)
    code = guarded_replace(code, "draw_sprite_ext(func_get_portrait(top_sprite, 0), 3, portrait_x, portrait_y + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);", "draw_sprite_ext(_lover_base_portrait, 3, portrait_x, portrait_y + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);", "patch_draw_code:draw_sprite_ext_func_get_portrait_top_sp", count=-1)
    code = guarded_replace(code, "draw_sprite_ext(func_get_portrait(top_sprite, 0), (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 12 : 8,", "draw_sprite_ext(_lover_base_portrait, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 12 : 8,", "patch_draw_code:draw_sprite_ext_func_get_portrait_top_sp_2", count=-1)

    # Fix all c_sprite and dt_c_sprite assignments without string collision
    code = guarded_replace(code, "dt_c_sprite = legacy_custom_condom;", "if (sprite_exists(legacy_custom_condom) && legacy_custom_condom != -1) dt_c_sprite = legacy_custom_condom;", "patch_draw_code:dt_c_sprite_legacy_custom_condom", count=-1)
    code = guarded_replace(code, " c_sprite = legacy_custom_condom;", " if (sprite_exists(legacy_custom_condom) && legacy_custom_condom != -1) c_sprite = legacy_custom_condom;", "patch_draw_code:c_sprite_legacy_custom_condom", count=-1)
    code = guarded_replace(code, "draw_sprite_ext(legacy_xray_sprite", "var _lx = (sprite_exists(legacy_xray_sprite) && legacy_xray_sprite != -1) ? legacy_xray_sprite : sFutaXray; draw_sprite_ext(_lx", "patch_draw_code:draw_sprite_ext_legacy_xray_sprite", count=-1)

    # Safety before drawing condoms in mating press (around line 1770)
    code = guarded_replace(code, "draw_sprite_ext(c_sprite, p_condom,", "if (!sprite_exists(c_sprite) || c_sprite == -1) c_sprite = sFutaCondom; draw_sprite_ext(c_sprite, p_condom,", "patch_draw_code:draw_sprite_ext_c_sprite_p_condom", count=-1)
    code = guarded_replace(code, "draw_sprite_ext(c_sprite, p_broken,", "if (!sprite_exists(c_sprite) || c_sprite == -1) c_sprite = sFutaCondom; draw_sprite_ext(c_sprite, p_broken,", "patch_draw_code:draw_sprite_ext_c_sprite_p_broken", count=-1)

    LOGGER.log("Draw_0: Injected sprite existence guards on custom_portrait draws (cures requested -1 crash).", prefix="[+]")

    # Unlock ALL 8 gameplay mechanics with open panels
    code = guarded_replace(code, "if (futa_selector_open == true || newlover_menu_toggle == true || newwife_menu_toggle == true || radio_toggle == true || futa_selector_close_timer > 0)\n{\n    penis_grab = false;\n}", "if (futa_selector_open == true || radio_toggle == true || futa_selector_close_timer > 0)\n{\n    penis_grab = false;\n}", "patch_draw_code:if_futa_selector_open_true_newlover_menu", count=-1)

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
        code = guarded_replace(code, old_t, new_t, "patch_draw_code:old_t")

    LOGGER.log("Draw_0: Unlocked ALL 8 gameplay mechanics to work continuously while UI panels are open.", prefix="[+]")

    # Hitboxes & accessibility for New Lover and New Wife
    old_nl_cond = "if (insert == false && orgasm == false && newwife_menu_toggle == false && title == false && start_timer < 1 && (manual_mode == 0 || radial_manual_ui_mode == true || radial_panel_from_radial == true))"
    new_nl_cond = "if (title == false && start_timer < 1)"
    code = guarded_replace(code, old_nl_cond, new_nl_cond, "patch_draw_code:old_nl_cond")


    old_nl_btn = '''    button_newlover_press = point_in_rectangle(mouse_x, mouse_y, portrait_x - 35, portrait_y + 52, portrait_x + 35, portrait_y + 69);'''
    new_nl_btn = gml("patch_draw_code/new_nl_btn")

    code = guarded_replace(code, old_nl_btn, new_nl_btn, "patch_draw_code:old_nl_btn")

    old_nl_open_block = gml("patch_draw_code/old_nl_open_block")

    new_nl_open_block = gml("patch_draw_code/new_nl_open_block")

    code = guarded_replace(code, old_nl_open_block, new_nl_open_block, "patch_draw_code:old_nl_open_block")

    # Fluid boundary clamping and dragging for New Lover panel
    old_nl_drag = gml("patch_draw_code/old_nl_drag")

    new_nl_drag = gml("patch_draw_code/new_nl_drag")

    code = guarded_replace(code, old_nl_drag, new_nl_drag, "patch_draw_code:old_nl_drag")

    target_nl_title = 'draw_text_transformed(menu_cx, menu_start_y + menu_pad, "LOVER", 0.65, 0.65, 0);'
    new_nl_title = gml("patch_draw_code/new_nl_title")
    if target_nl_title in code and "_close_nl_hover ? make_color_rgb" not in code:
        code = guarded_replace(code, target_nl_title, new_nl_title, "patch_draw_code:target_nl_title", count=1)

    # Fluid boundary clamping and dragging for New Wife panel
    old_nw_drag = gml("patch_draw_code/old_nw_drag")

    new_nw_drag = gml("patch_draw_code/new_nw_drag")

    code = guarded_replace(code, old_nw_drag, new_nw_drag, "patch_draw_code:old_nw_drag")

    target_nw_title = 'draw_text_transformed(menu_cx, menu_start_y + menu_pad, "WIFE", 0.65, 0.65, 0);'
    new_nw_title = gml("patch_draw_code/new_nw_title")
    if target_nw_title in code and "_close_nw_hover ? make_color_rgb" not in code:
        code = guarded_replace(code, target_nw_title, new_nw_title, "patch_draw_code:target_nw_title", count=1)

    old_nl_outside = "if (mouse_check_button_pressed(mb_left) && !menu_bounds && !newlover_dragging && !mm_press5 && !in_action_menu)"
    new_nl_outside = "// Outside-click auto-close removed: menus remain open independently\n        if (false)"
    code = guarded_replace(code, old_nl_outside, new_nl_outside, "patch_draw_code:old_nl_outside")

    old_nw_line_14135 = gml("patch_draw_code/old_nw_line_14135")
    new_nw_line_14135 = gml("patch_draw_code/new_nw_line_14135")
    code = guarded_replace(code, old_nw_line_14135, new_nw_line_14135, "patch_draw_code:old_nw_line_14135")

    old_nw_btn = "mm_press4 = point_in_rectangle(mouse_x, mouse_y, mm_x4 - 6, mm_y4 - 6, mm_x4 + 5, mm_y4 + 5);"
    new_nw_btn = gml("patch_draw_code/new_nw_btn")
    code = guarded_replace(code, old_nw_btn, new_nw_btn, "patch_draw_code:old_nw_btn")

    old_nw_click = "if (mm_press4 == true && mouse_check_button_pressed(mb_left) && title == false)"
    new_nw_click = "if (!futa_selector_open && !mob_expanded && ((_mouse_hit_nw && mouse_check_button_pressed(mb_left)) || _mob_touch_nw)) if (title == false)"
    code = guarded_replace(code, old_nw_click, new_nw_click, "patch_draw_code:old_nw_click")

    old_nw_draw = "if (newlover_menu_toggle == false && button_newlover_press == false && orgasm == false && title == false && start_timer < 1)"
    new_nw_draw = "if (title == false && start_timer < 1)"
    code = guarded_replace(code, old_nw_draw, new_nw_draw, "patch_draw_code:old_nw_draw")

    old_nw_menu = "if (newwife_menu_toggle == true && orgasm == false && button_newlover_press == false)"
    new_nw_menu = "if (newwife_menu_toggle == true && orgasm == false)"
    code = guarded_replace(code, old_nw_menu, new_nw_menu, "patch_draw_code:old_nw_menu")

    old_nw_outside = "if (mouse_check_button_pressed(mb_left) && !menu_bounds_w && !newwife_dragging && !mm_press4 && !mm_press5 && !in_action_menu)"
    new_nw_outside = "// Outside-click auto-close removed: menus remain open independently\n        if (false)"
    code = guarded_replace(code, old_nw_outside, new_nw_outside, "patch_draw_code:old_nw_outside")

    old_act_btn = "if (newlover_menu_toggle == false && button_newlover_press == false && newwife_menu_toggle == false && orgasm == false)"
    new_act_btn = "if (orgasm == false && title == false)"
    code = guarded_replace(code, old_act_btn, new_act_btn, "patch_draw_code:old_act_btn")

    code = guarded_replace(code, "if (mouse_check_button_pressed(mb_right) || keyboard_check_pressed(vk_escape))\n        {\n            newlover_menu_toggle = false;", "if (keyboard_check_pressed(vk_escape))\n        {\n            newlover_menu_toggle = false;", "patch_draw_code:if_mouse_check_button_pressed_mb_right_k", count=-1)
    code = guarded_replace(code, "if (mouse_check_button_pressed(mb_right) || keyboard_check_pressed(vk_escape))\n        {\n            newwife_menu_toggle = false;", "if (keyboard_check_pressed(vk_escape))\n        {\n            newwife_menu_toggle = false;", "patch_draw_code:if_mouse_check_button_pressed_mb_right_k_2", count=-1)

    code = guarded_replace(code, "newlover_menu_toggle = true;\n            newwife_menu_toggle = false;\n            radial_panel_from_radial = true;", "newlover_menu_toggle = true;\n            radial_panel_from_radial = true;", "patch_draw_code:newlover_menu_toggle_true_newwife_menu_t", count=-1)
    code = guarded_replace(code, "newwife_menu_toggle = true;\n            newlover_menu_toggle = false;\n            radial_panel_from_radial = true;", "newwife_menu_toggle = true;\n            radial_panel_from_radial = true;", "patch_draw_code:newwife_menu_toggle_true_newlover_menu_t", count=-1)
    code = guarded_replace(code, "else if (newlover_menu_toggle == true || newwife_menu_toggle == true)\n    {\n        newlover_menu_toggle = false;\n        newwife_menu_toggle = false;\n    }", "// keep simultaneous menus open", "patch_draw_code:else_if_newlover_menu_toggle_true_newwif", count=-1)

    code = guarded_replace(code, "if (top_sprite == custom_mating_press)\n    {\n        penis_sprite = custom_mating_press;\n    }", "if (custom_lover_toggle == true || top_sprite == custom_mating_press || top_sprite == legacy_custom_mating_press)\n    {\n        penis_sprite = top_sprite;\n    }", "patch_draw_code:if_top_sprite_custom_mating_press_penis_", count=-1)

    old_menu_trans = gml("patch_draw_code/old_menu_trans")

    new_menu_trans = gml("patch_draw_code/new_menu_trans")

    if old_menu_trans in code:
        code = code.replace(old_menu_trans, new_menu_trans, 1)
        LOGGER.log("Draw_0: Title screen warning set to display ONCE only on startup (fixes peek mode).", prefix="[+]")
    else:
        PATCH_MISSES.append("patch_draw_code:old_menu_trans")

    old_hitbox_vis = gml("patch_draw_code/old_hitbox_vis")

    new_hitbox_vis = gml("patch_draw_code/new_hitbox_vis")

    code = guarded_replace(code, old_hitbox_vis, new_hitbox_vis, "patch_draw_code:old_hitbox_vis")

    code = inject_virtual_keyboard_and_search(code)
    code = inject_lazy_thumbnails_into_draw(code)
    code = enforce_strict_custom_selection(code)

    old_skip = gml("patch_draw_code/old_skip")
    code = guarded_replace(code, old_skip, '// Skip option removed by patcher', "patch_draw_code:old_skip")

    code = inject_complete_overlay(code)


    if enable_toy_telemetry:
        bp_draw = gml("patch_draw_code/bp_draw")
        code = code + bp_draw
        LOGGER.log("Draw_0: Enabled ToyBridge UDP thrust broadcast telemetry.", prefix="[+]")

    return code


def inject_virtual_keyboard_and_search(code):
    """Injects virtual keyboard on search focus, prioritized favorites filter button, and card badges."""
    if "_sel_jump_done" in code and "FAV: ALL" in code:
        return code
    # Header: [FAV: ALL/ON] on Left with absolute priority, Search Bar on Right
    old_search_focus = gml("inject_virtual_keyboard_and_search/old_search_focus")

    new_search_focus = gml("inject_virtual_keyboard_and_search/new_search_focus")

    code = guarded_replace(code, old_search_focus, new_search_focus, "inject_virtual_keyboard_and_search:old_search_focus")

    old_max_scroll_def = "var _max_scroll = max(0, _total_content_w - room_width);"
    new_max_scroll_def = gml("inject_virtual_keyboard_and_search/new_max_scroll_def")

    if old_max_scroll_def in code and "_sel_jump_done" not in code:
        code = guarded_replace(code, old_max_scroll_def, new_max_scroll_def, "inject_virtual_keyboard_and_search:old_max_scroll_def", count=1)

    code = guarded_replace(code, "futa_selector_open = false;", "futa_selector_open = false; _sel_jump_done = false; selector_favs_only = false;", "inject_virtual_keyboard_and_search:futa_selector_open_false", count=-1)

    target_border_draw = "draw_set_color(_border_col);\n            draw_rectangle(_cx - 2, _cy - 2, _cx + _cell_w + 2, _cy + _cell_h + 2, true);"
    new_border_draw = gml("inject_virtual_keyboard_and_search/new_border_draw")

    if target_border_draw in code and "_is_equipped" not in code:
        code = guarded_replace(code, target_border_draw, new_border_draw, "inject_virtual_keyboard_and_search:target_border_draw", count=1)

    return code


def inject_lazy_thumbnails_into_draw(code):
    """Injects or enhances on-demand thumbnail loader with dynamic frame count fallback."""
    old_loader = gml("inject_lazy_thumbnails_into_draw/old_loader")
    new_loader = gml("inject_lazy_thumbnails_into_draw/new_loader")
    if old_loader in code:
        code = code.replace(old_loader, new_loader, 1)
        # Guard c_sprite and custom_lover_toggle execution in Draw_0
    else:
        PATCH_MISSES.append("inject_lazy_thumbnails_into_draw:old_loader")
    old_c_spr = gml("inject_lazy_thumbnails_into_draw/old_c_spr")

    new_c_spr = gml("inject_lazy_thumbnails_into_draw/new_c_spr")

    code = guarded_replace(code, old_c_spr, new_c_spr, "inject_lazy_thumbnails_into_draw:old_c_spr")





    old_cw_toggle = gml("inject_lazy_thumbnails_into_draw/old_cw_toggle")
    new_cw_toggle = gml("inject_lazy_thumbnails_into_draw/new_cw_toggle")
    code = guarded_replace(code, old_cw_toggle, new_cw_toggle, "inject_lazy_thumbnails_into_draw:old_cw_toggle")





    # Fortify grid selector clicks for custom futas and custom wives
    old_futa_click = gml("inject_lazy_thumbnails_into_draw/old_futa_click")
    new_futa_click = gml("inject_lazy_thumbnails_into_draw/new_futa_click")
    if old_futa_click in code: code = code.replace(old_futa_click, new_futa_click, 1)
    else:
        PATCH_MISSES.append("inject_lazy_thumbnails_into_draw:old_futa_click")

    old_wife_click = gml("inject_lazy_thumbnails_into_draw/old_wife_click")
    new_wife_click = gml("inject_lazy_thumbnails_into_draw/new_wife_click")
    if old_wife_click in code: code = code.replace(old_wife_click, new_wife_click, 1)
    else:
        PATCH_MISSES.append("inject_lazy_thumbnails_into_draw:old_wife_click")

    old_w_scale_def = gml("inject_lazy_thumbnails_into_draw/old_w_scale_def")
    new_w_scale_def = gml("inject_lazy_thumbnails_into_draw/new_w_scale_def")
    code = guarded_replace(code, old_w_scale_def, new_w_scale_def, "inject_lazy_thumbnails_into_draw:old_w_scale_def")

    # Favorites / Bookmarks UI and filter logic in Draw_0
    old_sd = gml("inject_lazy_thumbnails_into_draw/old_sd")

    new_sd = gml("inject_lazy_thumbnails_into_draw/new_sd")
    if old_sd in code: code = code.replace(old_sd, new_sd, 1)
    else:
        PATCH_MISSES.append("inject_lazy_thumbnails_into_draw:old_sd")

    old_ci_top = gml("inject_lazy_thumbnails_into_draw/old_ci_top")
    new_ci_top = gml("inject_lazy_thumbnails_into_draw/new_ci_top")
    if old_ci_top in code: code = code.replace(old_ci_top, new_ci_top, 1)
    else:
        PATCH_MISSES.append("inject_lazy_thumbnails_into_draw:old_ci_top")

    old_draw_cell_end = """            comment = "hover detection — highlight and record name";"""
    new_draw_cell_end = gml("inject_lazy_thumbnails_into_draw/new_draw_cell_end")
    if old_draw_cell_end in code: code = code.replace(old_draw_cell_end, new_draw_cell_end, 1)
    else:
        PATCH_MISSES.append("inject_lazy_thumbnails_into_draw:old_draw_cell_end")

    old_cc = 'if (mouse_check_button_pressed(mb_left) && !title && futa_selector_open_timer <= 0)'
    new_cc = 'if ((mouse_check_button_pressed(mb_left) || device_mouse_check_button_pressed(0, mb_left)) && !title && futa_selector_open_timer <= 0 && !_star_hover)'
    code = guarded_replace(code, old_cc, new_cc, "inject_lazy_thumbnails_into_draw:old_cc")

    old_fab_txt = 'draw_text((_fab_x1 + _fab_x2) * 0.5, (_fab_y1 + _fab_y2) * 0.5, mob_expanded ? "✕" : "≡");'
    new_fab_txt = gml("inject_lazy_thumbnails_into_draw/new_fab_txt")
    code = guarded_replace(code, old_fab_txt, new_fab_txt, "inject_lazy_thumbnails_into_draw:old_fab_txt")

    # Priority: Suppress background lover and wife buttons while character selector is open
    code = guarded_replace(code, 'comment = "futa ratings window";\nvar button_newlover_press = false;\nif (title == false && start_timer < 1)', 'comment = "futa ratings window";\nvar button_newlover_press = false;\nif (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)', "inject_lazy_thumbnails_into_draw:comment_futa_ratings_window_var_button_n", count=1)
    code = guarded_replace(code, 'comment = "switch partner button";\nmm_press4 = false;\nif (title == false && start_timer < 1)', 'comment = "switch partner button";\nmm_press4 = false;\nif (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)', "inject_lazy_thumbnails_into_draw:comment_switch_partner_button_mm_press4_", count=1)
    code = guarded_replace(code, 'if ((button_newlover_press == true || newlover_menu_toggle == true) && options_toggle == false && orgasm == false)', 'if (newlover_menu_toggle == true && newwife_menu_toggle == false && options_toggle == false && orgasm == false && futa_selector_open == false)', "inject_lazy_thumbnails_into_draw:if_button_newlover_press_true_newlover_m", count=1)
    code = guarded_replace(code, 'if (mm_press4 == true || newwife_menu_toggle == true)', 'if (newwife_menu_toggle == true && newlover_menu_toggle == false && options_toggle == false && futa_selector_open == false)', "inject_lazy_thumbnails_into_draw:if_mm_press4_true_newwife_menu_toggle_tr", count=1)


    # Keep overlay menu button behind CSS screens
    code = guarded_replace(code, 'var _fab_x_offset = round(room_width * 0.12);', 'if (futa_selector_open == false)\n{\nvar _fab_x_offset = round(room_width * 0.12);', "inject_lazy_thumbnails_into_draw:var_fab_x_offset_round_room_width_0_12", count=1)
    code = guarded_replace(code, '''draw_set_font(_mob_prev_fnt);
draw_set_halign(_mob_prev_halign);
draw_set_valign(_mob_prev_valign);
draw_set_color(_mob_prev_col);
draw_set_alpha(_mob_prev_alp);''', '''draw_set_font(_mob_prev_fnt);
draw_set_halign(_mob_prev_halign);
draw_set_valign(_mob_prev_valign);
draw_set_color(_mob_prev_col);
draw_set_alpha(_mob_prev_alp);
}''', "inject_lazy_thumbnails_into_draw:draw_set_font_mob_prev_fnt_draw_set_hali", count=1)
    # Subtle, unobtrusive opacity across mobile overlay
    code = guarded_replace(code, 'var _fab_alpha = (mob_expanded || _fab_over) ? 0.65 : 0.22;', 'var _fab_alpha = (mob_expanded || _fab_over) ? 0.40 : 0.12;', "inject_lazy_thumbnails_into_draw:var_fab_alpha_mob_expanded_fab_over_0_65", count=1)
    code = guarded_replace(code, 'draw_set_alpha((_qb_over && _mob_touch_d) ? 0.85 : 0.65);', 'draw_set_alpha((_qb_over && _mob_touch_d) ? 0.45 : 0.25);', "inject_lazy_thumbnails_into_draw:draw_set_alpha_qb_over_mob_touch_d_0_85_", count=1)
    code = guarded_replace(code, '''draw_set_alpha(0.85);
        draw_set_color(_qb_col);''', '''draw_set_alpha(0.40);
        draw_set_color(_qb_col);''', "inject_lazy_thumbnails_into_draw:draw_set_alpha_0_85_draw_set_color_qb_co", count=1)
    code = guarded_replace(code, '''draw_set_color(c_white);
        draw_text((_qbx1 + _qbx2) * 0.5, (_qby1 + _qby2) * 0.5, _qb_lbl);''', '''draw_set_alpha(0.65);
        draw_set_color(c_white);
        draw_text((_qbx1 + _qbx2) * 0.5, (_qby1 + _qby2) * 0.5, _qb_lbl);''', "inject_lazy_thumbnails_into_draw:draw_set_color_c_white_draw_text_qbx1_qb", count=1)
    code = guarded_replace(code, '''draw_set_alpha(0.58);
    draw_set_color(_c_mob_bg);''', '''draw_set_alpha(0.35);
    draw_set_color(_c_mob_bg);''', "inject_lazy_thumbnails_into_draw:draw_set_alpha_0_58_draw_set_color_c_mob", count=1)
    code = guarded_replace(code, '''draw_set_alpha(0.45);
    draw_set_color(_c_mob_border);''', '''draw_set_alpha(0.25);
    draw_set_color(_c_mob_border);''', "inject_lazy_thumbnails_into_draw:draw_set_alpha_0_45_draw_set_color_c_mob", count=1)
    code = guarded_replace(code, '''draw_set_alpha(0.85);
    draw_set_color(c_white);
    draw_text((_mx1 + _mx2) * 0.5, _my1 + 12, "CONTROLS");''', '''draw_set_alpha(0.55);
    draw_set_color(c_white);
    draw_text((_mx1 + _mx2) * 0.5, _my1 + 12, "CONTROLS");''', "inject_lazy_thumbnails_into_draw:draw_set_alpha_0_85_draw_set_color_c_whi", count=1)
    code = guarded_replace(code, 'draw_set_alpha((_btog_val || (_btn_over && _mob_touch_d && !mob_is_dragging)) ? 0.7 : 0.42);', 'draw_set_alpha((_btog_val || (_btn_over && _mob_touch_d && !mob_is_dragging)) ? 0.45 : 0.20);', "inject_lazy_thumbnails_into_draw:draw_set_alpha_btog_val_btn_over_mob_tou", count=1)
    code = guarded_replace(code, 'draw_set_alpha(_btog_val ? 0.8 : 0.35);', 'draw_set_alpha(_btog_val ? 0.50 : 0.20);', "inject_lazy_thumbnails_into_draw:draw_set_alpha_btog_val_0_8_0_35", count=1)
    code = guarded_replace(code, '''draw_set_alpha(0.85);
        draw_set_color(_btog_val ? _b_accent : c_white);''', '''draw_set_alpha(0.60);
        draw_set_color(_btog_val ? _b_accent : c_white);''', "inject_lazy_thumbnails_into_draw:draw_set_alpha_0_85_draw_set_color_btog_", count=1)

    # Force close Lover/Wife panels and stat graphs during climax
    old_ostart = gml("inject_lazy_thumbnails_into_draw/old_ostart")
    new_ostart = gml("inject_lazy_thumbnails_into_draw/new_ostart")
    code = guarded_replace(code, old_ostart, new_ostart, "inject_lazy_thumbnails_into_draw:old_ostart")

    code = guarded_replace(code, 'comment = "orgasm start for all cases";', 'if (orgasm == true) { newlover_menu_toggle = false; newwife_menu_toggle = false; }\ncomment = "orgasm start for all cases";', "inject_lazy_thumbnails_into_draw:comment_orgasm_start_for_all_cases", count=-1)




    LOGGER.log("Draw_0: Enhanced thumbnail loader with dynamic frame-count fallback.", prefix="[+]")
    return code


def enforce_strict_custom_selection(code):
    """Strictly loads and locks custom models on CUSTOM button press and swap grid click."""
    if "is_legacy_custom ? legacy_custom_mating_press : custom_mating_press" in code and "legacy_custom_wife_toggle ? legacy_custom_wife_mating_press : custom_wife_mating_press" in code:
        return code
    old_case8 = gml("enforce_strict_custom_selection/old_case8")

    new_case8 = gml("enforce_strict_custom_selection/new_case8")

    code = guarded_replace(code, old_case8, new_case8, "enforce_strict_custom_selection:old_case8")

    old_case6 = gml("enforce_strict_custom_selection/old_case6")

    new_case6 = gml("enforce_strict_custom_selection/new_case6")

    code = guarded_replace(code, old_case6, new_case6, "enforce_strict_custom_selection:old_case6")

    old_swap_click = gml("enforce_strict_custom_selection/old_swap_click")

    new_swap_click = gml("enforce_strict_custom_selection/new_swap_click")

# Clean stat graph logic preserved: 100% natural hover and panel binding


    # Layering & Drawing Safety Guards against -1 crashes
    old_bs = gml("enforce_strict_custom_selection/old_bs")

    new_bs = gml("enforce_strict_custom_selection/new_bs")
    code = guarded_replace(code, old_bs, new_bs, "enforce_strict_custom_selection:old_bs")

    old_bangs = '''    draw_sprite_ext(bangs_sprite, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 13 : 9, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);'''
    new_bangs = '''    if (bangs_sprite != -1 && sprite_exists(bangs_sprite))
        draw_sprite_ext(bangs_sprite, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 13 : 9, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);'''
    code = guarded_replace(code, old_bangs, new_bangs, "enforce_strict_custom_selection:old_bangs")

    old_w_bangs6 = gml("enforce_strict_custom_selection/old_w_bangs6")
    new_w_bangs6 = gml("enforce_strict_custom_selection/new_w_bangs6")
    code = guarded_replace(code, old_w_bangs6, new_w_bangs6, "enforce_strict_custom_selection:old_w_bangs6")

    old_w_bangs9 = gml("enforce_strict_custom_selection/old_w_bangs9")
    new_w_bangs9 = gml("enforce_strict_custom_selection/new_w_bangs9")
    code = guarded_replace(code, old_w_bangs9, new_w_bangs9, "enforce_strict_custom_selection:old_w_bangs9")

    old_w_eyes = gml("enforce_strict_custom_selection/old_w_eyes")
    new_w_eyes = gml("enforce_strict_custom_selection/new_w_eyes")
    code = guarded_replace(code, old_w_eyes, new_w_eyes, "enforce_strict_custom_selection:old_w_eyes")

    

    code = guarded_replace(code, old_swap_click, new_swap_click, "enforce_strict_custom_selection:old_swap_click")

    # Fix UI panel CUSTOM buttons for both Lover (case 8) and Wife (case 6)
    old_nl_custom = gml("enforce_strict_custom_selection/old_nl_custom")

    new_nl_custom = gml("enforce_strict_custom_selection/new_nl_custom")
    code = guarded_replace(code, old_nl_custom, new_nl_custom, "enforce_strict_custom_selection:old_nl_custom", optional=True)

    old_nw_custom = gml("enforce_strict_custom_selection/old_nw_custom")

    new_nw_custom = gml("enforce_strict_custom_selection/new_nw_custom")
    code = guarded_replace(code, old_nw_custom, new_nw_custom, "enforce_strict_custom_selection:old_nw_custom", optional=True)

    return code


def inject_complete_overlay(code):
    """Injects or updates the mobile touch overlay FAB, quick bar, drawer, and command execution."""
    target_fab = gml("inject_complete_overlay/target_fab")
    quick_r_n_c_o = gml("inject_complete_overlay/quick_r_n_c_o")

    # Do not inject duplicate quick access bar (already present in base engine)
    # Just update the single existing quick bar's [N] button to force-close panels
    code = guarded_replace(code, 'else if (_qb_key == 78)\n            {\n                orgasm_start = true;\n                orgasm = true;\n                keyboard_key_press(ord("N"));\n                mob_release_key = 78;\n            }', 'else if (_qb_key == 78)\n            {\n                newlover_menu_toggle = false;\n                newwife_menu_toggle = false;\n                orgasm_start = true;\n                orgasm = true;\n                keyboard_key_press(ord("N"));\n                mob_release_key = 78;\n            }', "inject_complete_overlay:else_if_qb_key_78_orgasm_start_true_orga", count=1)

    old_btns_def = '    var _btns = [["[N] CLIMAX", 78, 0, 0, _c_mob_accent], ["[M] MAN:" + _man_status, 77, 1, manual_mode > 0, make_color_rgb(0, 210, 110)], ["[RADIAL MENU]", "RADIAL", 1, radial_menu_open, make_color_rgb(0, 180, 230)], ["[T] " + _peek_status, 84, 0, 0, 16777215], ["[C] WIFE CLIM", 67, 0, 0, 16777215], ["[O] OVULATE", 79, 0, 0, 16777215], ["[G] GHOST", 71, 1, futa_ghost_toggle, _c_mob_accent], ["[Q] REROLL", 81, 0, 0, 16777215], ["[H] HITBOX", 72, 1, mob_hitbox_active, make_color_rgb(160, 0, 220)], ["[R] RESET", 82, 0, 0, 16777215], ["[ESC] BACK", 27, 0, 0, make_color_rgb(220, 60, 60)], ["[ENTER] SET", 13, 0, 0, make_color_rgb(60, 180, 80)]];'
    new_btns_def = gml("inject_complete_overlay/new_btns_def")

    code = guarded_replace(code, old_btns_def, new_btns_def, "inject_complete_overlay:old_btns_def")

    code = guarded_replace(code, "if (mob_lp_timer == 22 && !radial_menu_open && title == false && orgasm == false)", "if (mob_lp_timer == 22 && !radial_menu_open && title == false && orgasm == false && variable_instance_exists(id, \"manual_mode\") && manual_mode > 0)", "inject_complete_overlay:if_mob_lp_timer_22_radial_menu_open_titl", count=-1)

    old_btn_exec = gml("inject_complete_overlay/old_btn_exec")

    new_btn_exec = gml("inject_complete_overlay/new_btn_exec")

    code = guarded_replace(code, old_btn_exec, new_btn_exec, "inject_complete_overlay:old_btn_exec")

    return code
