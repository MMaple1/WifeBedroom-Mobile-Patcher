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
    - Incompatible or corrupted character packs are skipped and listed in output/<apk>_skipped_packs.md
      (moved to output/quarantine/<date-time>/ only with --move-skipped).
"""

import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Re-export every public name so existing scripts and tests can keep using this module.
from wbp.common import *
from wbp.axml import *
from wbp.detect import *
from wbp.env import *
from wbp.packs import *
from wbp.engines import *
from wbp.gml_patches import *
from wbp.toy import *
from wbp.apk import *
from wbp.cli import *

if __name__ == "__main__":
    main()
