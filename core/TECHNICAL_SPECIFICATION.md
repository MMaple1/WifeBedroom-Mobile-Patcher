# Deeproom 4.0, ModRoom v3.3 & Wife's Bedroom v1.5 Mobile Technical Architecture Specification (v1.2)

This specification is an engineering reference for modders, tool developers and maintainers who work on the mobile and touch systems that the WB Mobile Patcher adds to Deeproom, ModRoom and Wife's Bedroom builds using UndertaleModTool (UTMT) or GameMaker Studio source.

Every numbered section states:
- **Component ID and provenance**: `[Deeproom Mobile Custom]`, `[ToyBridge]` or another family tag
- **Target object and event**: the place in GameMaker's object hierarchy the change attaches to
- **Anchor**: the text the patcher searches for in the game's code, or the function a bundled script defines
- **What it does**, in present tense, as the shipped code does it
- **Code excerpt** copied verbatim from the shipped sources (omitted lines are marked `// ...`)
- **Source**: the file and function or snippet where the behaviour lives

## How to read this specification

**Where the code lives.** The patcher is `WB_Mobile_Patcher.py` (launcher) plus the `wbp/` package. Module map: `common` (logger, `guarded_replace`, GML snippet loader), `axml` (Android manifest editor), `detect` and `env` (engine and tool detection), `packs` (pack classification, duplicate skipping, manifests, name bridging, asset gathering), `descriptors` and `profiles` (per-engine descriptors and rules), `engines` (`patch_v15_engine_bytecode`, `patch_mr33_engine_bytecode`), `gml_patches` (the dynamic patcher), `apk` (`patch_game_apk`), `toy` and `toy_native` (hardware telemetry), `wbconv` (shared conversion core, identical in both converters) and `cli`. GML strings the patchers inject live in `core/gml_patches/<function>/<name>.gml`; complete replacement scripts for Deeproom live in `core/bundle_src/` and are packed into `core/mobile_engine.bundle`.

**Which code runs for which game.** `patch_game_apk()` picks one path per detected engine:

| Detected engine | GML comes from |
|---|---|
| Deeproom 4.0.3 Kiwami | `core/mobile_engine.bundle`: complete replacement scripts for eight code entries |
| ModRoom v3.3 | `patch_mr33_engine_bytecode()` in `wbp/engines.py` |
| Wife's Bedroom v1.5 | `patch_v15_engine_bytecode()` in `wbp/engines.py` |
| Fallback: a path above fails, or Deeproom without the bundle | the dynamic patcher in `wbp/gml_patches.py`: `patch_create_code()`, `patch_draw_code()`, `patch_step_code()` and the functions they call |

A feature can therefore exist in the bundle and differ on the other paths, or the reverse; each section's excerpt names the path it comes from.

**Reading the bundle.** It is zlib-compressed JSON mapping code-entry file name to GML source:

```text
import json, zlib
scripts = json.loads(zlib.decompress(open("core/mobile_engine.bundle", "rb").read()))
print(list(scripts))                      # e.g. gml_Object_oFutaMatingPress_Create_0.gml
print(scripts["gml_Object_oFutaMatingPress_Draw_0.gml"][:500])
```

`python tools/bundle_tool.py unpack` writes the same scripts to `core/bundle_src/`; `pack` rebuilds the bundle. Because the bundle replaces whole scripts, it also carries the game's own functions for those entries.

**Anchors and missing anchors.** Anchors given as decompiled line numbers shift between game builds; search for the anchor text instead. Patches that look for text in the game's GML use `guarded_replace()`, which records a miss instead of skipping silently; misses are written to `output/<apk>_patch_report.txt`. A miss is normal for a patch written for another engine version.

**Keeping the excerpts true.** `python tools/spec_check.py --strict` fails when any code excerpt in this file has a line that is not in the shipped sources, or when the text carries review notes. Run it after changing the code or the specification.

**Related tools.** The two companion converters (`Modded_to_WB_1.5.py`, `WB_1.5_to_Modded.py`) are separate programs that share `wbconv.py`; Part 6 describes the conversion rules they and the patcher use. Feature IDs in the patcher's own docstrings are numbered differently from this specification; this document's numbering is used throughout.

---

## Table of Contents

- [Part 1: Core Engine & Lifecycle Enhancements](#part-1-core-engine--lifecycle-enhancements)
  - [1. [DR-01] [Deeproom Mobile Custom] Native Manifest Stream Scanning (_manifest.txt)](#1-dr-01-deeproom-mobile-custom-native-manifest-stream-scanning-_manifesttxt)
  - [2. [DR-02] [Deeproom Mobile Custom] Android Asset Path Normalization (tc_norm_path)](#2-dr-02-deeproom-mobile-custom-android-asset-path-normalization-tc_norm_path)
  - [3. [DR-03] [Deeproom Mobile Custom] Multi-Directory Dialogue Scanning & Safe Parser](#3-dr-03-deeproom-mobile-custom-multi-directory-dialogue-scanning--safe-parser)
  - [4. [DR-04] [Deeproom Mobile Custom] Custom Bedrooms Scanner & Touch Drag Scrolling Navigation](#4-dr-04-deeproom-mobile-custom-custom-bedrooms-scanner--touch-drag-scrolling-navigation)
  - [5. [DR-05] [Deeproom Mobile Custom] Sandboxed Storage & Persistent Session Redirection (setting_data.sav)](#5-dr-05-deeproom-mobile-custom-sandboxed-storage--persistent-session-redirection-setting_datasav)
- [Part 2: Character Rigging, Scaling & Pill Protections](#part-2-character-rigging-scaling--pill-protections)
  - [6. [DR-06] [Deeproom Mobile Custom] Universal Origin-Based Model Scaling & Multi-Frame Slicing](#6-dr-06-deeproom-mobile-custom-universal-origin-based-model-scaling--multi-frame-slicing)
  - [7. [DR-07] [Deeproom Mobile Custom] Pill Custom Asset Protections, Sheath Fallbacks & Proportional Condom Scaling](#7-dr-07-deeproom-mobile-custom-pill-custom-asset-protections-sheath-fallbacks--proportional-condom-scaling)
  - [8. [DR-08] [Deeproom Mobile Custom] Ovulation Disentanglement from Wife Climax (func_wife_climax)](#8-dr-08-deeproom-mobile-custom-ovulation-disentanglement-from-wife-climax-func_wife_climax)
  - [9. [DR-09] [Deeproom Mobile Custom] Custom Spouse X-Ray Origin Coordinates Initialization](#9-dr-09-deeproom-mobile-custom-custom-spouse-x-ray-origin-coordinates-initialization)
- [Part 3: Rendering Pipeline Stability & Fallbacks](#part-3-rendering-pipeline-stability--fallbacks)
  - [10. [DR-10] [Deeproom Mobile Custom] Lover-Wife Portrait Fallback Parity Architecture](#10-dr-10-deeproom-mobile-custom-lover-wife-portrait-fallback-parity-architecture)
  - [11. [DR-11] [Deeproom Mobile Custom] Non-Negative Sprite Shield & Condom/X-ray Fallbacks](#11-dr-11-deeproom-mobile-custom-non-negative-sprite-shield--condomx-ray-fallbacks)
  - [12. [DR-12] [Deeproom Mobile Custom] Clean Portrait Unloading & Cross-Character Isolation](#12-dr-12-deeproom-mobile-custom-clean-portrait-unloading--cross-character-isolation)
  - [13. [DR-13] [Deeproom Mobile Custom] Dynamic Composite Thumbnail Slicing & Frame Fallback](#13-dr-13-deeproom-mobile-custom-dynamic-composite-thumbnail-slicing--frame-fallback)
- [Part 4: Touch UI, Character Selection Screen (CSS) & Navigation](#part-4-touch-ui-character-selection-screen-css--navigation)
  - [14. [DR-14] [Deeproom Mobile Custom] CSS Auto-Scroll & Centering Math (Jump-to-Selected)](#14-dr-14-deeproom-mobile-custom-css-auto-scroll--centering-math-jump-to-selected)
  - [15. [DR-15] [Deeproom Mobile Custom] CSS Equipped Partner Pulsing Gold Border & Title Star](#15-dr-15-deeproom-mobile-custom-css-equipped-partner-pulsing-gold-border--title-star)
  - [16. [DR-16] [Deeproom Mobile Custom] CSS Card Click Isolation & Star Hitbox Disentanglement (!_star_hover)](#16-dr-16-deeproom-mobile-custom-css-card-click-isolation--star-hitbox-disentanglement-_star_hover)
  - [17. [DR-17] [Deeproom Mobile Custom] CSS Geometric Vector Star Badges, Silent Click Isolation & Dynamic Filter](#17-dr-17-deeproom-mobile-custom-css-geometric-vector-star-badges-silent-click-isolation--dynamic-filter)
  - [18. [DR-18] [Deeproom Mobile Custom] CSS Modal Input Priority & Background Suppression](#18-dr-18-deeproom-mobile-custom-css-modal-input-priority--background-suppression)
  - [19. [DR-19] [Deeproom Mobile Custom] CSS Header Layout: Left Search Bar, Right-Side [FAV: ALL/ON] Toggle & Locked Close Button](#19-dr-19-deeproom-mobile-custom-css-header-layout-left-search-bar-right-side-fav-allon-toggle--locked-close-button)
  - [20. [DR-20] [Deeproom Mobile Custom] CSS Mobile Virtual Keyboard Trigger & Auto-Dismissal](#20-dr-20-deeproom-mobile-custom-css-mobile-virtual-keyboard-trigger--auto-dismissal)
  - [21. [DR-21] [Deeproom Mobile Custom] Mutual Panel Exclusivity & Radar Chart Isolation](#21-dr-21-deeproom-mobile-custom-mutual-panel-exclusivity--radar-chart-isolation)
  - [22. [DR-22] [Deeproom Mobile Custom] Climax Screen Protection & Panel Auto-Closing](#22-dr-22-deeproom-mobile-custom-climax-screen-protection--panel-auto-closing)
  - [23. [DR-23] [Deeproom Mobile Custom] Translucent Mobile Overlay with Strict Modal Z-Ordering](#23-dr-23-deeproom-mobile-custom-translucent-mobile-overlay-with-strict-modal-z-ordering)
  - [24. [DR-24] [Deeproom Mobile Custom] Single-Trigger Overlay Action Execution](#24-dr-24-deeproom-mobile-custom-single-trigger-overlay-action-execution)
  - [25. [DR-25] [Deeproom Mobile Custom] Uninterrupted 8-Mechanic Gameplay Interaction & Disclaimer One-Time Gate](#25-dr-25-deeproom-mobile-custom-uninterrupted-8-mechanic-gameplay-interaction--disclaimer-one-time-gate)
  - [26. [DR-26] [Deeproom Mobile Custom] Neutralization of Rickroll Fake Crash Loop in Step_0](#26-dr-26-deeproom-mobile-custom-neutralization-of-rickroll-fake-crash-loop-in-step_0)
- [Part 5: Android Platform & ToyBridge Foundation Systems](#part-5-android-platform--toybridge-foundation-systems)
  - [27. [TB-01] [ToyBridge] Synthetic Right-Click & Touch Hold Engine](#27-tb-01-toybridge-synthetic-right-click--touch-hold-engine)
  - [28. [TB-02] [ToyBridge] Single-Column Vertical Menu Layout](#28-tb-02-toybridge-single-column-vertical-menu-layout)
  - [29. [TB-03] [ToyBridge] Drag-to-Scroll Accumulator (menu_scroll_update)](#29-tb-03-toybridge-drag-to-scroll-accumulator-menu_scroll_update)
  - [30. [TB-04] [ToyBridge] SIZES Options Page Hyper-Scale Toggle (TouchHyperToggle)](#30-tb-04-toybridge-sizes-options-page-hyper-scale-toggle-touchhypertoggle)
  - [31. [TB-05] [ToyBridge] On-Device Mod Sharing Activity (wbmods.PhoneImportActivity)](#31-tb-05-toybridge-on-device-mod-sharing-activity-wbmodsphoneimportactivity)
  - [32. [DR-27] [Deeproom Mobile Custom] Pure Python Binary AXML Editor & APK DEX Bundling](#32-dr-27-deeproom-mobile-custom-pure-python-binary-axml-editor--apk-dex-bundling)
  - [33. [TB-06] [ToyBridge] Optional External UDP Telemetry Broadcast (buttplug_socket)](#33-tb-06-toybridge-optional-external-udp-telemetry-broadcast-buttplug_socket)
  - [34. [DR-28] [Deeproom Mobile Custom] Pre-Flight Mod Pack Classification & Quarantine Architecture](#34-dr-28-deeproom-mobile-custom-pre-flight-mod-pack-classification--quarantine-architecture)
  - [35. [DR-29] [Deeproom Mobile Custom] Universal ModRoom & Legacy Spouse Format Detection (check_custom_wife)](#35-dr-29-deeproom-mobile-custom-universal-modroom--legacy-spouse-format-detection-check_custom_wife)
  - [36. [DR-30] [Deeproom Mobile Custom] Mobile Audio & Voice Pack Streaming (custom_music & custom_sounds)](#36-dr-30-deeproom-mobile-custom-mobile-audio--voice-pack-streaming-custom_music--custom_sounds)
  - [37. [DR-31] [Deeproom Mobile Custom] Anatomy Sprite & Boob Box Pre-Flight Safety Guards](#37-dr-31-deeproom-mobile-custom-anatomy-sprite--boob-box-pre-flight-safety-guards)
  - [38. [DR-32] [Deeproom Mobile Custom] Screen Boundary Clamping for Mobile Dragging Menus](#38-dr-32-deeproom-mobile-custom-screen-boundary-clamping-for-mobile-dragging-menus)
  - [39. [DR-33] [Deeproom Mobile Custom] Dual-Engine Bytecode Ingestion, v1.5 Manifest Streaming & Unified Alphabetical Ingestion](#39-dr-33-deeproom-mobile-custom-dual-engine-bytecode-ingestion-v15-manifest-streaming--unified-alphabetical-ingestion)
  - [40. [DR-34] [Deeproom Mobile Custom] Multi-Input Ingestion, Extended CLI, Modular Install Modes & Dynamic Naming](#40-dr-34-deeproom-mobile-custom-multi-input-ingestion-extended-cli-modular-install-modes--dynamic-naming)
- [Part 6: Version 1.1 Multi-Engine Architecture, Universal Asset Bridging & Companion Converters](#part-6-version-11-multi-engine-architecture-universal-asset-bridging--companion-converters)
  - [41. [DR-35] [Tri-Engine] Multi-Version Engine Detection, Bytecode Matrix & Native Streaming](#41-dr-35-tri-engine-multi-version-engine-detection-bytecode-matrix--native-streaming)
  - [42. [DR-36] [Tri-Engine] Universal Bi-Directional Filename Bridge & Forward Deduplication](#42-dr-36-tri-engine-universal-bi-directional-filename-bridge--forward-deduplication)
  - [43. [DR-37] [GameMaker GML] Bytecode Compatibility & Control-Character Escaping](#43-dr-37-gamemaker-gml-bytecode-compatibility--control-character-escaping)
  - [44. [DR-38] [Universal Shield] Universal Wife Recognition Shield & Cowgirl Fallback Architecture](#44-dr-38-universal-shield-universal-wife-recognition-shield--cowgirl-fallback-architecture)
  - [45. [DR-39] [Sprite Integrity] ModRoom v3.3 Frame Divisor Slicing Math & Transparent Padding Cure](#45-dr-39-sprite-integrity-modroom-v33-frame-divisor-slicing-math--transparent-padding-cure)
  - [46. [DR-40] [Pack Discovery] Universal Recursive Mod Pack Discovery Engine](#46-dr-40-pack-discovery-universal-recursive-mod-pack-discovery-engine)
  - [47. [DR-41] [Companion Converters] Bi-Directional Dual-Architecture Converter Suite](#47-dr-41-companion-converters-bi-directional-dual-architecture-converter-suite)
- [Part 7: ToyBridge 1.5.3 Full Suite, Bluetooth Latency & Synthesis Architecture](#part-7-toybridge-153-full-suite-bluetooth-latency--synthesis-architecture)
  - [48. [TB-07] [ToyBridge 1.5.3] Standalone Direct WebSocket Client (--toy-mode direct, Other_68)](#48-tb-07-toybridge-153-standalone-direct-websocket-client---toy-mode-direct-other_68)
  - [49. [TB-08] [ToyBridge 1.5.3] In-Engine Lead Prediction & Bluetooth Latency Compensation (0-500ms)](#49-tb-08-toybridge-153-in-engine-lead-prediction--bluetooth-latency-compensation-0-500ms)
  - [50. [TB-09] [ToyBridge 1.5.3] Anti-Hang Connection Retry Limiter & Title Screen Touch Controls](#50-tb-09-toybridge-153-anti-hang-connection-retry-limiter--title-screen-touch-controls)
  - [51. [TB-10] [ToyBridge 1.5.3] HMV Audio Beat-Sync Mode & Interactive Bed Speakers](#51-tb-10-toybridge-153-hmv-audio-beat-sync-mode--interactive-bed-speakers)
  - [52. [TB-11] [ToyBridge 1.5.3] Descriptor [info] Section Synthesis & Safe Fallback Architecture](#52-tb-11-toybridge-153-descriptor-info-section-synthesis--safe-fallback-architecture)
- [Part 8: v1.1 Pack Pipeline, Engine Safety & Asset Features](#part-8-v11-pack-pipeline-engine-safety--asset-features)
  - [53. [DR-42] [3-Tier Duplicate Pipeline] Automated Cross-Folder & Multi-Content Duplicate Detection Architecture](#53-dr-42-3-tier-duplicate-pipeline-automated-cross-folder--multi-content-duplicate-detection-architecture)
  - [54. [DR-43] [Deeproom 4.0.3 Kiwami Engine Architecture] Container Traversal, Manifest Dual-Routing & INI Specification](#54-dr-43-deeproom-403-kiwami-engine-architecture-container-traversal-manifest-dual-routing--ini-specification)
  - [55. [DR-44] [Dynamic Variable Safety Shield] Live Bytecode Extraction & Guard Synthesis Architecture](#55-dr-44-dynamic-variable-safety-shield-live-bytecode-extraction--guard-synthesis-architecture)
  - [56. [DR-45] [In-Game Portrait Interaction Offsets] Real-Time Calibration & Dual-Character Memory Parity](#56-dr-45-in-game-portrait-interaction-offsets-real-time-calibration--dual-character-memory-parity)
  - [57. [DR-46] [Custom SFX Engine] Dynamic Audio Loading, Randomization & Mod Overrides](#57-dr-46-custom-sfx-engine-dynamic-audio-loading-randomization--mod-overrides)
  - [58. [DR-47] [Sprite Strip Padding Protection] ModRoom v3.3 Slicing Math Parity](#58-dr-47-sprite-strip-padding-protection-modroom-v33-slicing-math-parity)
  - [59. [DR-48] [Universal Loose-Portrait Resolution] Auto-Aliasing Variant Filenames](#59-dr-48-universal-loose-portrait-resolution-auto-aliasing-variant-filenames)
  - [60. [DR-49] [Universal Bridge & Full 8-Category Engine Loaders] Multi-Directory GML Resolvers](#60-dr-49-universal-bridge--full-8-category-engine-loaders-multi-directory-gml-resolvers)
- [Part 9: Build Pipeline, Packaging & Maintenance](#part-9-build-pipeline-packaging--maintenance)
  - [61. [DR-50] [Pipeline] Build Pipeline Overview](#61-dr-50-pipeline-build-pipeline-overview)
  - [62. [DR-51] [Packaging] APK Repackaging Rules](#62-dr-51-packaging-apk-repackaging-rules)
  - [63. [DR-52] [Signing] APK Signing & Alignment](#63-dr-52-signing-apk-signing--alignment)
  - [64. [DR-53] [Pack Safety] Non-Destructive Pack Skipping & Reports](#64-dr-53-pack-safety-non-destructive-pack-skipping--reports)
  - [65. [DR-54] [GML] Additional Injected Features](#65-dr-54-gml-additional-injected-features)
  - [66. [DR-55] [Maintenance] Adding or Changing a Patch](#66-dr-55-maintenance-adding-or-changing-a-patch)
  - [67. [DR-56] [Environment] Requirements & Bundled Tools](#67-dr-56-environment-requirements--bundled-tools)
  - [68. [DR-57] [Pack Formats] Wife / Spouse Formats & the Filename Bridge](#68-dr-57-pack-formats-wife--spouse-formats--the-filename-bridge)

---

## Glossary

| Term | Meaning |
|---|---|
| **DR-xx / TB-xx** | Feature IDs: DR = Deeproom mobile features written for this tool, TB = features ported from ToyBridge |
| **ToyBridge** | Upstream mobile-touch and telemetry project; its functionality is now natively implemented by the patcher |
| **Kiwami** | The Deeproom 4.0.3 edition |
| **CSS** | Character Selection Screen (the partner/spouse grid) |
| **data.win / game.droid** | GameMaker's compiled game data: `data.win` on PC, `assets/game.droid` inside the APK |
| **Code entry** | One GML script in the game data, named `gml_Object_<object>_<event>_<n>`, e.g. `gml_Object_oFutaMatingPress_Draw_0` |
| **UndertaleModCli (UTMT)** | Command-line UndertaleModTool used to dump and replace code entries in `game.droid` |
| **Engine bundle** | `core/mobile_engine.bundle`: zlib-compressed JSON of complete replacement scripts for Deeproom 4.0.3 |
| **Pack** | One mod folder (character, spouse, bedroom …) containing assets and a descriptor |
| **custom_stuff/** | Deeproom 4.0.3's container folder for packs |
| **Manifest (`_manifest.txt`)** | Text index of a folder's contents, read instead of slow `file_find_*` scans on Android (DR-01) |
| **Variable shield** | Generated guards that create variables the patched code reads but the game never set (DR-44) |
| **Skip report** | `<apk>_skipped_packs.md/.json`, listing packs left out of a build (DR-53) |
| **AXML / DEX** | Android binary XML (e.g. `AndroidManifest.xml`) and Android bytecode files |
| **Engine profile** | `EngineProfile` in `wbp/profiles.py`: contains modern naming support flags and required sprite lists |
| **Bridge planner** | `plan_name_bridge()` in `wbp/packs.py`: generates filename copies to adapt different engine formats |
| **Admission rules** | The sprite set a pack must possess (based on `MODROOM_NEEDS`) before an engine lists it |
| **Modern / ModRoom format** | `custom_data.wife` with `custom_wife_*_0.png` strips and `_alt_N` variants |
| **Legacy / standard format** | `custom_data.spouse` (or `.futa`) with standard names such as `custom_mating_press.png` |
| **Intiface Central** | Desktop/phone server app that drives toys over Bluetooth (Buttplug protocol) |
| **HMV** | Beat-sync mode that follows music timing |

---

---

## Upstream Developer Integration Map (By Target Object & Event)

For downstream modders and engine maintainers integrating these features directly via UndertaleModTool or GameMaker Studio, this map groups the GML subsystems by the exact object and event file you need to open:

### 1. File: `gml_Object_oFutaMatingPress_Create_0`
Open this script once to integrate all lifecycle, scaling, and initialization subsystems:
- **Phone mods registry**: `pm_registry_read/write/add/remove` keep `<save>/phone_mods_registry.txt`, the list of everything phone imports created (see the phone-mods paragraph under section 31).
- **Variable Initializations**: Define `boob_box = false;`, `cowgirl_origin_y = 84;`, `selector_favs_only = false;`, `global.favs_futa = ds_map_create();` upfront.
- **`[DR-01]`**: Ingest `custom_futas/_manifest.txt` and `custom_wives/_manifest.txt` inside scanner functions.
- **`[DR-02]`**: Define `tc_norm_path(path)` leading-slash normalizer.
- **`[DR-05]`**: Ingest and save settings in `setting_data.sav` and `func_save_settings()`.
- **`[DR-06]`**: Dynamic multi-frame slicer and `160 / frame_w` scale normalization in `func_load_custom_futa()`. `func_futa_pack_is_legacy()` chooses the loader, the same on PC and phone: standard names when `custom_mating_press.png` exists or `custom_futa_mating_press_0.png` is missing, otherwise the `_0.png` loader.
- **`[DR-07]`**: Out-of-bounds frame guards in `func_get_futa_frame()`.
- **`[DR-08]`**: Disentangle `func_ovulate()` from `func_wife_climax()`.
- **`[DR-09]`**: Initialize default `xray_origin_x = 80; xray_origin_y = 84;` in `func_load_custom_spouse()`.
- **`[DR-12]`**: Every character switch clears both portrait slots (`custom_portrait` and `legacy_custom_portrait`, and the two partner slots) and sets the portrait scale, so no previous portrait can stay on screen.
- **`[TB-03]`**: Add touch drag accumulator (one row per 64 px of drag) in the UI update logic.
- **`[TB-07]`**: Initialize `buttplug_socket = network_create_socket(network_socket_tcp)` and protocol handshake.
- **`[DR-29]`**: Add `check_custom_wife(path)` universal ModRoom and Legacy format validator.
- **`[DR-30]`**: Stream `custom_music/*.ogg` and `custom_sounds/futa/*` voice packs.

### 2. File: `gml_Object_oFutaMatingPress_Draw_0`
Open this script to integrate all rendering, UI modal gating, and touch controls:
- **`[DR-10]`**: Lover portrait fallback parity (`_is_custom_lover` conditional and `_lover_base_portrait`).
- **`[DR-11]`**: Non-negative sprite shields before `draw_sprite_ext` for `c_sprite`, `dt_c_sprite`, and `legacy_xray_sprite`.
- **`[DR-13]`**: Dynamic composite thumbnail loader with aspect ratio probing.
- **`[DR-14]`**: Centering auto-scroll math on equipped partner upon CSS opening using `_sel_jump_done` latch.
- **`[DR-15]`**: Equipped partner animated gold glow border and header title star.
- **`[DR-16]`**: Card click isolation guard (`!_star_hover`) preventing accidental equipping when toggling bookmarks.
- **`[DR-17]`**: Geometric vector star badge with immediate write/delete in `setting_data.sav`.
- **`[DR-18]`**: Modal input suppression on background buttons during CSS display.
- **`[DR-19]`**: Selector header: search bar on the left, `[FAV: ALL/ON]` filter button on the right, with touch precedence.
- **`[DR-20]`**: Mobile virtual keyboard trigger (`keyboard_virtual_show`) and search filter handling.
- **`[DR-21]`**: Mutually exclusive radar stat graphs bound strictly to active panels.
- **`[DR-22]`**: Climax screen auto-closing forcing floating panels to hide.
- **`[DR-23]`**: Translucent mobile overlay ($0.12$ idle, $0.40$ active) suppressed when CSS is open.
- **`[DR-24]`**: Consolidated single-loop quick actions preventing double execution.
- **`[DR-25]`**: Remove modal lockouts to unlock all 8 mechanics during open menus.
- **`[TB-01]`**: Synthetic right-click touch hold timer (`mob_lp_timer`).
- **`[TB-02]`**: Single-column vertical menu pill layout calculation.
- **`[TB-04]`**: SIZES options page `[HYPER: ON/OFF]` toggle with slider range expansion.
- **`[TB-07]`**: Direct WebSocket telemetry packets sent to Intiface.
- **`[DR-31]`**: Anatomy render shield (`if (sprite_exists(anatomy_sprite))`).
- **`[DR-32]`**: Touch drag boundary clamping for floating panels.

### 3. File: `gml_Object_oFutaMatingPress_Step_0`
- **`[DR-22]`**: Guard portrait hover hitboxes during climax or when CSS is open.
- **`[DR-26]`**: Neutralize legacy desktop crash triggers.
- **`[TB-10]`**: Audio beat-sync frequency analysis and state updates for HMV mode.

### 4. File: `gml_Object_oBackground_Create_0`
- **`[DR-04]`**: Custom bedrooms scanner reading `custom_bedrooms/_manifest.txt` directly.

### 5. File: `gml_Object_oDialogueManager_Create_0`
- **`[DR-03]`**: Safe dialogue JSON parsing with `try / catch` blocks.
- **`[DR-03]`**: Dialogue pack precedence: `dialogue_packs/` preferred over built-in text.

### 6. Android Platform Packaging Layer
- **`[TB-05]`**: Bundle `phone_import.dex` containing `wbmods.PhoneImportActivity` as secondary DEX.
- **`[DR-27]`**: Binary AXML injection into `AndroidManifest.xml` registering the import activity.
- **`[DR-28]`**: Pre-flight pack checks via `classify_custom_pack`, `missing_sprites` and, for Deeproom, `deeproom_strip_problems` (strips that do not divide into their loader's frame count, partners without a portrait) to prevent runtime crashes and cut-up sprites.

---

---

## Variable Scope & Initialization Master Reference

| Variable Name | Scope | Defined In | Default Value | Architectural Function |
| :--- | :--- | :--- | :--- | :--- |
| `custom_mating_press_scale` | Instance | `Create (0)` | `1.0` | Normalization scale factor ($160 / \text{frame\_w}$) for the lover's mating-press sprite. |
| `global.favs_futa` | Global | `Create (0)` | `ds_map_create()` | Map containing names of bookmarked custom lovers. |
| `global.favs_wife` | Global | `Create (0)` | `ds_map_create()` | Map containing names of bookmarked custom spouses. |
| `selector_favs_only` | Instance | `Create (0)` | `false` | Boolean toggle filtering CSS grid to show only starred cards. |
| `_sel_jump_done` | Instance | `Draw (0)` | `false` | One-shot latch ensuring CSS only auto-scrolls once per menu opening. |
| `boob_box` | Instance | `Create (0)` | `false` | Safety initialization preventing early uninitialized variable lookups. |
| `cowgirl_origin_y` | Instance | `Create (0)` | `84` | Default vertical origin coordinate. |
| `tc_hyper` | Instance | `Create (0)` | `false` (true when `hyper_sizes.on` exists in the save folder) | SIZES options page multiplier expanding slider limits. |
| `mob_expanded` | Instance | `Create (0)` | `false` | Toggle state for the mobile floating action drawer menu. |
| `mob_lp_timer` | Instance | `Create (0)` | `0` | Touch-hold frame counter used to synthesize right-clicks. |
| `selector_search_focused`| Instance | `Create (0)` | `false` | Tracks whether the CSS search bar is focused. |
| `buttplug_socket` | Instance | `Create (0)` | `-1` | TCP socket for Intiface Central WebSocket communication. |
| `xray_origin_x` / `xray_origin_y` | Instance | `Create (0)` | `80` / `84` | X-ray overlay origin for custom spouses. |
| `custom_condom_scale` | Instance | `Create (0)` | `1` | Condom sprite scale, matched to the lover's scale. |
| `offset_panel_open` | Instance | `Create (0)` | `false` | Whether the in-game offset calibration panel is open. |

---

## Part 1: Core Engine & Lifecycle Enhancements

### 1. [DR-01] [Deeproom Mobile Custom] Native Manifest Stream Scanning (_manifest.txt)

- **Target Object**: `oBackground` / `oDialogueManager`
- **Target Event**: `Create (0)`
- **Anchor**: `tc_ff_first` and `tc_ff_next` implementations

Bypasses slow, blocking filesystem loops by streaming newline-delimited text manifests (`_manifest.txt`) into memory. This replaces the file walking on mobile platforms (the manifest-less fallback still walks the folder) to prevent ANR timeouts. Exception (2026-11-17): folders inside the game's own save folder (`tc_is_save_path`), which the game creates on the phone and which have no `_manifest.txt`, are listed with `file_find_first`. The same functions also exist in `oFutaMatingPress`.

```gml
    var _pat = string_lower(string_delete(_m, 1, _cut));
    var _suf = (string_char_at(_pat, 1) == "*") ? string_delete(_pat, 1, 1) : "";
    tc_ff_items = [];
    var _f = file_text_open_read(_mf);
    if (_f != -1)
    {
        while (!file_text_eof(_f))
        {
            var _ln = string_replace_all(string_replace_all(file_text_readln(_f), "\r", ""), "\n", "");
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
```

Source: bundle_src/gml_Object_oBackground_Create_0.gml, tc_ff_first; wbp/gml_patches.py, patch_create_code

---

### 2. [DR-02] [Deeproom Mobile Custom] Android Asset Path Normalization (tc_norm_path)

- **Target Object**: `oBackground` / `oDialogueManager`
- **Target Event**: `Create (0)`
- **Anchor**: Function definition `tc_norm_path(arg0)`

Normalizes double slashes and, on Android and iOS, strips leading slashes so asset paths resolve. Paths inside the game's save folder (`game_save_id`, checked by `tc_is_save_path`) keep their leading slash, because they are absolute (`/data/user/0/<app>/files/...`). The same function also exists in `oFutaMatingPress`.

```gml
function tc_norm_path(arg0)
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
}
```

Source: bundle_src/gml_Object_oBackground_Create_0.gml, tc_norm_path

---

### 3. [DR-03] [Deeproom Mobile Custom] Multi-Directory Dialogue Scanning & Safe Parser

- **Target Object**: `oDialogueManager`
- **Target Event**: `Create (0)`
- **Anchor**: `dialogue_files` initialization and `load_dialogue_file()`

Scans multiple directories for dialogue JSON files using manifest-aware stream scanning. Includes a safe parser that handles JSON syntax errors without crashing the engine.

```gml
var _dlg_pack_dir = (file_exists("custom_stuff/dialogue_packs/_manifest.txt") || file_exists("assets/custom_stuff/dialogue_packs/_manifest.txt")) ? "custom_stuff/dialogue_packs" : "dialogue_packs";
var file_name = tc_ff_first(_dlg_pack_dir + "/*.json", 0);
while (file_name != "")
{
    array_push(dialogue_files, file_name);
    file_name = tc_ff_next();
}
tc_ff_close();
// ...
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
```

Source: bundle_src/gml_Object_oDialogueManager_Create_0.gml, load_dialogue_file

---

### 4. [DR-04] [Deeproom Mobile Custom] Custom Bedrooms Scanner & Touch Drag Scrolling Navigation

- **Target Object**: `oBackground` & `oFutaMatingPress`
- **Target Event**: `Create (0)` (oBackground) & `Draw (0)` (oFutaMatingPress)
- **Anchor**: `func_scan_custom_backgrounds()` and bedroom menu drawing block

Implements manifest-based bedroom discovery and adds touch-specific interactions to the bedroom selection UI, including swipe-drag scrolling and enlarged clickable navigation arrows.

```gml
function func_scan_custom_backgrounds()
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
}
// ...
    if (mouse_check_button_pressed(mb_left) && _bg_panel_hover)
    {
        bg_menu_dragging = true;
        bg_menu_click_ok = true;
        bg_menu_drag_start_y = mouse_y;
        bg_menu_drag_start_scroll = bg_menu.scroll;
    }
    if (bg_menu_dragging)
    {
        if (mouse_check_button(mb_left))
        {
            if (abs(bg_menu_drag_start_y - mouse_y) > 6)
            {
                bg_menu_click_ok = false;
            }
            var _bg_delta = (bg_menu_drag_start_y - mouse_y) / 12;
            bg_menu.scroll = clamp(bg_menu_drag_start_scroll + _bg_delta, 0, _bg_max_scroll);
        }
// ...
    bg_menu.scroll = clamp(bg_menu.scroll, 0, _bg_max_scroll);
    bg_menu.scroll_lerp = lerp(bg_menu.scroll_lerp, bg_menu.scroll, 0.35);
```

Source: bundle_src/gml_Object_oBackground_Create_0.gml, func_scan_custom_backgrounds; bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml; fallback core/gml_patches/patch_background_code/new_bg_scan.gml


### 5. [DR-05] [Deeproom Mobile Custom] Sandboxed Storage & Persistent Session Redirection (setting_data.sav)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)` & `Draw (0)`
- **Anchor**: Inside `func_save_settings()` and startup settings loader in `oFutaMatingPress` `Create (0)`

Settings are persisted into `setting_data.sav` via standard ini functions. On startup, `setting_data.sav` is read to restore favorites maps (`global.favs_futa`, `global.favs_wife`), options flags such as `selector_favs_only`, and hyper size toggles (`tc_hyper`). In addition to ini persistence, toggling `tc_hyper` writes or deletes a marker file at `game_save_id + "hyper_sizes.on"`.

```gml
global.favs_wife = ds_map_create();
selector_favs_only = false;
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
    if (ini_key_exists("options", "hyper_sizes"))
    {
        tc_hyper = bool(ini_read_real("options", "hyper_sizes", false));
    }
    if (ini_key_exists("options", "selector_favs_only"))
    {
        selector_favs_only = bool(ini_read_real("options", "selector_favs_only", false));
    }
    ini_close();
}
```

Saving persists options and feature settings to `setting_data.sav`:

```gml
function func_save_settings()
{
    ini_open("setting_data.sav");
    ini_write_real("options", "master_audio", global.vol_master);
    ini_write_real("options", "sound_sfx", global.vol_sfx);
    ini_write_real("options", "voice_fx", global.vol_voice);
    ini_write_real("options", "ambient_vol", global.vol_ambient);
    ini_write_real("options", "master_audio_toggle", global.audio_master_on);
    ini_write_real("options", "sound_sfx_toggle", global.audio_sfx_on);
    ini_write_real("options", "voice_fx_toggle", global.audio_voice_on);
    ini_write_real("options", "xray", xray);
    ini_write_real("types", "vagina_toggle", futa_pussy_toggle);
    ini_write_real("mechanics", "knotting_toggle", knotting_toggle);
    ini_write_real("mechanics", "knotted_max_time", knotted_max_time);
    ini_write_real("mechanics", "womb_inflation_toggle", womb_inflation_toggle);
    ini_write_real("mechanics", "womb_inflation_scale", womb_inflation_scale);
    ini_write_real("mechanics", "slip_toggle", slip_toggle);
    ini_write_real("mechanics", "slip_chance", slip_chance);
    ini_write_real("mechanics", "reenter_toggle", reenter_toggle);
    ini_write_real("mechanics", "reenter_max_timer", reenter_max_timer);
    ini_write_real("mechanics", "condom_break_toggle", condom_break_toggle);
    ini_write_real("mechanics", "condom_break_threshold", condom_break_threshold);
    ini_write_real("values", "stroke_depth", stroke_depth);
    ini_write_real("values", "stroke_speed", stroke_speed);
    ini_write_real("values", "pump_delay", pump_delay);
// ...
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, func_save_settings

---

## Part 2: Character Rigging, Scaling & Pill Protections

### 6. [DR-06] [Deeproom Mobile Custom] Universal Origin-Based Model Scaling & Multi-Frame Slicing

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)` & `Draw (0)`
- **Anchor**: `func_load_custom_futa` and `func_load_custom_wife`

In `func_load_custom_futa`, custom character assets initialize default origin coordinates for sprites (`sprite_origin_x = 80`, `sprite_origin_y = 84`, `mp_origin_x = 80`, `mp_origin_y = 84`). During drawing, custom sprite scaling is computed against character dimensions and applied across mating press and condom sprites:

```gml
        if (insert == false)
        {
            var scale_x = (image_xscale + top_breath) * top_penis_width * custom_mating_press_scale;
            var scale_y = (image_yscale - top_breath) * top_penis_length * custom_mating_press_scale;
            var scale_c_x = (image_xscale + top_breath) * top_penis_width * custom_condom_scale;
            var scale_c_y = (image_yscale - top_breath) * top_penis_length * custom_condom_scale;
            var draw_y_base = y - (thrust * 32);
```

Portraits are scaled to a 128 px frame (`... _scale = 128 / width`) in every portrait loader (lover and partner, standard and modern; 2026-11-17). In `func_load_custom_spouse`, for example, `custom_wife_portrait_scale = 128 / _wpw`, while custom mating press sheets are loaded with specified frame counts and origins:

```gml
    var f_mate = string(arg0) + "/custom_mating_press.png";
    if (file_exists(f_mate))
    {
        if (sprite_exists(legacy_custom_wife_mating_press))
        {
            sprite_delete(legacy_custom_wife_mating_press);
        }
        legacy_custom_wife_mating_press = sprite_add(f_mate, 4, false, false, mp_origin_x, mp_origin_y);
    }
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, func_load_custom_spouse

---

### 7. [DR-07] [Deeproom Mobile Custom] Pill Custom Asset Protections, Sheath Fallbacks & Proportional Condom Scaling

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)` & `Draw (0)`
- **Anchor**: `func_get_futa_frame` switch statements in `Create (0)`

When rendering custom sprite layers, missing pill art frames fall back to default layers to prevent crashes and invisible anatomy. For position 0, shaft requests return frame 7 as a safe fallback layer, and condoms return frame 0. For position 1 (cowgirl), hands check against the sprite subimage count (`sprite_get_number(legacy_custom_cowgirl) > 6`) before returning frame index 6 or 4, and shaft falls back to frame 2:

```gml
                case "shaft":
                    comment = "layer 1 (base/sheath) - safely falls back to base custom asset if pill art missing";
                    return 7;
                case "glans":
                    comment = "layer 2 (tip/extension)";
                    if (penis_type_index == 0)
                    {
                        comment = "human glans";
                        return -1;
                    }
                    if (penis_type_index == 1)
                    {
                        comment = "horse shaft";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knot has no 2nd layer";
                        return -1;
                    }
                    if (penis_type_index == 3)
                    {
                        comment = "knotted horse has no 2nd layer";
                        return -1;
                    }
                    return -1;
                case "condom":
                    comment = "condom - safely falls back to base condom frame 0 if pill art missing";
                    return 0;
                case "broken":
                    comment = "broken condom - safely falls back to frame 0 if pill art missing";
                    return 0;
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, func_get_futa_frame

---

### 8. [DR-08] [Deeproom Mobile Custom] Ovulation Disentanglement from Wife Climax (func_wife_climax)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: `gml_patches/patch_create_code/old_climax_ov.gml`

In desktop code, `func_wife_climax()` directly invoked `func_ovulate()` during climax loops. Under mobile custom scripts, `func_wife_climax()` manages climax state, climax timers, and jiggle triggers without calling `func_ovulate()`. Ovulation is handled separately via `func_ovulate()`, keyboard shortcuts (`ord("O")`), and milestone pill events in `Draw (0)`:

```gml
function func_wife_climax()
{
    var was_active = wife_climax;
    wife_climax = true;
    wife_climax_timer = 480 + (60 * wife_climax_stage);
    if (!was_active)
    {
        wife_climax_stage = 1;
    }
    else
    {
        wife_climax_stage = min(wife_climax_stage + 1, wife_climax_stage_max);
    }
    switch (wife_climax_stage)
    {
        case 1:
            bottom_ass_jiggle = 0.3;
            body_jiggle = 0.01;
            break;
        case 2:
            bottom_ass_jiggle = 0.35;
// ...
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, func_wife_climax; core/gml_patches/patch_create_code/old_climax_ov.gml

---

### 9. [DR-09] [Deeproom Mobile Custom] Custom Spouse X-Ray Origin Coordinates Initialization

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Inside `func_load_custom_spouse(arg0)`

When loading custom spouse sprites, the X-ray origin defaults to coordinates (80, 84). The loader opens `custom_data.spouse` only, as in the native game; the modern `.wife` loader reads only the flat `[sprite]` keys. (A fallback between the two layouts was tried on 2026-11-17 and reverted: packs are tuned against the native game.) The origin is read from `[xray] origin_x/y`, then `[sprite] xray_x/y`, and clamped to 40..120. If `custom_xray.png` is found, the 4-frame sprite is added and its offset recalculated if the sprite width differs from the 160px baseline.

**Measured origin (2026-11-17).** Install option "Align X-ray overlays" (asked right after the duplicate prompt, default Yes; `--no-xray-origins` turns it off). When on, for Deeproom builds the patcher measures frame 0 of every partner and lover X-ray strip and compares it with the pack's own mating-press sprite (partner: frame 0; lover: frame 7). Across the library the X-ray centre lines up with the sprite centre (p10..p90 within 0.5 px), and the bottom edge of a partner X-ray sits +70 px below the origin. An adjustment is made only when the library measure and the pack's own sprite agree that the X-ray is off, in the same direction (x by more than 4 px; y by more than 6 px, partners only: the lover's vertical reference is unreliable, so lover heights are never changed). Rows and columns with fewer than 3 opaque pixels are ignored (stray pixels), and a frame 0 wider than 110 px or taller than 170 px is not treated as a plain X-ray overlay. The result is written as `[xray] mobile_origin_x/y` into the APK copy of the descriptor (`wbp/descriptors.py`, `_deeproom_xray_origins`; Pillow is used when installed, otherwise the standard-library PNG reader; the pack's files are not changed; a list is written to `output/<apk>_xray_origins.txt`). All four X-ray loaders (spouse, modern wife, legacy lover, modern lover) then use that origin exactly (no clamp, no rescale), and Draw (0) no longer resets a partner X-ray that has one (`wife_xray_fixed_offset`). Typical cause: the X-ray origin was copied from the mating-press origin (100-120 for wide mating-press canvases) although the X-ray strips use standard 160 px frames, which drew the X-ray 20-40 px off-centre. On the 2026-11 library: 45 partners and 2 lovers adjusted.

```gml
    var f_xray = string(arg0) + "/custom_xray.png";
    if (file_exists(f_xray))
    {
        if (sprite_exists(legacy_custom_wife_xray))
        {
            sprite_delete(legacy_custom_wife_xray);
        }
        legacy_custom_wife_xray = sprite_add(f_xray, 4, false, false, xray_origin_x, xray_origin_y);
        wife_xray_fixed_offset = _lcwx_fixed;
        var _lcwx_w = _lcwx_fixed ? 160 : sprite_get_width(legacy_custom_wife_xray);
        if (_lcwx_w > 0 && _lcwx_w != 160)
        {
            var _lcwx_sc = 160 / _lcwx_w;
            sprite_set_offset(legacy_custom_wife_xray, xray_origin_x / _lcwx_sc, xray_origin_y / _lcwx_sc);
        }
        _lcwx_w = _lcwx_fixed ? 160 : sprite_get_width(legacy_custom_wife_xray);
        if (_lcwx_w > 0 && _lcwx_w != 160)
        {
            var _lcwx_sc = 160 / _lcwx_w;
            sprite_set_offset(legacy_custom_wife_xray, xray_origin_x / _lcwx_sc, xray_origin_y / _lcwx_sc);
        }
    }
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, func_load_custom_spouse

---

## Part 3: Rendering Pipeline Stability & Fallbacks


### 10. [DR-10] [Deeproom Mobile Custom] Lover-Wife Portrait Fallback Parity Architecture

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: `gml_patches/patch_draw_code/new_lpe.gml`

#### Technical Problem
If custom portrait art is uninitialized or absent, drawing unconditionally using custom sprite IDs results in runner crashes. Conversely, substituting custom IDs unconditionally without gating causes custom assets to render incorrectly.

```gml
    face_x += ((face_x_set - face_x) * 0.1);
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
    draw_sprite_ext(_lover_base_portrait, 1, portrait_x, portrait_y + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);
```
Source: core/gml_patches/patch_draw_code/new_lpe.gml

---

### 11. [DR-11] [Deeproom Mobile Custom] Strict Custom Selection (`enforce_strict_custom_selection`)

- **Target Object**: Patcher Engine
- **Target Event**: Patch Injection
- **Anchor**: `enforce_strict_custom_selection:old_w_eyes`

Applies GML replacements for strict custom selection, including replacing `old_w_eyes` with `new_w_eyes` and replacing custom panel button handlers.

```python
    old_w_bangs9 = gml("enforce_strict_custom_selection/old_w_bangs9")
    code = guarded_replace(code, old_w_bangs9, new_w_bangs9, "enforce_strict_custom_selection:old_w_bangs9")

    old_w_eyes = gml("enforce_strict_custom_selection/old_w_eyes")
    new_w_eyes = gml("enforce_strict_custom_selection/new_w_eyes")
    code = guarded_replace(code, old_w_eyes, new_w_eyes, "enforce_strict_custom_selection:old_w_eyes")

    code = guarded_replace(code, old_swap_click, new_swap_click, "enforce_strict_custom_selection:old_swap_click")
```
Source: wbp/gml_patches.py, enforce_strict_custom_selection

---

### 12. [DR-12] [Deeproom Mobile Custom] Clean Portrait Unloading & Cross-Character Isolation

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: `func_load_custom_futa`

When loading custom futa data in `func_load_custom_futa`, portrait file paths are checked sequentially. Since 2026-11-17 every lover and partner loader first clears BOTH portrait slots of its role (`custom_portrait` and `legacy_custom_portrait`; for partners `custom_wife_portrait` and `legacy_custom_wife_portrait`; sprites with an index of 189 or less are built-in and never deleted), loads the new portrait with 10 or 17 frames chosen by `func_portrait_frames` (whichever divides the width) and sets the portrait scale to 128 / frame width. Before this, switching from a standard-name lover to a modern one left the old portrait on screen.

```gml
            f_port = string(arg0) + "/custom_portrait.png";
            if (!file_exists(f_port))
            {
                if (file_exists(string(arg0) + "/custom_futa_portrait_0.png")) f_port = string(arg0) + "/custom_futa_portrait_0.png";
                else if (file_exists(string(arg0) + "/custom_wife_portrait_0.png")) f_port = string(arg0) + "/custom_wife_portrait_0.png";
                else if (file_exists(string(arg0) + "/custom_portrait1.png")) f_port = string(arg0) + "/custom_portrait1.png";
                else if (file_exists(string(arg0) + "/custom_portraitt.png")) f_port = string(arg0) + "/custom_portraitt.png";
                else if (file_exists(string(arg0) + "/custom_portrait-1.4.png")) f_port = string(arg0) + "/custom_portrait-1.4.png";
                else if (file_exists(string(arg0) + "/custom_portrait_alt.png")) f_port = string(arg0) + "/custom_portrait_alt.png";
            }
            if (file_exists(f_port))
            {
                if (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait > 189)
                {
                    sprite_delete(legacy_custom_portrait);
                }
                legacy_custom_portrait = sprite_add(f_port, 10, false, false, portrait_origin_x, portrait_origin_y);
```
Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, func_load_custom_futa

---

### 13. [DR-13] [Deeproom Mobile Custom] Dynamic Composite Thumbnail Slicing & Frame Fallback

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Lazy thumbnail loader injection

Selector thumbnails are loaded through `func_futa_selector_portrait()` / `func_wife_selector_portrait()`: they pick the portrait file the character's loader will use and take 10 or 17 frames, whichever divides the strip width (`func_portrait_frames`), so high-res (256 px) portraits and 10-frame strips saved under `_0` names both load.

```gml
                    else if (file_exists(_pb))
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
```
Source: core/gml_patches/inject_lazy_thumbnails_into_draw/new_loader.gml

---

## Part 4: Touch UI, Character Selection Screen (CSS) & Navigation

### 14. [DR-14] [Deeproom Mobile Custom] CSS Auto-Scroll & Centering Math (Jump-to-Selected)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: `gml_patches/inject_virtual_keyboard_and_search/new_max_scroll_def.gml`

Calculates horizontal scroll bounds and snaps `scroll` and `scroll_lerp` to center the currently selected partner index upon initializing the selection UI.

```gml
var _max_scroll = max(0, _total_content_w - room_width);
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
    }
```
Source: core/gml_patches/inject_virtual_keyboard_and_search/new_max_scroll_def.gml

---

### 15. [DR-15] [Deeproom Mobile Custom] CSS Equipped Partner Pulsing Gold Border & Title Star

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: the `_is_equipped` check in the selector draw code

Draws a semi-transparent pulsing gold rectangle and star title header for the currently equipped partner item within the selector card rendering loop.

```gml
            var _is_equipped = _ci == ((selector_mode == 0) ? custom_futa_index : custom_wife_index);
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
            draw_rectangle(_cx - 2, _cy - 2, _cx + _cell_w + 2, _cy + _cell_h + 2, true);
```
Source: bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml, oFutaMatingPress Draw

---

### 16. [DR-16] [Deeproom Mobile Custom] CSS Card Click Isolation & Star Hitbox Disentanglement (!_star_hover)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Line ~21330

Evaluates point collisions for the favorite star toggle button separately. Tapping the star modifies `setting_data.sav` favorite keys and calls `mouse_clear(mb_left)`. Card selection requires `!_star_hover` to ensure clicks do not overlap.

```gml
            // Individual Thumbnail Favorite Star Button
            var _star_w = 18;
            var _star_h = 18;
            var _star_x1 = (_cx + _cell_w) - _star_w;
            var _star_y1 = _cy;
            var _star_x2 = _cx + _cell_w;
            var _star_y2 = _cy + _star_h;

            var _fav_map = (selector_mode == 0) ? global.favs_futa : global.favs_wife;
            var _is_fav = ds_map_exists(_fav_map, _fname);

            var _star_hover = point_in_rectangle(mouse_x, mouse_y, _star_x1 - 2, _star_y1 - 2, _star_x2 + 2, _star_y2 + 2);
            if (os_type == os_android || os_type == os_ios)
            {
                if (point_in_rectangle(device_mouse_x(0), device_mouse_y(0), _star_x1 - 2, _star_y1 - 2, _star_x2 + 2, _star_y2 + 2))
                {
                    _star_hover = true;
                }
            }

            draw_set_alpha(1);
            draw_set_color(_is_fav ? make_color_rgb(255, 215, 0) : make_color_rgb(35, 35, 35));
            draw_rectangle(_star_x1, _star_y1, _star_x2, _star_y2, false);
            draw_set_color(_is_fav ? c_white : make_color_rgb(140, 140, 140));
            draw_rectangle(_star_x1, _star_y1, _star_x2, _star_y2, true);

            var _bcx = (_star_x1 + _star_x2) * 0.5;
            var _bcy = (_star_y1 + _star_y2) * 0.5;
            draw_set_color(_is_fav ? c_black : make_color_rgb(200, 200, 200));
            draw_line_width(_bcx - 5, _bcy, _bcx + 5, _bcy, 2);
            draw_line_width(_bcx, _bcy - 5, _bcx, _bcy + 5, 2);
            draw_line_width(_bcx - 3, _bcy - 3, _bcx + 3, _bcy + 3, 2);
            draw_line_width(_bcx - 3, _bcy + 3, _bcx + 3, _bcy - 3, 2);

            if ((mouse_check_button_pressed(mb_left) || device_mouse_check_button_pressed(0, mb_left)) && _star_hover)
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
                mouse_clear(mb_left);
            }

            comment = "hover detection — highlight and record name";
            var _cell_hover = point_in_rectangle(mouse_x, mouse_y, _cx, _cy, _cx + _cell_w, _cy + _cell_h) && !_star_hover;
```
Source: bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml, oFutaMatingPress Draw


### 17. [DR-17] [Deeproom Mobile Custom] CSS Geometric Vector Star Badges, Silent Click Isolation & Dynamic Filter

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Thumbnail card drawing loop (`// Individual Thumbnail Favorite Star Button`)

Draws 8-point geometric vector star badges on thumbnails without font atlas dependencies. Tapping the star executes `mouse_clear(mb_left);` to consume the click, toggling favorites silently without equipping the character or closing the menu:

The code is the same as the excerpt in section 16 (star badges).

Source: bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml

---

### 18. [DR-18] [Deeproom Mobile Custom] CSS Modal Input Priority & Background Suppression

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Step (0)` & `Draw (0)`
- **Anchor**: Top of Step event and hover checks

When `futa_selector_open` or `mob_expanded` is active, background panels and interactions are suppressed to provide exclusive input capture to the character grid modal:

```gml
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
// ...
if (title == false && start_timer < 1 && futa_selector_open == false)
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
}
```

Source: bundle_src/gml_Object_oFutaMatingPress_Step_0.gml

---

### 19. [DR-19] [Deeproom Mobile Custom] CSS Header Layout: Left Search Bar, Right-Side [FAV: ALL/ON] Toggle & Locked Close Button

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Character selector header bar (`comment = "search bar";`)

Establishes header geometry with the search bar spanning the top, the favorite filter toggle button on the right, and dark overlay styling behind the interface:

```gml
    comment = "search bar";
    var _bar_x1 = 20;
    var _bar_x2 = room_width - 120;
    var _bar_y1 = 4;
    var _bar_y2 = 20;

    var _fav_btn_x1 = room_width - 114;
    var _fav_btn_x2 = room_width - 48;
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
            mouse_clear(mb_left);
        }
// ...
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
    draw_set_valign(fa_top);
```

Source: bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml

---

### 20. [DR-20] [Deeproom Mobile Custom] CSS Mobile Virtual Keyboard Trigger & Auto-Dismissal

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Search input loop

Controls mobile software keyboard activation and dismissal when focusing or leaving the CSS search bar:

```gml
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
```

Source: bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml


### 21. [DR-21] [Deeproom Mobile Custom] Mutual Panel Exclusivity & Radar Chart Isolation

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Stat graph rendering condition

This logic controls the visibility of the radar stat chart based on the state of several menu toggles. The chart is rendered only when the new lover menu is open and the new wife menu, options menu, orgasm state, and character selector are all closed. It sets the drawing font to a small size before proceeding with the chart visualization under these specific mutual exclusivity conditions.

```gml
    comment = "hover chart - shown when hovering OR when menu is open";
    if (newlover_menu_toggle == true && newwife_menu_toggle == false && options_toggle == false && orgasm == false && futa_selector_open == false)
    {
        draw_set_font(fntFontSmall);
```

Source: `bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml`

---

### 22. [DR-22] [Deeproom Mobile Custom] Climax Screen Protection & Panel Auto-Closing

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Overlay panel auto-closing handler

This block functions as a master reset for UI state variables to ensure that overlay panels do not overlap with the climax screen or other expanded views. It forcibly sets numerous toggle variables, such as menu visibility, radial menu states, and interaction flags like headpats or boob presses, to false. The code checks for the existence of the `mob_expanded` variable and clears the menus if that state or a climax event is active.

```gml
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
```

Source: `bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml`

---

### 23. [DR-23] [Deeproom Mobile Custom] Translucent Mobile Overlay with Strict Modal Z-Ordering

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Mobile touch overlay root block

This section handles the initialization and spatial positioning of the mobile touch overlay when the character selector is closed. It resets the jump state and favorites filter flags while calculating a horizontal offset for Floating Action Buttons (FAB) based on a percentage of the room width. These checks ensure that the mobile-specific UI elements are correctly anchored and reset when the user exits the selection modal.

```gml
if (futa_selector_open == false)
{
    _sel_jump_done = false;
    selector_favs_only = false;
}
if (futa_selector_open == false)
{
    var _fab_x_offset = round(room_width * 0.12);
```

Source: `bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml`

---

### 24. [DR-24] [Deeproom Mobile Custom] Single-Trigger Overlay Action Execution

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Quick bar touch handler

This handler processes touch input for a quick-action bar by checking if a button is hovered and a mobile touch press is detected. Depending on the specific key code assigned to the button, it executes functions for resetting sex stats, triggering a wife climax, or starting an ovulation event. For the "N" key code, it closes the lover and wife menus while simultaneously triggering the orgasm state and simulating a physical key press.

```gml
            draw_set_color(c_white);
            draw_text((_qbx1 + _qbx2) * 0.5, (_qby1 + _qby2) * 0.5, _qb_lbl);
            if (_qb_over && _mob_touch_p)
            {
                if (_qb_key == 82)
                {
                    func_reset_sex_stats();
                    sex_progress = 0;
                    edge_charge = 0;
                }
                else if (_qb_key == 67)
                {
                    func_wife_climax();
                }
                else if (_qb_key == 79)
                {
                    func_ovulate();
                }
                else if (_qb_key == 78)
                {
                    newlover_menu_toggle = false;
                    newwife_menu_toggle = false;
                    orgasm_start = true;
                    orgasm = true;
                    keyboard_key_press(ord("N"));
                    mob_release_key = 78;
                }
                else
```

Source: `bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml`

---

### 25. [DR-25] [Deeproom Mobile Custom] Uninterrupted 8-Mechanic Gameplay Interaction & Disclaimer One-Time Gate

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Hotkey title toggle and peek mode handler

This logic manages the transition between gameplay and the title or disclaimer screens using hotkey triggers. It sets the title state to active, hides the disclaimer, and captures the current background ID while setting flags for peek mode and re-entry logic. If the title is already active from a hotkey, the code reverses the process to return to gameplay by disabling the title state and resetting peek mode variables.

```gml
    {
        title = true;
        disclaimer = false;
        title_timer = 0;
        title_from_hotkey = true;
        title_background_id = oBackground.background_id;
        peek_closed_during_play = true;
        if (insert == false && orgasm == false && !(hearts_toggle == true && loads >= max_loads))
        {
            reenter_flag = true;
            reenter_timer = 0;
        }
        muffle_pending = true;
        muffle_delay_timer = 47;
    }
    else if (title == true && title_from_hotkey == true)
    {
        title = false;
        peek_mode = 0;
        prev_peek_mode = -1;
```

Source: `bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml`

---

### 26. [DR-26] [Deeproom Mobile Custom] Neutralization of Rickroll Fake Crash Loop in Step_0

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Step (0)`
- **Anchor**: `Rick_Astley` string check

The Python patcher neutralizes the Rickroll fake crash loop in `Step_0` by searching for pattern matches containing `global.rg_chosen_pill == "Rick_Astley"` and replacing the block with a comment line.

Source: `wbp/gml_patches.py patch_step_code`

---

## Part 5: Android Platform & ToyBridge Foundation Systems

### 27. [TB-01] [ToyBridge] Synthetic Right-Click & Touch Hold Engine

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Long-press touch detection loop

This code implements a long-press detection system by measuring the duration a user holds a touch point without moving more than 18 pixels. If the touch is held for 22 frames while in manual mode and not in a restricted state like an orgasm or title screen, it activates the radial menu. It sets the `radial_menu_open` flag to true and records that the menu was opened via a right-click equivalent hold.

```gml
        if (_mob_touch_d)
        {
            if (point_distance(_mob_tx, _mob_ty, mob_lp_start_x, mob_lp_start_y) < 18)
            {
                mob_lp_timer += 1;
                if (mob_lp_timer == 22 && !radial_menu_open && title == false && orgasm == false && variable_instance_exists(id, "manual_mode") && manual_mode > 0)
                {
                    radial_menu_open = true;
                    radial_sub_menu = "";
                    radial_rc_held = true;
                }
            }
            else
            {
                mob_lp_timer = 0;
            }
        }
```

Source: `bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml`


### 28. [TB-02] [ToyBridge] Single-Column Vertical Menu Layout

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: NEW LOVER and NEW WIFE menu draw loops

This loop renders a vertical, single-column menu for selecting character types like Human, Devil, or Slime. It draws a semi-transparent background sprite and iterates through an array of items, calculating the vertical position and hover state for each row. The code also handles disabled states for specific items based on whether custom sprites are loaded and detects left-mouse clicks to close the menu or select an entry.

```gml
        var header_col_nl = newlover_dragging ? 65535 : 16777215;
        draw_sprite_ext(sButtonBack, 1, menu_cx, menu_cy, menu_w_px / 16, total_h / 16, 0, header_col_nl, 0.8);
        comment = "title";
        draw_set_color(header_col_nl);
        draw_text_transformed(menu_cx, menu_start_y + menu_pad, "LOVER", 0.65, 0.65, 0);
        draw_set_font(fntFontSmall);
        draw_set_color(_close_nl_hover ? make_color_rgb(255, 120, 120) : c_white);
        draw_text_transformed(_close_nl_x, _close_nl_y, "X", 0.6, 0.6, 0);
        draw_set_font(fntFontBig);
        if (_close_nl_hover && mouse_check_button_pressed(mb_left))
        {
            newlover_menu_toggle = false;
        }
        comment = "all items in single column";
        var menu_items = ["HUMAN", "DEVIL", "FURRY", "SLIME", "ANDROID", "ALIEN", "CLOWN", "BUNNY", "CUSTOM", "RANDOM"];
        var menu_base_cols = [make_color_rgb(255, 204, 170), make_color_rgb(204, 119, 255), make_color_rgb(204, 153, 85), make_color_rgb(119, 238, 119), make_color_rgb(187, 187, 187), make_color_rgb(100, 220, 130), make_color_rgb(255, 80, 80), make_color_rgb(180, 180, 180), make_color_rgb(255, 255, 197), make_color_rgb(255, 255, 197)];
        var items_start_y = menu_start_y + menu_pad + title_h + 4;
        draw_set_valign(fa_middle);
        for (var mi = 0; mi < 10; mi++)
        {
            var item_cy = items_start_y + (item_h * 0.5) + (mi * item_step);
            var item_hover_0 = 0;
            var item_hover_1 = 0;
            var item_hover_2 = 0;
            var item_hover_3 = 0;
            var item_disabled = mi == 7 && custom_sprite_loaded == false;
            var item_col = item_disabled ? 8421504 : menu_base_cols[mi];
            if (mi == 4 || mi == 8 || mi == 9)
            {
                item_hover_0 = point_in_rectangle(mouse_x, mouse_y, (menu_cx - (col_w_px * 0.5)) + menu_pad, (item_cy - (item_h * 0.5)) + 2.5, (menu_cx + (col_w_px * 0.5)) - menu_pad, (item_cy + (item_h * 0.5)) - 2.5);
```

Source: bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml, NEW LOVER menu draw loop

---

### 29. [TB-03] [ToyBridge] Drag-to-Scroll Accumulator (menu_scroll_update)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: `function menu_scroll_update(arg0, arg1, arg2)`

This function manages menu scrolling through both the mouse wheel and a touch-drag accumulator. It tracks the vertical displacement of the mouse between frames and adds it to an accumulation variable, adjusting the scroll index once the movement exceeds a defined row height. The resulting scroll value is clamped using a median function to ensure it stays within the bounds of the total item count and the visible area.

```gml
function menu_scroll_update(arg0, arg1, arg2)
{
    if (mouse_wheel_up() || mouse_wheel_down())
    {
        arg0.scroll += mouse_wheel_down() - mouse_wheel_up();
        arg0.scroll = median(arg0.scroll, 0, max(0, arg1 - arg2));
    }
    if (mouse_check_button(mb_left))
    {
        if (!variable_struct_exists(arg0, "touch_drag_last_y"))
        {
            arg0.touch_drag_last_y = mouse_y;
            arg0.touch_drag_accum = 0;
        }
        else
        {
            arg0.touch_drag_accum += mouse_y - arg0.touch_drag_last_y;
            arg0.touch_drag_last_y = mouse_y;
            var _row_height = 64;
            while (arg0.touch_drag_accum <= -_row_height)
            {
                arg0.scroll -= 1;
                arg0.touch_drag_accum += _row_height;
            }
            while (arg0.touch_drag_accum >= _row_height)
            {
                arg0.scroll += 1;
                arg0.touch_drag_accum -= _row_height;
            }
            arg0.scroll = median(arg0.scroll, 0, max(0, arg1 - arg2));
        }
    }
}
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, menu_scroll_update

---

### 30. [TB-04] [ToyBridge] SIZES Options Page Hyper-Scale Toggle (TouchHyperToggle)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Options page 2 (SIZES), under wife sliders

This logic renders a toggle button on the SIZES options page to enable or disable "HYPER" scaling. It draws a background sprite with variable transparency based on hover and toggle states and displays the current status as "HYPER: ON" or "HYPER: OFF." When the button is clicked and the title screen is not active, it flips the boolean state of the `tc_hyper` variable.

```gml
var _tc_hx = options_x + 58;
var _tc_hy = options_y + 12;
var _tc_hh = point_in_rectangle(mouse_x, mouse_y, _tc_hx - 28, _tc_hy + 1, _tc_hx + 28, _tc_hy + 9);
draw_sprite_ext(sButtonBack, 1, _tc_hx, _tc_hy + 5, 4.2, 1, 0, tc_hyper ? 65535 : 16777215, 0.5 + (0.5 * _tc_hh) + (0.5 * tc_hyper));
draw_set_halign(1);
draw_set_valign(0);
draw_text_ext_transformed(_tc_hx, _tc_hy, tc_hyper ? "HYPER: ON" : "HYPER: OFF", 12, 100, 0.5, 0.5, 0);
if (mouse_check_button_pressed(1) && _tc_hh && title == false)
{
    tc_hyper = !tc_hyper;
// ...
```

Source: core/gml_patches/apply_hyper_sizes/hyper_toggle.gml, hyper_toggle

---

### 31. [TB-05] [ToyBridge] On-Device Mod Sharing Activity (wbmods.PhoneImportActivity)

- **Target Platform**: Android Dalvik / ART Runtime (`classes2.dex`)
- **Package**: `wbmods.PhoneImportActivity`

`patch_game_apk()` edits `AndroidManifest.xml` via `AxmlEditor.add_import_activity()` to register `wbmods.PhoneImportActivity` for handling VIEW, SEND, and SEND_MULTIPLE intents targeting `.zip` and `.json` mod archives. If registered successfully, `phone_import.dex` is added to the target APK as the next free `classesN.dex` (usually `classes2.dex`) at root as the next available DEX file (`classes2.dex`). Incoming archives are stored in the app-private `files/phone_inbox/` directory.

**Phone mods in the game (2026-11-17).** The title screen's ADD MOD dialog (`Other_63`) takes an `https://` link (downloaded with `http_get_file`) or a local `.zip` / `.json` path (`/sdcard/`, `/storage/emulated/0/`, `file://`), which is copied into `phone_inbox/`; the inbox check in Draw (0) imports it like a shared file. On Android, `tc_norm_path` keeps paths inside `game_save_id` absolute (`tc_is_save_path`), and `tc_ff_first` lists such folders with `file_find_first` instead of a `_manifest.txt`, because folders the game creates have no manifest. Each import also appends the packs, bedrooms, texture packs, voice packs and dialogue files it creates to `<save>/phone_mods_registry.txt` (`pm_registry_add`); the startup reload, the REMOVE MOD list and the VOICES list read it (`pm_registry_read`) besides scanning, and removing a mod drops it (`pm_registry_remove`). Remove searches up to 8 folder levels below `phone_mods/`; all imports create `phone_voices/` before copying a voice pack. Checked by `tests/test_phone_mods_registry.py`; not device-tested.

Source: wbp/apk.py, patch_game_apk

---

### 32. [DR-27] [Deeproom Mobile Custom] Pure Python Binary AXML Editor & APK DEX Bundling

- **Target File**: `AndroidManifest.xml` (inside APK root)
- **Module**: `AxmlEditor` in `wbp/axml.py`

`AxmlEditor` directly parses and manipulates binary XML chunks in `AndroidManifest.xml` during APK patching without invoking external tools like `apktool` or `aapt2`. It appends required string pool entries, updates the resource map, injects `<activity>` and `<intent-filter>` elements into the `<application>` node, and verifies registration using `has_import_activity()`. Upon success, `patch_game_apk()` bundles `phone_import.dex` as the next available `classesN.dex` file in the APK package.

Source: wbp/axml.py, AxmlEditor; wbp/apk.py, patch_game_apk

---

### 33. [TB-06] [ToyBridge] Optional External UDP Telemetry Broadcast (buttplug_socket)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)` & `Draw (0)`
- **Anchor**: UDP telemetry broadcast snippet

This script handles the transmission of gameplay data to an external destination using the UDP protocol. It checks if a valid network socket exists and uses a timer to limit broadcasts to approximately every 33 milliseconds. When triggered, it packages variables including thrust speed, thrust strength, and orgasm status into a string buffer and sends it to `127.0.0.1` on the port in `buttplug_port` (45735 by default), so a receiver on the same device (a bridge app) can read it.

```gml
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
```

Source: core/gml_patches/patch_draw_code/bp_draw.gml, bp_draw


### 34. [DR-28] [Deeproom Mobile Custom] Pre-Flight Mod Pack Classification & Quarantine Architecture

- **Target Module**: `wbp/packs.py`, `wbp/apk.py`, `wbp/cli.py`
- **Functions**: `classify_custom_pack()`, `plan_pack_skips()`, `write_skip_report()`, `move_skipped_packs()`

Evaluates custom pack folders before ingestion to prevent APK build aborts or runtime crashes:
0. Besides the checks below, `missing_sprites()` skips packs lacking a sprite the target engine needs, and for Deeproom `deeproom_strip_problems()` skips packs whose strips do not divide into the frame count their loader uses (or partners without a portrait).
1. Numbered-Alt Check: Flags packs containing filenames matching `^custom_data_\d+\.(futa|spouse)$` (case-insensitive) as non-portable.
2. Recognized Data File Check: Validates presence of recognized descriptor files (`custom_data.futa`, `custom_data.wife`, `custom_data.spouse`, `custom_data.bedroom`).
3. Skipping: Non-portable packs and duplicate entries are excluded from APK asset ingestion and manifests. A skip report is generated in Markdown and JSON formats (`_skipped_packs.md` / `_skipped_packs.json` or `_validation.md` / `_validation.json` during dry runs).
4. Quarantine: When `--move-skipped` is enabled, skipped packs are moved to a new timestamped folder under `output/quarantine/<YYYYMMDD-HHMMSS>/<kind>/<cat>/`. Existing destination files are not overwritten or deleted; collision handling appends incremental numeric suffixes (`_<k>`).

Source: wbp/packs.py, classify_custom_pack, plan_pack_skips, move_skipped_packs; wbp/apk.py, patch_game_apk

---

### 35. [DR-29] [Deeproom Mobile Custom] Universal ModRoom & Legacy Spouse Format Detection (check_custom_wife)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: `function check_custom_wife(arg0)`

#### Architectural Role
Normalizes paths and evaluates sprite file existence for spouse positions across both ModRoom conventions (`custom_wife_*_0.png`) and legacy Wife's Bedroom naming (`custom_mating_press.png`, `custom_reverse_cowgirl.png`, `custom_portrait.png`). Returns a struct indicating file presence for mating press, cowgirl, reverse cowgirl, and portrait:

```gml
function check_custom_wife(arg0)
{
    arg0 = tc_norm_path(arg0);
    check_struct = {};
    check_struct.custom_wife_mating_press = file_exists(string(arg0) + "/custom_wife_mating_press_0.png") || file_exists(string(arg0) + "/custom_mating_press.png");
    check_struct.custom_wife_cowgirl = file_exists(string(arg0) + "/custom_wife_cowgirl_0.png") || file_exists(string(arg0) + "/custom_reverse_cowgirl.png");
    check_struct.custom_wife_reverse_cowgirl = file_exists(string(arg0) + "/custom_wife_reverse_cowgirl_0.png") || file_exists(string(arg0) + "/custom_reverse_cowgirl.png");
    check_struct.custom_wife_portrait = file_exists(string(arg0) + "/custom_wife_portrait_0.png") || file_exists(string(arg0) + "/custom_portrait.png");
    return check_struct;
}
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, check_custom_wife

---

### 36. [DR-30] [Deeproom Mobile Custom] Mobile Audio & Voice Pack Streaming (custom_music & custom_sounds)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: `function func_radio_scan()`

#### Architectural Role
Dynamic scanning of custom background audio tracks using `func_radio_scan()`. On Android and iOS, directory scans read relative to `"custom_music"`, whereas desktop platforms query through `tc_wd + "/custom_music"`. Found files populate `radio_track_list` using virtual directory traversal via `tc_ff_first` and `tc_ff_next`:

```gml
function func_radio_scan()
{
    ds_list_clear(radio_track_list);
    var _base = (os_type == os_android || os_type == os_ios) ? "custom_music" : (tc_wd + "/custom_music");
    var _f = tc_ff_first(_base + "/*.ogg", 0);
    while (_f != "")
    {
        var _full = _base + "/" + _f;
        if (file_exists(_full))
        {
            ds_list_add(radio_track_list, _full);
        }
        _f = tc_ff_next();
    }
    tc_ff_close();
    radio_has_tracks = ds_list_size(radio_track_list) > 0;
}
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, func_radio_scan; core/gml_patches/patch_create_code/new_radio.gml, func_radio_scan

---

### 37. [DR-31] [Deeproom Mobile Custom] Anatomy Sprite & Boob Box Pre-Flight Safety Guards

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)` & `Draw (0)`
- **Anchor**: Variable initialization in `Create (0)` and event start in `Draw (0)`

#### Architectural Role
Initializes `boob_box` in `Create (0)` and guards against undefined variable errors at the start of `Draw (0)` prior to UI, interaction, and rendering passes:

```gml
// Create_0 variable initialization
mob_lp_start_x = 0;
mob_lp_start_y = 0;

boob_box = false;
```

```gml
// Draw_0 guard check
if (!variable_instance_exists(id, "boob_box"))
{
    boob_box = false;
}
if (!variable_instance_exists(id, "boob_box"))
{
    boob_box = false;
}
tc_typing = false;
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml; bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml

---

### 38. [DR-32] [Deeproom Mobile Custom] Screen Boundary Clamping for Mobile Dragging Menus

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Menu drag update blocks for `newlover_dragging` and `newwife_dragging`

#### Architectural Role
Clamps mobile dragging panels within horizontal and vertical room bounds during active drag interactions to prevent panel headers and content from being dragged off-screen:

```gml
        if (newlover_dragging)
        {
            newlover_menu_cx = clamp(mouse_x + drag_offset_x, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
// ...
        if (newwife_dragging)
        {
            newwife_menu_x = clamp(mouse_x + drag_offset_x, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
            newwife_menu_y = clamp(mouse_y + drag_offset_y, (total_h * 0.5) + 4, room_height - ((total_h * 0.5) + 4));
            menu_cx = newwife_menu_x;
            menu_cy = newwife_menu_y;
            menu_start_y = menu_cy - (total_h * 0.5);
            menu_end_y = menu_cy + (total_h * 0.5);
```

Source: bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml, menu drag blocks

---

### 39. [DR-33] [Deeproom Mobile Custom] Dual-Engine Bytecode Ingestion, v1.5 Manifest Streaming & Unified Alphabetical Ingestion

- **Target Module**: `wbp/apk.py`, `wbp/engines.py`, `wbp/detect.py`
- **Functions**: `patch_game_apk()`, `detect_mod_engine_version()`, `find_matching_base_apk()`, `gather_custom_assets()`, `generate_manifest_data()`

#### Architectural Role
Supports targeted bytecode patching and custom asset ingestion matching the identified engine architecture:
1. **Version Detection**: `detect_mod_engine_version()` evaluates mod layouts, distinguishing between `1.4`, `1.5`, and `modroom33` target structures. Base APK templates are dynamically resolved by `find_matching_base_apk()` based on requested version candidates.
2. **Deeproom / ModRoom Pipeline**: Ingests scripts via UndertaleModCli code entry replacements (`mobile_engine.bundle`). Dynamically generates variable shields (`generate_dynamic_variable_shield`) by disassembling bytecode in `gml_Object_oFutaMatingPress_Create_0` to safeguard host engine variables against uninitialized access.
3. **Wife's Bedroom v1.5 Pipeline**: Injects v1.5 native bytecode patches via `patch_v15_engine_bytecode()`. Implements buffer manifest streaming, updates `custom_lover_folders`, `custom_partner_folders`, and `custom_bedroom_folders`, and restores session selections during boot.
4. **Path & Asset Resolution**: Looks up keystores, tools, input APKs, and mod folders relative to the patcher directory, maintaining isolation from fixed machine paths.

Source: wbp/apk.py, patch_game_apk; wbp/engines.py, patch_v15_engine_bytecode; wbp/detect.py, detect_mod_engine_version, find_matching_base_apk

---

### 40. [DR-34] [Deeproom Mobile Custom] Multi-Input Ingestion, Extended CLI, Modular Install Modes & Dynamic Naming

- **Target Module**: `wbp/cli.py`, `wbp/detect.py`
- **Functions**: `main()`, `prompt_install_options()`, `clean_output_dir()`

#### Architectural Role
Provides input aggregation, command-line arguments, interactive feature selection, and output artifact naming:

1. **Input Ingestion & Packaging**:
   - **Candidate Selection**: When multiple candidate archives or folders exist in `input/`, an interactive selector allows selecting a package, defaulting to item 1 under non-interactive `-y` mode.
   - **Multi-Input Ingestion**: Discovers APKs, directories, and ZIP archives passed as arguments or located in `input/`. Multiple loose pack directories containing custom descriptor files are ingested together.
   - **Archive Extraction**: Compressed archives are extracted to temporary directories prior to scanning and asset aggregation.

2. **CLI Automation & Utility Flags**:
   - `--clean`: Purges existing `.apk` and `.idsig` files from `output/` via `clean_output_dir()` prior to building. Base backups (`.bak`) are preserved.
   - `--fast`: Sets asset packaging mode to store uncompressed files directly (`zipfile.ZIP_STORED`).
   - `--validate-only`: Runs pack classification, skip checks, and manifest generation without building or writing modified APK binaries.
   - `-y`, `--yes`: Runs unattended builds using default options.
   - Additional flags: toy telemetry (`--toy-*`, `--hmv-mode`, `--export-toy-tools`), `--move-skipped`, `--approximate` (lossy format bridging), `--no-quarantine-duplicates` and `--no-xray-origins`.

3. **Modular Install Modes**:
   - `prompt_install_options()` presents default full installations or custom granular component toggling (`quarantine_duplicates`, `xray_origins` ("Align X-ray overlays", asked right after the duplicate question, default Yes, `--no-xray-origins`), `core_manifest`, `scaling`, `stability`, `climax_and_panels`, `css_and_favs`, `phone_import`, `toy_telemetry`, `clean_output`, `fast_packaging`).

4. **Dynamic Output APK Naming**:
   - Derives the output filename from the mod archive, folder name, or base APK stem, appending `_modded.apk` unless an explicit output target is specified via `-o` / `--output`.
   - Replaces reserved filesystem characters (`[\/:*?"<>|]`) with underscores.

Source: wbp/cli.py, prompt_install_options, main; wbp/detect.py, clean_output_dir

---

## Part 6: Version 1.1 Multi-Engine Architecture, Universal Asset Bridging & Companion Converters


### 41. [DR-35] [Tri-Engine] Multi-Version Engine Detection, Bytecode Matrix & Native Streaming

- **Target Module**: `wbp/detect.py`, `wbp/apk.py`, `wbp/cli.py`
- **Functions**: `detect_mod_engine_version()`, `find_matching_base_apk()`, `patch_game_apk()`

#### Architectural Role & Engine Detection Logic
Engine detection inspects mod folder contents and `data.win` binary signatures to categorize mods into targeted runtime pipelines (`"1.4"`, `"1.5"`, or `"modroom33"`). When compiling a v1.5 mod target, `find_matching_base_apk()` searches for v1.5 APK templates in the input and patcher directories.

```python
def detect_mod_engine_version(folder: Path) -> str:
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
```
Source: `wbp/detect.py`, `detect_mod_engine_version`

---

### 42. [DR-36] [Tri-Engine] Universal Bi-Directional Filename Bridge & Forward Deduplication

- **Target Module**: `wbp/packs.py`, `wbp/apk.py`, `wbp/cli.py`
- **Functions**: `gather_custom_assets()`, `generate_manifest_data()`

#### Architectural Role & Asset Processing
Assets are gathered across custom character and sound directories, scanning for custom characters, sounds, music, and dialogues. When target engine formats differ between ModRoom (`_0.png`) and standard names, filename bridging renames or converts sprite strips and generates `_manifest.txt` indices.

```python
            LOGGER.log(f"Scanning '{Path(source_folder).name}' for custom characters, sounds, music, and dialogues...")
            custom_assets = gather_custom_assets(source_folder, is_v15=(target_engine == "v15"), target_arch=target_engine, skip_dirs=skip_dirs, approximate=bool(opts.get("approximate")))
            LOGGER.log(f"Discovered {len(custom_assets)} custom asset file(s).")
```

Besides renaming, the bridge converts frame counts. `convert_bridged_strip()` in `wbp/packs.py` uses the shared `wbp/wbconv.py`: when a strip's real width matches the source format, it is padded with blank frames to the target format's frame count (lossless). Conversions that drop frames, and every portrait change, happen only with `--approximate`; otherwise the strip is renamed unchanged and listed in `<apk>_format_notes.txt`. The partner X-ray crop (4 to 3 frames) drops a frame, so it is done only with `--approximate`, and only for packs that carry a `custom_data.wife`; otherwise the X-ray keeps its 4 frames. A partner pack with only a reverse cowgirl gets that strip copied, padded to 11 frames, as the forward cowgirl.

Source: `wbp/apk.py`, `patch_game_apk`

---

### 43. [DR-37] [GameMaker GML] Bytecode Compatibility & Control-Character Escaping

- **Target Module**: `wbp/gml_patches.py`, `wbp/apk.py`
- **Functions**: `patch_create_code()`, `patch_draw_code()`

#### Architectural Role & Injection Safety
Dynamic code replacements inject GML logic into `gml_Object_oFutaMatingPress_Create_0` and `gml_Object_oFutaMatingPress_Draw_0`. Safe variable initialization prevents uninitialized variable access and input state leaks.

```gml
// Master Modal Supremacy & Total Input Isolation Shield
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
```
Source: `wbp/gml_patches.py`, `patch_draw_code`

---

### 44. [DR-38] [Universal Shield] Universal Wife Recognition Shield & Cowgirl Fallback Architecture

- **Target Modules**: `core/gml_patches/patch_mr33_engine_bytecode/old_check_wife.gml`, `bundle_src/gml_Object_oFutaMatingPress_Create_0.gml`
- **Anchor**: `function check_custom_wife(arg0)`

#### Architectural Role & Custom Wife Validation
ModRoom v3.3 checks custom partner folder contents using `check_custom_wife`. The runtime evaluates the presence of partner assets before adding valid folders to `custom_wives_folder` and initializing partner portraits.

```gml
function check_custom_wife(arg0)
{
    check_struct = {};
    check_struct.custom_data = file_exists(string(arg0) + "/custom_data.wife");
    check_struct.custom_wife_mating_press = file_exists(string(arg0) + "/custom_wife_mating_press_0.png");
    check_struct.custom_wife_cowgirl = file_exists(string(arg0) + "/custom_wife_cowgirl_0.png");
    check_struct.custom_wife_reverse_cowgirl = file_exists(string(arg0) + "/custom_wife_reverse_cowgirl_0.png");
    check_struct.custom_wife_portrait = file_exists(string(arg0) + "/custom_wife_portrait_0.png");
    return check_struct;
}
```

The converters and the patcher apply the same fallback: a partner pack that has only a reverse cowgirl strip receives a copy of it, padded to ModRoom's 11 forward-cowgirl frames, so ModRoom's admission rule (mating press, forward cowgirl, reverse cowgirl) is met and the pack is not purged.

Source: `core/gml_patches/patch_mr33_engine_bytecode/old_check_wife.gml`, `check_custom_wife`

---

### 45. [DR-39] [Sprite Integrity] ModRoom v3.3 Frame Divisor Slicing Math & Transparent Padding Cure

- **Target Modules**: `bundle_src/gml_Object_oFutaMatingPress_Create_0.gml`, `bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml`
- **Functions**: `func_load_custom_futa()`, `func_load_custom_wife()`

#### Architectural Role & Custom Character Loading
Custom characters and wives are loaded dynamically at runtime via `func_load_custom_futa` and `func_load_custom_wife`. The loaders inspect descriptor headers such as `custom_data.spouse` or `custom_mating_press.png` to apply appropriate sprite origins, offsets, and stat configurations.

```gml
function func_load_custom_wife(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    if (file_exists(string(arg0) + "/custom_data.spouse") || file_exists(string(arg0) + "/custom_mating_press.png") || !file_exists(string(arg0) + "/custom_wife_mating_press_0.png"))
    {
        func_load_custom_spouse(arg0);
        exit;
    }
    legacy_custom_wife_toggle = false;
    var sprite_origin_x = 80;
    var sprite_origin_y = 84;
    var portrait_origin_x = 64;
    var portrait_origin_y = 64;
    comment = "memory bleed guard";
    custom_bottom_boob_size = 1;
    custom_bottom_ass_size = 1;
    custom_partner_male = false;
    custom_contraceptive_pill = false;
    custom_ovulation_pill = false;
    custom_eggxcelent_pill = false;
    custom_greedy_womb_pill = false;
    custom_dialogue_set_bottom = -1;
    custom_wife_size_response = 1;
    custom_wife_intensity_response = 1;
    custom_wife_cum_response = 1;
```

The frame counts per format live in `FRAMES` in `wbp/wbconv.py` (lover standard 10/9/5/3 for portrait, mating press, cowgirl and X-ray against 17/24/19/18 modern; partner standard 10/4/5/6/5/4 for portrait, mating press, reverse cowgirl, forward cowgirl, deepthroat and X-ray against 17/5/10/11/5/3 modern). A portrait frame is 128 px wide and every other frame 160 px.

Source: `bundle_src/gml_Object_oFutaMatingPress_Create_0.gml`, `func_load_custom_wife`

---

### 46. [DR-40] [Pack Discovery] Universal Recursive Mod Pack Discovery Engine

- **Target Module**: `wbp/packs.py`
- **Functions**: `classify_custom_pack()`

#### Architectural Role & Mod Pack Classification
Custom character and room folders are classified via `classify_custom_pack()` to ensure compatibility before assets are ingested or compiled into target builds.

```python
def classify_custom_pack(folder: Path, modern_ok: bool = False):
    """
    Classifies one character/bedroom folder as portable (simple convention - can just be
    copied into the other mod system's expected layout) or not (uses the older numbered
    convention or lacks recognized custom_data files, which causes crashes on mobile).
    Exact classification logic from ToyBridgeLauncher's GamePatcher / ToyLauncher.

    modern_ok: the target engine reads the ModRoom naming natively (ModRoom V3.3 and Deeproom: custom_futa_*_0.png,
    custom_wife_*_0.png and the _alt_N variants), so those names are not a reason to skip a pack. Wife's Bedroom v1.5
    cannot read them and keeps the old rule.
    """
    try:
        entries = list(folder.iterdir())
    except OSError as e:
        return False, f"Couldn't read folder: {e}", None

    names = [e.name for e in entries]
```
Source: `wbp/packs.py`, `classify_custom_pack`


### 47. [DR-41] [Companion Converters] Bi-Directional Dual-Architecture Converter Suite

- **Tools**:
  - `Modded_to_WB_1.5_Converter_v1.1` (Launcher: `Convert_to_WB_1.5.bat`)
  - `WB_1.5_to_Modded_Converter_v1.1` (Launcher: `Convert_from_WB_1.5.bat`)

#### Architectural Role
Provides lossless cross-engine mod portability between legacy split-category engines (ModRoom v3.3, Deeproom 4.0, Vanilla v1.2) and modern Steam-standard unified `custom/` architecture (Wife's Bedroom v1.5):

1. **Modded to WB 1.5 Converter**:
   - Consolidates `custom_futas/`, `custom_wives/`, `custom_bedrooms/`, and loose root folders into unified `custom/<character_name>/`.
   - Normalizes all character files to standard names (`custom_portrait.png`, `custom_data.spouse`).
   - Resolves Steam Workshop numeric IDs to human-readable names via INI `[info] name=`.
   - Generates clean v1.5 `_manifest.txt` indexing files.
2. **WB_1.5_to_Modded_Converter**:
   - Deconstructs unified `custom/` directories into split categories (`custom_futas/`, `custom_wives/`, `custom_bedrooms/`).
   - Defaults to **Both Architectures** side-by-side:
     - **`output/ModRoom_Mods/`**: Legacy `_0.png` naming with distortion unlinking and Universal Wife Shield for ModRoom v3.3.
     - **`output/Deeproom_Mods/`**: Standard canonical unnumbered naming with Universal Wife Shield for Deeproom 4.0.

Both converters share `wbconv.py` (four identical copies: both converters, the patcher's `wbp/` and the Custom Studio's `backend/`; `tools/sync_wbconv.py` keeps them equal). They convert in a staging folder and write the destination only when a pack was produced, support `--dry-run` and write a per-pack conversion report. Lossy frame conversion needs `--approximate`; the partner X-ray crop applies only to packs with a `custom_data.wife`; a 10-frame partner portrait is kept as authored for ModRoom. Pack folder names pass through `safe_dirname()`, which removes control and invisible characters and stacked combining marks, replaces characters Windows forbids and avoids device names, and a name the operating system still refuses falls back to the pack's folder name and then to a hash.

Source: converters/Modded_to_WB_1.5.py; converters/WB_1.5_to_Modded.py

---

## Part 7: ToyBridge 1.5.3 Full Suite, Bluetooth Latency & Synthesis Architecture

---

### 48. [TB-07] [ToyBridge 1.5.3] Standalone Direct WebSocket Client (--toy-mode direct, Other_68)

- **Target Objects**: `oFutaMatingPress`
- **Events**: `Create_0`, `Draw_0`, `Other_68` (Async Networking)
- **Anchor**: `thrust_time = 0;` (Create_0), `thrust_prev = thrust;` (Draw_0)

#### Architectural Role
Eliminates the requirement for background bridges on mobile. The patcher injects a native WebSocket client into GameMaker's networking event to communicate directly with Intiface Central. These edits replace the functionality previously provided by the external `GamePatcher.exe` tool.

```gml
if (ds_map_find_value(async_load, "id") == tb_sock)
{
    var _tb_type = ds_map_find_value(async_load, "type");
    if (_tb_type == 4)
    {
        if (ds_map_find_value(async_load, "succeeded"))
        {
            tb_state = 2;
            tb_retry_at = current_time + 6000;
            tb_last_rx = current_time;
            buffer_seek(tb_buf, buffer_seek_start, 0);
            buffer_write(tb_buf, buffer_text, "GET / HTTP/1.1\r\nHost: 127.0.0.1:" + string(tb_port) + "\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: V2lmZXNCZWRyb29tVG95IQ==\r\nSec-WebSocket-Version: 13\r\n\r\n");
            network_send_raw(tb_sock, tb_buf, buffer_tell(tb_buf));
        }
        else
        {
            tb_state = 0;
        }
    }
// ...
```

- **Actuator Support**: Emits JSON `ScalarCmd` and `LinearCmd` messages mapped via thrust velocity and position.
- **Safety Mechanism**: Game-loop hooks automatically fire `StopAllDevices` if the connection fails or the actuator state needs to be reset.

Source: core/gml_patches/native_toy/direct_other68.gml; wbp/toy_native.py

---

### 49. [TB-08] [ToyBridge 1.5.3] In-Engine Lead Prediction & Bluetooth Latency Compensation (0-500ms)

- **Target Object**: `oFutaMatingPress`
- **Event**: `Draw_0`
- **Setting**: `tb_lead`, read from the `lead` key in the `[toy]` section of `toy_direct.ini`

#### Architectural Role
Bluetooth toys typically exhibit motor inertia and transmission lag. The patcher lets the user choose a latency value during the build and writes it to `assets/toy_direct.ini` in the APK. At startup the in-game client reads `profile`, `port` and `lead` from the packaged copy (`working_directory`) and then from the save folder, where a value the player changed (the profile tap) takes precedence. Every 66 ms the client sends the stroke position it expects `tb_lead` milliseconds from now: the current position plus the speed measured since the previous send times the lead, with the lead capped at half the stroke period (`min(tb_lead, _tb_dur * 0.5)`) and the result clamped to the profile's range. The vibration level is not predicted. With a lead of 0 the current position is sent.

```gml
                var _tb_pos_src = clamp(thrust, 0, 1);
                if (tb_lead > 0)
                {
                    var _tb_dt = _tb_now - tb_pos_at;
                    if (tb_pos_at > 0 && _tb_dt > 0 && _tb_dt < 400)
                    {
                        var _tb_ext = min(tb_lead, _tb_dur * 0.5);
                        _tb_pos_src = clamp(_tb_pos_src + (((_tb_pos_src - tb_pos_prev) / _tb_dt) * _tb_ext), 0, 1);
                    }
                }
                tb_pos_prev = clamp(thrust, 0, 1);
                tb_pos_at = _tb_now;
                var _tb_pos = _tb_lo + (_tb_pos_src * (_tb_hi - _tb_lo));
```

```python
    # 3. Bluetooth Latency Compensation (Delay Fix)
    print("\nSelect Bluetooth Latency Compensation (Delay Fix):")
    print("  Common Bluetooth devices respond ~100-300ms late.")
      print("  [1] 0 ms (Off / Wired / Low Latency)")
// ...
    print("  [5] 200 ms (RECOMMENDED for Bluetooth toys e.g. Lovense / Handy) [DEFAULT]")
// ...
    lead_map = {"1": 0, "2": 50, "3": 100, "4": 150, "5": 200, "6": 250, "7": 300, "8": 400, "9": 500}
    chosen_lead = lead_map[lead_choice]
```

- **Presets**: `0 ms (Off)`, `50 ms`, `100 ms`, `150 ms`, `200 ms (Recommended)`, `250 ms`, `300 ms`, `400 ms`, `500 ms`.
- **Pre-seeding**: The selected value is written to `assets/toy_direct.ini` inside the APK by `apply_toybridge_suite_patches`.

Source: core/gml_patches/native_toy/direct_create.gml, direct_draw_top.gml; wbp/cli.py; wbp/toy.py apply_toybridge_suite_patches

---

### 50. [TB-09] [ToyBridge 1.5.3] Anti-Hang Connection Retry Limiter & Title Screen Touch Controls

- **Target Modules**: `wbp/toy.py`, `oFutaMatingPress_Draw_0`
- **Variables**: `tb_retry_count`, `tb_retry_max`, `tb_paused_retry`

#### Architectural Role
Prevents infinite background polling and battery drain on mobile devices when the telemetry server is offline by implementing an in-game retry limit and interactive UI.

1. **CLI Setup Probe**: Executes a non-blocking TCP socket connect on port 12345 using `probe_intiface_server` with a 0.4s timeout.
2. **In-Engine Retry Limiting**: Caps connection attempts at a configurable maximum (default 5). If reached, it sets `tb_paused_retry = true` and stops further attempts.
3. **Interactive Title HUD**: The HUD displays `TOY: NOT FOUND (TAP RETRY)` when paused. Tapping the HUD resets `tb_retry_count` and `tb_paused_retry` to trigger a reconnect.

```python
def probe_intiface_server(host="127.0.0.1", port=12345, max_attempts=3, timeout=0.4):
    """Checks if an Intiface Central server is active on host:port, limiting to max_attempts without hanging."""
    for attempt in range(1, max_attempts + 1):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
    return False
```

Source: wbp/toy.py probe_intiface_server; wbp/toy.py apply_toybridge_suite_patches

---

### 51. [TB-10] [ToyBridge 1.5.3] HMV Audio Beat-Sync Mode & Interactive Bed Speakers

- **Target Object**: `oFutaMatingPress`, `oBackground`
- **Events**: `Create_0`, `Draw_0`, `Other_68`, `Step_0`
- **Flag**: `--hmv-mode`

#### Architectural Role
Integrates HMV (Heavy Music Video) mode by patching the game's background rendering and thrust variables to respond to external UDP data. This replaces the edits previously made by `GamePatcher.exe`.

- **Background Sync**: Replaces `c_white` (or `16777215`) in `oBackground_Draw_0` with `oFutaMatingPress.hmv_background_color` to tint the room in sync with audio rhythm.
- **UDP Listener**: Injects an Other_68 networking handler to receive beat-tracking and spectrum data on Port 45736, driving thrust velocity and color dynamics.
- **Companion Tools**: The companion apps (`ToyLauncher.exe`, `HmvLive.exe`) are not shipped; `--export-toy-tools` copies them from `tools/toybridge/` or an installed ToyBridge launcher to the output folder when they are present.

```python
def hmv_background(text):
    """Tint the background with the beat colour: every white colour argument in oBackground Draw_0."""
    if HMV_COLOR in text:
        return text
    return text.replace("c_white", HMV_COLOR).replace("16777215", HMV_COLOR)
```

The companion PC apps for the bridge and beat-sync modes (`ToyLauncher.exe`, `ButtplugBridge.exe`, `HmvLive.exe`) are not shipped with the patcher; `--export-toy-tools` copies them from `tools/toybridge/` or from an installed ToyBridge launcher when one is present.

Source: wbp/toy_native.py; wbp/toy.py export_toybridge_companion_suite

---

### 52. [TB-11] [ToyBridge 1.5.3] Descriptor [info] Section Synthesis & Safe Fallback Architecture

- **Target Modules**: `converters/Modded_to_WB_1.5.py`
- **Function**: `normalize_pack_slug()`

#### Architectural Role
Ensures character and bedroom descriptor files strictly comply with the Wife's Bedroom v1.5 specification during conversion. It sanitizes metadata to prevent UI issues and ensures standard category placement.

- **Name Sanitization**: Strips community tags and trailing copy indicators (e.g. `_copy`, `_old`, `_backup`) from folder names using regex to create clean comparison slugs.
- **Slug Normalization**: Replaces illegal characters and whitespace with underscores.
- **Category Enforcement**: The `detect_intrinsic_category` function inspects files like `custom_data.spouse` or `background.png` to ensure packs are routed to the correct `custom_wives`, `custom_futas`, or `custom_bedrooms` directory regardless of their original source folder.

```python
def normalize_pack_slug(name: str) -> str:
    """Normalizes a folder or character name into a clean comparison slug (Tier 1)."""
    s = re.sub(r"\((COMM|3\.5|1\.4|V1|BS|WIP|Nude|Clothed|Rework)\)", "", name, flags=re.I)
    s = re.sub(r"(\s*-\s*copy(\s*\(\d+\))?|\s*\(\d+\)|_copy|_old|_backup)$", "", s, flags=re.I)
    return re.sub(r"\s+", "_", s)
```

Source: converters/Modded_to_WB_1.5.py; converters/WB_1.5_to_Modded.py

---

## Part 8: v1.1 Pack Pipeline, Engine Safety & Asset Features

### 53. [DR-42] [3-Tier Duplicate Pipeline] Automated Cross-Folder & Multi-Content Duplicate Detection Architecture

- **Target Modules**: `wbp/packs.py`, `converters/Modded_to_WB_1.5.py`
- **Function**: `plan_duplicate_skips()`
- **Flags**: `--move-skipped`

#### Architectural Role
Prevents asset collisions and character clobbering by identifying duplicate packs across different source folders or categories before they are added to the APK.

#### Pipeline Tiers
1. **Tier 1 (Name & Slug Match)**: Uses `normalize_pack_slug()` to strip tags and read internal `[info] name=` from descriptors.
2. **Tier 2 (Asset Fingerprinting)**: Not explicitly detailed in snippet logic but identified as part of the `plan_duplicate_skips` role for fingerprinting core sprites.
3. **Tier 3 (Canonical Selection & Scoring)**: 
   - **Category Affinity**: `detect_intrinsic_category()` inspects headers and sprites. A pack receives a scoring bonus if located in its matching folder (e.g., a wife pack in `custom_wives/`).
   - **Quarantine**: If multiple versions of a pack exist, the highest-scoring version is kept. Others are skipped and recorded in `skipped_packs.md`. If `--move-skipped` is enabled, duplicates are moved to a quarantine folder.

```python
def detect_intrinsic_category(pack_path: Path) -> str:
    """Inspects internal files to determine the true intrinsic category of a pack."""
    try:
        files = {f.name.lower() for f in pack_path.iterdir() if f.is_file()}
        if any(w in files for w in ["custom_data.spouse", "custom_data.wife", "custom_wife.ini"]):
            return "custom_wives"
        if any(w in files for w in ["custom_data.futa", "custom_futa.ini"]):
            return "custom_futas"
        if any(w in files for w in ["custom_data.bedroom", "background.png", "custom_background.png"]):
            return "custom_bedrooms"
// ...
```

Source: wbp/packs.py; converters/Modded_to_WB_1.5.py


### 54. [DR-43] [Deeproom 4.0.3 Kiwami Engine Architecture] Container Traversal, Manifest Dual-Routing & INI Specification

- **Target Modules**: `WB_Mobile_Patcher.py`, `converters/wbconv.py`, `bundle_src/gml_Object_oDialogueManager_Create_0.gml`
- **Applicable Engines**: Deeproom 4.0.3 Kiwami, ModRoom v3.3, Wife's Bedroom v1.5

#### Architectural Overview
Deeproom 4.0.3 Kiwami introduces a centralized `custom_stuff/` root directory container for user content. The engine performs dual-routing, checking for manifest files in both the legacy root and the `custom_stuff/` subdirectory to maintain backward compatibility.

```gml
dialogue_files = [];
var _dlg_pack_dir = (file_exists("custom_stuff/dialogue_packs/_manifest.txt") || file_exists("assets/custom_stuff/dialogue_packs/_manifest.txt")) ? "custom_stuff/dialogue_packs" : "dialogue_packs";
var file_name = tc_ff_first(_dlg_pack_dir + "/*.json", 0);
// ...
var _dlg_cust_dir = (file_exists("custom_stuff/dialogue/_manifest.txt") || file_exists("assets/custom_stuff/dialogue/_manifest.txt")) ? "custom_stuff/dialogue" : "dialogue";
```

#### INI Specification & Stats
The engine and converters handle expanded descriptors for gameplay mechanics including condom offsets, stamina, and pill effects:
- `[condom]`: `condom_y_mpress` and `condom_y_cowgirls`.
- `[stats]`: `stamina`, `max_pumps`, `cumshot_mult`, `pump_delay_min`, `pump_delay_max`.
- `[pills]`: `mega_sperm_pill`, `extra_thick_pill`, `diphallia_pill`, `stamina_pill`, `leaky_pill`, `hyper_breeding_pill`.

```python
    ini.add("condom", "condom_y_mpress", val("sprite", "condom_y", "78.000000"))
    ini.add("condom", "condom_y_cowgirls", val("sprite", "standing_condom_y", "0.000000"))
    ini.add("gender", "is_male", '"0"')
```

Source: bundle_src/gml_Object_oDialogueManager_Create_0.gml; converters/wbconv.py

---

### 55. [DR-44] [Dynamic Variable Safety Shield] Live Bytecode Extraction & Guard Synthesis Architecture

- **Target Modules**: `wbp/apk.py`, `wbp/engines.py`
- **Applicable Engines**: Deeproom 4.0.3 Kiwami, ModRoom v3.3
- **Anchor**: `generate_dynamic_variable_shield(utmt_exe, target_data_file, bundle_create_code)`

#### Architectural Role
The Dynamic Variable Safety Shield prevents crashes when a pre-compiled engine bundle is injected into an upstream APK that contains newer instance variables not initialized in the bundle's `Create_0` script. It uses `UndertaleModCli.exe` to disassemble the host bytecode and identify missing assignments.

#### Execution Pipeline
1. **Live Disassembly Analysis**: Executes a C# script to disassemble the host `gml_Object_oFutaMatingPress_Create_0` and extract variable names assigned via `pop.v.* builtin` opcodes, filtering out common built-ins.
2. **Synthesis**: Computes the difference between host variables and bundle variables.
3. **Injection**: Appends a guard block to the GML before compilation.

```python
c0_key = "gml_Object_oFutaMatingPress_Create_0.gml"
if c0_key in payload:
    shield_code, shielded_vars = generate_dynamic_variable_shield(utmt_cli, tmp_droid, payload[c0_key])
    if shielded_vars:
        LOGGER.log(f"Dynamic Variable Shield: Safeguarded {len(shielded_vars)} host variable(s) against uninitialized access ({', '.join(shielded_vars[:5])}{'...' if len(shielded_vars) > 5 else ''})!", prefix="[+]")
        payload[c0_key] += "\n" + shield_code
```

Source: wbp/apk.py, generate_dynamic_variable_shield; wbp/engines.py, generate_dynamic_variable_shield

---

### 56. [DR-45] [In-Game Portrait Interaction Offsets] Real-Time Calibration & Dual-Character Memory Parity

- **Target Modules**: `bundle_src/gml_Object_oFutaMatingPress_Create_0.gml`, `Draw_0.gml`
- **Applicable Engines**: Deeproom 4.0.3 Kiwami, ModRoom v3.3, Wife's Bedroom v1.5

#### Implementation Architecture
The system enables per-character coordinate calibration for interaction hitboxes (kiss, boobs, headpat) and condom positioning. It includes a calibration mode where a semi-transparent green rectangle follows the touch position to set new offsets.

```gml
    else if (wife_offset_panel_mode == "boobs")
    {
        var _wbb_x1 = (portrait_x - 34) + custom_boob_x_offset + (mouse_x - (((portrait_x - 34) + custom_boob_x_offset + (portrait_x + 41 + custom_boob_x_offset)) / 2));
        var _wbb_y1 = portrait_y + 20 + custom_boob_y_offset + (mouse_y - ((portrait_y + 20 + custom_boob_y_offset + (portrait_y + 52 + custom_boob_y_offset)) / 2));
        var _wbb_x2 = _wbb_x1 + 75;
        var _wbb_y2 = _wbb_y1 + 32;
        draw_set_alpha(0.5);
        draw_set_color(c_green);
        draw_rectangle(_wbb_x1, _wbb_y1, _wbb_x2, _wbb_y2, false);
        draw_set_alpha(1);
    }
```

#### Persistence
Offsets are committed to the respective character data files via specialized saving functions that modify the INI contents directly.

```gml
function func_save_futa_condom_offset(arg0, arg1)
{
    var _folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
    var _path = string(_folder) + "/custom_data.futa";
    // ...
    var _new_line = arg0 + " = \"" + string(arg1) + "\"";
```

Source: bundle_src/gml_Object_oFutaMatingPress_Draw_0.gml; bundle_src/gml_Object_oFutaMatingPress_Create_0.gml

---

### 57. [DR-46] [Custom SFX Engine] Dynamic Audio Loading, Randomization & Mod Overrides

- **Target Modules**: `bundle_src/gml_Object_oFutaMatingPress_Create_0.gml`, `gml_patches/patch_create_code/new_gca.gml`
- **Applicable Engines**: Deeproom 4.0.3 Kiwami, ModRoom v3.3

#### Audio Dispatchers & Randomization
The engine tracks randomization indices to prevent consecutive sound repetition for insertions and pullouts. It uses `func_get_custom_audio` to scan mod directories for `.ogg` overrides.

```gml
function func_play_condom_break_sfx()
{
    if (top_sprite == sFutaMatingPressClown)
    {
        oAudioManager.play_sfx(sndGoofyWompWomp, 0, 1, 0.8);
        return true;
    }
    if (ds_list_size(custom_condom_break_list) > 0)
    {
        var _c_snd = ds_list_find_value(custom_condom_break_list, irandom(ds_list_size(custom_condom_break_list) - 1));
        if (_c_snd != undefined && audio_exists(_c_snd))
        {
            oAudioManager.play_sfx(_c_snd, 0, 1, 1);
            return true;
        }
    }
```

#### Mod Pack Audio Overrides
During character load, the engine scans specifically for `sfx/insert`, `insert`, `sfx/pullout`, `pullout`, `sfx/condom_break`, and `condom_break` subfolders within the character pack.

```gml
    func_get_custom_audio(custom_insert_list, string(arg0) + "/sfx/insert");
    func_get_custom_audio(custom_insert_list, string(arg0) + "/insert");
    func_get_custom_audio(custom_pullout_list, string(arg0) + "/sfx/pullout");
    func_get_custom_audio(custom_pullout_list, string(arg0) + "/pullout");
```

Source: bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, func_play_condom_break_sfx; core/gml_patches/patch_create_code/new_gca.gml, func_get_custom_audio

---

### 58. [DR-47] [Sprite Strip Padding Protection] ModRoom v3.3 Slicing Math Parity

- **Target Modules**: `bundle_src/gml_Object_oFutaMatingPress_Create_0.gml`, `bundle_src/gml_Object_oBackground_Create_0.gml`
- **Applicable Engines**: ModRoom v3.3, Deeproom 4.0 Standard

#### Mathematical Formulation & Technical Problem
Engines such as ModRoom v3.3 and Deeproom 4.0 use `sprite_add` with fixed frame counts for different categories (e.g., 4 frames for backgrounds, 17 frames for certain futa portraits). If a sprite strip contains an incorrect frame count, GameMaker's uniform slicing leads to visual tearing or offset frames.

#### Implementation
The code ensures that `sprite_add` is called with the specific frame counts expected by the engine's rendering logic. Asset loading scripts specify the subimage count to ensure correct internal slicing of the texture strip.

```gml
    var _spr = sprite_add(_bg_path, 4, false, false, 220, 128);
    if (!sprite_exists(_spr) || sprite_get_number(_spr) < 4)
    {
        if (sprite_exists(_spr))
        {
            sprite_delete(_spr);
        }
        return false;
    }
```

Source: bundle_src/gml_Object_oBackground_Create_0.gml; bundle_src/gml_Object_oFutaMatingPress_Create_0.gml


### 59. [DR-48] [Universal Loose-Portrait Resolution] Auto-Aliasing Variant Filenames

- **Target Modules**: `wbp/packs.py`, `wbp/apk.py`
- **Applicable Engines**: All Supported Engines

#### Architectural Role
Community modders frequently author portraits with variant naming conventions instead of exact standard names. If unhandled, character selector cards display blank white silhouettes. The patcher resolves these by aliasing discovered variant filenames to the standard targets expected by the engine loaders.

#### Aliasing Pipeline
1. The patcher checks for primary portrait targets (`custom_portrait.png`, `custom_futa_portrait_0.png`, `custom_wife_portrait_0.png`).
2. If missing, it scans the pack directory for files matching variant patterns.
3. Discovered variants are automatically aliased to the required engine target during the asset gathering phase.
4. Matching manifest entries are generated so the asset is indexed for fast buffer streaming at runtime.

When no `custom_portrait.png` exists, the first loose `*portrait*.png` is copied to it. The copy goes only where the target engine reads it (`assets/custom_stuff/...` for Deeproom, `assets/...` for the others), and a `_0.png` portrait of a native modern pack is left alone so that its loader does not change.

Source: wbp/packs.py, gather_custom_assets

---

### 60. [DR-49] [Universal Bridge & Full 8-Category Engine Loaders] Multi-Directory GML Resolvers

- **Target Modules**: `core/mobile_engine.bundle`, `oBackground_Create_0.gml`, `oFutaMatingPress_Create_0.gml`, `oImpregnate_Draw_0.gml`
- **Applicable Engines**: Deeproom 4.0.3 Kiwami, ModRoom v3.3, Wife's Bedroom v1.5

#### Engine Loader Enhancements
1. **Bedrooms (`oBackground_Create_0.gml`)**:
   - `func_scan_custom_backgrounds()` dynamically resolves `_base_dir`:
     ```gml
     var _base_dir = (file_exists("custom_stuff/custom_bedrooms/_manifest.txt") || file_exists("assets/custom_stuff/custom_bedrooms/_manifest.txt")) ? "custom_stuff/custom_bedrooms" : "custom_bedrooms";
     ```
   - `func_load_custom_background()` implements reciprocal fallback between `background.png` and `custom_background.png`.
2. **Voice Packs (`oFutaMatingPress_Create_0.gml`)**:
   - `_cs_bases` array scans `custom_stuff/custom_sounds/futa` alongside root `custom_sounds/futa`:
     ```gml
     var _cs_bases = ["custom_sounds/futa", "custom_sounds", "custom_stuff/custom_sounds/futa", "custom_stuff/custom_sounds"];
     // ...
     var _cs_full = _base + "/" + _cs_file;
     if (file_exists(_cs_full + "/moan_slow/_manifest.txt") || file_exists(_cs_full + "/moan_fast/_manifest.txt") || file_exists(_cs_full + "/_manifest.txt") || tc_dir_exists(_cs_full))
     ```
3. **Impregnation Shield (`oImpregnate_Draw_0.gml`)**:
   - Injected defensive `variable_instance_exists` checks for `custom_sperm_sprite` and `custom_sperm_big_sprite` preventing runtime crashes:
     ```gml
     if (variable_instance_exists(oFutaMatingPress, "custom_sperm_big_sprite") && sprite_exists(oFutaMatingPress.custom_sperm_big_sprite))
     {
         sperm_sprite = oFutaMatingPress.custom_sperm_big_sprite;
     }
     ```

Source: bundle_src/gml_Object_oBackground_Create_0.gml, func_scan_custom_backgrounds; bundle_src/gml_Object_oImpregnate_Draw_0.gml, Draw_0

---

## Part 9: Build Pipeline, Packaging & Maintenance
### 61. [DR-50] [Pipeline] Build Pipeline Overview

- **Where**: `main()` → `prompt_install_options()` → `patch_game_apk()` in `WB_Mobile_Patcher.py`
- **Enabled by / Default / What you see**: every build; the console prints one line per stage, with progress bars (`print_progress`) for the pack check, duplicate scan and X-ray alignment and spinners (`Spinner`) while UndertaleModCli compiles.

1. **Inputs**: positional inputs can be a base `.apk`, a PC game folder, mod folders or `.zip` archives. Zips are extracted to temporary folders; several mod inputs are merged into one staging folder.
2. **Engine detection** (`detect_mod_engine_version`): returns `1.5`, `modroom33` or `1.4` (Deeproom) from folder layout and `data.win` traits.
3. **Base APK** (`find_matching_base_apk`): `-b/--base-apk` wins; otherwise searches the input folder, patcher folder, and `input/` for engine expected names.
4. **Options** (`prompt_install_options`): user selects installation profile or feature toggles.
5. **Backup**: base APK is copied to `output/<base>_base_backup.apk.bak` if it does not exist.
6. **Game code**: `assets/game.droid` is extracted and patched via `patch_game_apk` using UndertaleModCli to replace code entries.
7. **Pack checks**: `plan_pack_skips` identifies incompatible or duplicate packs before gathering assets.
8. **Assets and manifests**: `gather_custom_assets` adds files under sanitized lower-case paths; `generate_manifest_data` creates `_manifest.txt` indexes; `convert_descriptors` writes one descriptor per pack for ModRoom / v1.5 and, for Deeproom with the X-ray option on, measured X-ray origins (listed in `output/<apk>_xray_origins.txt`).
9. **Repackaging & Signing**: The APK is repacked and signed using `uber-apk-signer.jar`.

Source: wbp/cli.py, main; wbp/apk.py, patch_game_apk

---

### 62. [DR-51] [Packaging] APK Repackaging Rules

- **Where**: `patch_game_apk()` and `sanitize_apk_part()`
- **Enabled by / Default / What you see**: every build; `--fast` changes compression.

- Entries of the base APK are copied with original compression, except `META-INF/` which is dropped.
- Entries whose lower-cased path matches a custom asset or generated manifest are replaced by the custom version.
- Path matching is case-insensitive because custom paths are sanitized to lower case:
  ```python
  def sanitize_apk_part(name: str) -> str:
      clean = name.strip().lower().replace(" ", "_").replace("#", "").replace(":", "_").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace('"', '').replace("'", "")
      clean = re.sub(r"_+", "_").strip("_")
      return clean or "unnamed"
  ```
- Custom `.json` files have trailing commas before `}` or `]` removed to satisfy GameMaker's `json_parse` requirements.
- Art source files (`.aseprite`, `.psd`, `.kra`) and folders named `templates`, `quarantine`, or `!duplicates` are excluded from packaging.

Source: wbp/packs.py, sanitize_apk_part; wbp/apk.py, patch_game_apk

---

### 63. [DR-52] [Signing] APK Signing & Alignment

- **Where**: `sign_apk_file()`
- **Enabled by / Default / What you see**: every build; "Aligning & signing APK".

- Executes `uber-apk-signer.jar` via Java with the following parameters:
  ```python
  cmd = [
      java, "-jar", uber_jar,
      "-a", str(apk_path),
      "--ks", str(keystore),
      "--ksAlias", "apkpatcherkey",
      "--ksPass", keystore_pass,
      "--ksKeyPass", keystore_pass,
      "--allowResign", "--overwrite"
  ]
  ```
- The signer aligns the ZIP entries and signs the APK. It requires `core/apkpatcher.keystore` and its password from `core/apkpatcher.keystore.pass`.
- If the keystore or password file is missing, the APK remains unsigned and will be rejected by Android devices.
- The shared keystore in the repository ensures that builds from different users can update each other.

Source: wbp/apk.py, sign_apk_file

---

### 64. [DR-53] [Pack Safety] Non-Destructive Pack Skipping & Reports

- **Where**: `plan_pack_skips()`, `write_skip_report()`, `move_skipped_packs()`
- **Enabled by / Default / What you see**: automatic; a report appears in `output/` when packs are skipped.

1. `plan_incompatible_skips()` runs `classify_custom_pack()` on all mod folders. Packs lacking recognized data files or using numbered-alt conventions are marked as `incompatible`.
2. `plan_duplicate_skips()` groups remaining packs and selects one to keep based on scoring (penalizing names like `_old` or `_backup`).
3. `gather_custom_assets()` uses the generated skip list to exclude files from the build.
4. `write_skip_report()` generates `output/<apk>_skipped_packs.md` containing tables of skipped packs and the reasons for their exclusion.
5. If `--move-skipped` is provided, skipped packs are moved to `output/quarantine/<timestamp>/` rather than being modified in the source folder.

Packs whose display names collide in the loose `custom/` folder keep the tag that tells them apart: the part of the pack folder name that is not just the display name again is appended (`unique_apk_name()` in `wbp/packs.py`), and a number only as a last resort; the index files (`_manifest.txt`) use the same renamed folder names as the assets.

Source: wbp/packs.py, classify_custom_pack; wbp/apk.py, patch_game_apk

---

### 65. [DR-54] [GML] Additional Injected Features

- **Where**: `patch_create_code()`, `patch_draw_code()` and `patch_v15_engine_bytecode()`
- **Enabled by / Default**: always applied on the dynamic patching path.

| Feature | What it does | Implementation |
|---|---|---|
| **Texture packs** | Swaps vanilla sprites for PNGs in `texture_packs/` | `func_texture_pack_replace` replaces `sprite_list` entries |
| **Lazy thumbnails** | Character-grid thumbnails load when shown | `inject_lazy_thumbnails_into_draw` injected into Draw |
| **Strict custom selection** | Forces custom stats/sprites for selected mods | `enforce_strict_custom_selection` injected into Draw |
| **Stat application guards** | Prevents sprite -1 crashes | Defensive checks in `func_apply_custom_futa_stats` |
| **Image size check bypass** | Accelerates startup by skipping sheet loads | `check_custom_image_size` patched to return `true` |

**v1.5 Metadata Indexing**: For v1.5 builds, `patch_v15_engine_bytecode` adds `func_load_custom_metadata` to Create, allowing the engine to read pack names and descriptions without loading every sprite strip into VRAM.

Source: wbp/gml_patches.py, patch_draw_code; bundle_src/gml_Object_oFutaMatingPress_Create_0.gml, check_custom_image_size

---

### 66. [DR-55] [Maintenance] Adding or Changing a Patch

1. **Path Selection**: Features must be added to the bundle for Deeproom 4.0.3 and to the patcher's `patch_*` functions for ModRoom and v1.5.
2. **Patcher Implementation**: Add `old_...` / `new_...` string pairs. Anchors must be verbatim from decompiled code. Guard with `if old in code:` to ensure stability across game updates.
3. **Bundle Implementation**: Decode the bundle, edit the GML script, and re-compress with `zlib`.
4. **Variable Shield**: New variables read in Draw/Step must be initialized in Create or covered by the DR-44 dynamic shield.
5. **Documentation**: Update the technical specification, including Target Anchor and IDs.
6. **Verification**: Run `ruff check` on the patcher and perform a `--fast` build to test on a device or emulator.

Source: WB_Mobile_Patcher.py, developer workflow

---

### 67. [DR-56] [Environment] Requirements & Bundled Tools

| Requirement | Detail | Checked by |
|---|---|---|
| Python 3.8+ | Standard library only | `verify_environment()` |
| Java | Required for APK signing | `verify_environment()` |
| UndertaleModCli | `core/UndertaleModCli/` | `get_utmt_cli()` |
| uber-apk-signer | `core/uber-apk-signer.jar` | `find_uber_apk_signer()` |
| Signing key | `core/apkpatcher.keystore` | `sign_apk_file()` |

Source: wbp/env.py, verify_environment; wbp/env.py, find_uber_apk_signer

---

### 68. [DR-57] [Pack Formats] Wife / Spouse Formats & the Filename Bridge

- **Target Modules**: `wbp/packs.py`, `wbp/descriptors.py`, `wbp/profiles.py`
- **Applicable Engines**: All Supported Engines

Character packs exist in two main formats: legacy (standard names) and modern (ModRoom/Deeproom `_0.png` names). They use different frame counts and descriptor keys.

**Format Differences**:
- **Deeproom 4.0.3**: Reads both sets natively. A partner pack with `custom_data.spouse` or `custom_mating_press.png` (or without `custom_wife_mating_press_0.png`) goes to the spouse loader, which reads `custom_data.spouse`; otherwise the modern loader reads `custom_data.wife` and only its flat `[sprite]` keys.
- **ModRoom V3.3**: Prefers `_0.png` names; requires specific `custom_data.wife` keys for hitboxes.
- **Wife's Bedroom v1.5**: Reads standard names only (e.g., `custom_portrait.png`).

**Patcher Bridging Logic**:
- **Asset Gathering**: `restrict_manifests` ensures files are only placed in directories the target engine reads (e.g. `assets/custom_stuff/` for Deeproom).
- **Name Bridge**: For ModRoom builds, standard-named strips are copied to `_0` names so the native loader finds them. Deeproom builds keep both names as authored.
- **Descriptor Conversion**: `wbp/descriptors.py` converts between `.spouse` and `.wife` keys based on the engine profile:
  ```python
  def convert_descriptors(assets, target_arch, xray_origins=True):
      if target_arch not in ("modroom33", "v15"):
          return assets, {}
      # ...
  ```
- **Safety**: `classify_custom_pack` rejects ModRoom format packs for v1.5 builds unless standard names are also present, as v1.5 cannot read the `_0.png` animation frames correctly.

Frame counts are part of the bridge: see section 42 for how strips are padded or, with `--approximate`, reduced when they are renamed between the two formats.

Source: wbp/profiles.py, PROFILES; wbp/descriptors.py, convert_descriptors; wbp/packs.py, restrict_manifests
