# Changelog: WB Mobile Patcher

All notable changes to the **WB Mobile Patcher** tool are documented in this file.

---

## [Version 1.2.0] - 2026-11-16

### Highlights
- **Fixed the Deeproom crash "Trying to read from undefined INI file" (`func_load_custom_wife`).** Loading a partner pack that has an X-ray strip (for example `!azure_dogwife`) read the X-ray origin after the pack's descriptor had already been closed. The loader now reopens the descriptor for that read. A test checks that no bundled script reads an ini file while none is open.
- **Clearer names for repeated characters.** When two loose packs share a display name, the second keeps the tag from its folder name (`astolfo_naked`) instead of a doubled name.
- **Smaller fixes.** A loose portrait is copied only where the target engine reads it and never over a native modern pack's `_0.png`; a partner with only a reverse cowgirl gets it padded as the forward one for ModRoom (the same as the converters); index files use the same renamed folder names as the assets; the READMEs start with a plain-language quick guide.
- **Bluetooth latency compensation works (`--toy-lead`).** The in-game direct client now sends the stroke position it predicts `lead` ms ahead (speed-based extrapolation, capped at a quarter of the stroke period) and reads `lead`, `profile` and `port` from the packaged `toy_direct.ini` as well as the save folder, so the values chosen at build time reach the game. Not tested on a device; this part of the direct client no longer matches the old GamePatcher.exe output.
- **Technical specification finalised.** Every section now describes the shipped code, carries a `Source:` line, and holds only code excerpts copied from the shipped sources; the review notes are gone. `tools/spec_check.py --strict` and a test keep it that way. Converters: pack folder names are made filesystem-safe (control characters, combining-mark pile-ups, trailing dots, Windows device names) and a name the OS still refuses falls back to the pack's folder name or a hash instead of crashing.
- **Toy integration is built in.** The direct Intiface client, the UDP thrust broadcast and the HMV beat-sync hooks are applied by the patcher itself (`wbp/toy_native.py`, snippets in `core/gml_patches/native_toy/`); `GamePatcher.exe` is no longer used or needed. The edits were derived by comparing the output of GamePatcher.exe on Deeproom, ModRoom and v1.5 game files and match it text for text, except that direct and HMV together now keep both networking handlers (GamePatcher.exe kept only the last), the UDP broadcast is now also added to Deeproom (GamePatcher.exe wrongly reported it as already present), and the title-screen tap patch matches the real code (`mb_left`). The companion PC apps (ToyLauncher, ButtplugBridge, HmvLive) are no longer shipped; `--export-toy-tools` copies them from `tools/toybridge/` or an installed ToyBridge launcher when present.
- **Name bridges now convert frame counts.** When a standard-named strip is bridged to the ModRoom (_0.png) name (or the reverse), it is padded, cropped or frame-mapped with the converters' rules (`wbp/wbconv.py`, a verbatim copy of their `core/wbconv.py`) instead of only renamed (lossless padding by default; conversions that drop frames, and portraits, only with the new `--approximate` flag, otherwise they are renamed unchanged and listed); converted strips are listed in the `_format_notes.txt` next to the APK. `MODROOM_NEEDS` is now shared with that module. The partner X-ray 4 to 3 crop is no longer treated as safe (a library scan of hybrid packs shows the standard 4th frame equals the modern 3rd), so it needs `--approximate` in the converters and the patcher, and is only done for packs that have a `custom_data.wife`; other (`.spouse`) packs keep their X-ray as authored, renamed only. `tools/sync_wbconv.py` keeps the three copies of `wbconv.py` identical and a test fails if they drift. A missing ModRoom scan block now reaches the patch-miss report.
- **ModRoom V3.3 builds no longer crash on a missing sprite or an empty bedroom-name list, no longer drop ModRoom's own packs, and gain touch scrolling, a two-column pill menu and release-based background picks** (but not Deeproom's full touch overlay).
- **One descriptor per pack in the target engine's format**, no duplicate `custom_*` folders in the APK, and clear reports of what was skipped or renamed and why.
- **Deeproom touch fixes** (drawer buttons, background list, multi-touch) and X-ray strips of any width.
- **Code reorganised** into a `wbp/` package with per-engine profiles, tests and a golden-output harness.
- **Not tested on a device.** Builds were checked by compiling, signing and inspecting the APKs.

### ModRoom V3.3
- **ModRoom crash "Variable Index [0] out of range [0] - custom_background_name_array" (Draw event of oFutaMatingPress).** ModRoom's own scan calls `func_check_custom_background()` for each bedroom, and that call fills `custom_background_name_array`. The patched manifest loop added the folders without calling it, so the bedroom list had entries and the names array was empty. The loop now calls the check (and resets the array), so the two stay in step and only bedrooms with a `custom_data.bedroom` are listed.
- **Touch scrolling, two-column pill menu and release-based background pick for ModRoom.** ModRoom's PC code has no touch handling (its `Draw_0` has no `device_mouse`, touch or Android code), so lists could only be scrolled with the mouse wheel. `menu_scroll_update` now has the touch-drag scroll Deeproom uses (one row per 12 px of drag, with a drag/arming record), the pill menu is drawn as two columns of 7 larger buttons (ModRoom has 14 pills; its old list scrolled 11 rows with arrows), and a background is chosen on release after a press inside the menu and without a drag, so swiping to scroll no longer switches rooms. ModRoom does **not** get Deeproom's full touch overlay (drawer, touch-and-hold radial menu); that code is part of Deeproom's own 22,000-line `Draw_0` and does not exist for ModRoom.
- **ModRoom crash "draw_sprite_ext argument 1 invalid reference to (sprite) - requested -1" (Draw event of oFutaMatingPress).** ModRoom's own scan lists a pack only if it has all the sprites the game draws (lover: portrait, mating press, cowgirl, X-ray; partner: mating press, forward cowgirl, reverse cowgirl, plus a descriptor). The Android patch replaced that scan with a manifest list and added every pack, and it also forced `custom_wife_has_portrait = true`, so a pack with a missing sprite was listed and then drew a sprite that was still -1. Now: (1) the build lists only packs that meet ModRoom's rules (with the patched alternatives for standard names) and the skipped-packs report names the missing sprite, e.g. a standard `.spouse` pack has no forward cowgirl; (2) `custom_wife_has_portrait` is set only when a pack is loaded; (3) as a safety net, `Draw_0` draws sprites through `tc_safe_sprite_ext` / `tc_safe_sprite_part_ext` (252 and 16 call sites), which skip a sprite that is -1 instead of ending the game. In the ModRoom V3.3 example 14 of 20 packs are kept and 6 skipped with reasons.
- **ModRoom builds no longer drop ModRoom's own packs.** The pre-flight check called ModRoom's native names (`custom_futa_*_0.png`, `custom_wife_*_0.png`, `_alt_N` variants) the "older numbered convention" and skipped those packs for every target, so 13 of the 20 packs in the ModRoom V3.3 example never reached the APK (it kept 7, all standard-named). The check now accepts that naming for ModRoom and Deeproom builds (Wife's Bedroom v1.5 cannot read it and keeps the old rule) and still skips a pack whose sprites do not match its folder (wife sprites in `custom_futas`, lover sprites in `custom_wives`), and numbered `custom_data_N` files. Native ModRoom packs also keep their own names: no standard-named copies are added, because ModRoom's futa loader switches to its legacy 9-frame path whenever `custom_mating_press.png` exists. The example now keeps 18 of 20 packs.
- **ModRoom builds no longer add other-kind sprite copies.** A wife pack used to get `custom_futa_*_0.png` copies and a futa pack `custom_wife_*_0.png` copies, which no loader reads (38 files in the ModRoom V3.3 example). Hybrid packs with both descriptors keep every copy. Deeproom and v1.5 output is unchanged.

### Packs, formats and output
- **No duplicate `custom_*` folders in the APK.** Character files were already written only where each engine reads them, but the index files (`_manifest.txt`) were written twice: Deeproom builds also got a copy under the root `assets/custom_futas`, `custom_wives`, `custom_bedrooms` and `custom_sounds` (about 1,240 manifests, folders that held nothing else), and ModRoom builds got extra copies under `assets/custom_stuff/`. Now Deeproom writes manifests only under `assets/custom_stuff/custom_*`, ModRoom only under the root `assets/custom_*`, and v1.5 only under `assets/custom/`. This follows the engines' own code: the Deeproom bundle prefers `custom_stuff/custom_wives/_manifest.txt` when it exists and uses the root path only as a fallback, and ModRoom's streaming code reads the root path first. A root copy also made the Deeproom sound scan (`custom_sounds` is listed before `custom_stuff/custom_sounds`) find pack folders with no files in them. Not yet tried on a device.
- **One descriptor per pack, in the target's format** (`wbp/descriptors.py`). ModRoom builds write a single `custom_data.wife` (a `.spouse` pack is converted: per-pose origins copied to the flat `[sprite]` keys) instead of a `.spouse` plus a `.wife` clone. v1.5 builds turn a `.wife` pack into `custom_data.spouse` and add `[info] name` (the folder name) to `.futa`/`.spouse` files that lack it, so they no longer show as "Untitled" (52 packs in the v1.5 example folder). The conversion only adds keys, never changes values, and Deeproom output is unchanged. 14 unit tests in `tests/test_descriptors.py`.
- **Deeproom builds keep ModRoom-format packs as authored.** Packs with `custom_*_mating_press_0.png` no longer get standard-named copies and a `.spouse` file, which switched Deeproom to its legacy loaders (futa mating press 9 vs 24 frames, wife 4 vs 5, portrait 10 vs 17). Deeproom also no longer adds a `.wife` clone to every `.spouse` pack (388 files in the example folder).
- **v1.5 builds list ModRoom-format packs** (`_0.png` strips without standard names) in `output/<apk>_format_notes.txt`; v1.5 reads standard names only, so their art would not show. v1.5 output for packs in its own format is unchanged.
- **Format warning.** Builds list wife packs whose sprites were renamed between the ModRoom (`_0.png`) and standard names in `output/<apk>_format_notes.txt`: the two formats cut frames differently (mating press 5 vs 4, portrait 17 vs 10, reverse cowgirl 10 vs 5, X-ray 3 vs 4), so those characters should be checked in game.
- `custom_data.wife` descriptors now also supply the display name (`extract_pack_display_name`).
- **Duplicate and incompatible packs are skipped, never moved.** The pre-flight checks now only decide; skipped packs are left out of the APK and its manifests, and `output/<apk>_skipped_packs.md` / `.json` list each one with the reason, the kept copy and how to include it. The user's mod folder is no longer changed. The old move could delete an earlier quarantined copy with the same name.
- New `--move-skipped` option moves skipped packs into a new `output/quarantine/<date-time>/` folder; it never overwrites or deletes.
- `--validate-only` is now read-only: it reports packs that would be skipped (`output/<mod>_validation.md`) and builds or moves nothing.
- Duplicate tie-breaking also treats `Name Copy`, `Name Copy 2` and `Name old` as copies.

### Deeproom 4.0.3 game fixes (`core/mobile_engine.bundle`)
These change the Deeproom engine only; the ModRoom and v1.5 engine code is not touched by them.
- **X-ray strips of any width (modern `.wife` loader).** The loader cut every X-ray strip into 3 frames, so a 4-frame strip (640 px, the legacy/spouse layout) was cut into 213 px slices. It now reads the frame count from the strip width (160 px per frame, 1-8 frames) and keeps 3 when the width is not a multiple of 160. The draw code only uses frames 0-2 of a wife X-ray strip (canal, womb, cervix) and takes the modern cum-pool layer from the lover sprite, so the fourth frame is ignored and the strip should now display correctly (read from the code, not run in the game).
- **`[xray]` origin wins over `[sprite] xray_x/xray_y`** (both Deeproom partner loaders). Deeproom's own `[xray] origin_x/y` is now read first and the v1.5-style `[sprite]` keys are the fallback; before it was the reverse, so a file holding both used the v1.5 value.
- **Touch drawer buttons act once.** They fired on touch-down and again on release (a toggle could cancel itself, and the Manual mode button could skip a step); they now act once, on release, and only if the finger did not drag.
- **Background list no longer switches room when you swipe to scroll.** A pick now needs a release within 6 px of the touch-down.
- **Multi-touch:** a second finger no longer moves the first finger's drag; the finger that started a gesture owns it until it lifts.
- **No more file-system check every frame** for the wife's deepthroat sprite while the pose menu is open; the result is cached per wife.
- Checked and left unchanged: the audio-stream cache is keyed by file path and its ids are stored in lists, so destroying cached streams would break them; legacy/modern wife sprite handling only keeps one extra sprite set. Not done because they need a device test or a runtime check: synthetic long-press for portrait/outfit (`touch_long_press_synthetic` is never set), larger touch targets, drawer scroll momentum, `string_split` for manifest parsing, a cached selector filter.
- `core/bundle_src/` holds the editable GML of the bundle; `python tools/bundle_tool.py pack` rebuilds `core/mobile_engine.bundle` from it.

### Added
- **Tests.** A golden-output harness (`tests/golden_harness.py`, baseline `tests/golden.json`) builds the three example games and compares hashes of every patched GML script, every APK entry and the missed-anchor list, to prove a refactor changed nothing. 34 unit tests (`tests/test_descriptors.py`, `test_packs.py`, `test_output.py`, `test_gml_patches.py`; run `python -m unittest discover -s tests`) check what each engine can read, descriptor conversion, the validator/packer agreement and the locked-output handling. The harness only proves output did not change since its last recorded run; the unit tests are what check correctness.
- **`edit_files/` folders are no longer packaged** (editor source art; the game never reads them).
- **On-device mod sharing (TB-05 / DR-27) is now built into the APK.** The binary manifest editor registers `wbmods.PhoneImportActivity` and `core/phone_import.dex` is added as `classes2.dex` (next free `classesN.dex`). The "Phone Mod Sharing" option now has an effect; a failed edit leaves the manifest unchanged. Verified byte-for-byte against the ToyBridge reference APK; not tested on a device.
- **Patch report.** 110 GML patches (plus 20 that only logged success) that used to skip silently when their anchor text was missing now record a miss (`guarded_replace()`); misses are listed in `output/<apk>_patch_report.txt`.

### Fixed
- **Build failed at the very end with `PermissionError ... output\\<name>_modded.apk`.** The old APK was deleted with the error swallowed, so when another program (MEGA sync, Explorer preview, antivirus) had it open the build ran for minutes and then could not create the file. The patcher now retries the delete for a few seconds and, if the file is still locked, writes `<name>_<date-time>.apk` and says so. `--clean` reports files it could not remove, and the failure report explains permission errors. Tests: `tests/test_output.py`.
- UndertaleModCli and other tools could hang forever waiting for keyboard input when the patcher ran without a console; all child processes now get a closed stdin.
- Removed dead code: `apply_unified_diff()` (its pattern never matched) and `pad_strip_to_target_frames()` (never called).
- Missing `hashlib` import crashed the default duplicate check; missing `socket` import crashed the telemetry server probe.
- The Default Installation answer to the duplicate question was ignored.
- `--clean` and the clean prompt did nothing; they now remove old `.apk` / `.idsig` files before building (base `.bak` backups are kept).
- The wife eye/iris sprite guard was written but never applied.
- `patch_game_apk()` raised NameError when called without options.
- The variable shield now logs a notice when UndertaleModCli fails instead of silently adding nothing.
- Tool output is decoded as UTF-8 on Windows; temporary folders from `.zip` mods are removed at exit.
- Folders named `templates`, `quarantine` or `!duplicates` are no longer listed as packs in generated manifests.

### Code structure
- **Code reorganised, output unchanged.** The 7,700-line `WB_Mobile_Patcher.py` is now a thin launcher plus the `wbp/` package (10 modules), and the 232 embedded GML strings (about 4,000 lines) moved to `core/gml_patches/`. The golden harness confirms byte-identical patched GML and APK contents for the Deeproom 4.0.3, ModRoom v3.3 and Wife's Bedroom v1.5 example games, and a signed ModRoom build was checked.
- **Engine profiles and one bridge planner (no output change).** `wbp/profiles.py` holds what each engine reads (ModRoom V3.3, Deeproom 4.0.3, Wife's Bedroom v1.5): native `_0.png` / `_alt_N` names, which packs it can list, and how partner descriptors are written. The filename bridge is one function, `plan_name_bridge()`, used by the packer to make the copies and by the pre-flight check to decide whether a pack will have every sprite the engine needs, so the verdict always matches the files that end up in the APK. The golden harness is identical before and after, and the unit tests cover the rules, including a check that the validator and the packer agree.
- The 50 ms latency preset is offered in the interactive menu (it was CLI-only).
- `GamePatcher.exe` is looked up under `%LOCALAPPDATA%` instead of a hard-coded user folder.
- `WB_Mobile_Patcher.bat` finds Python via `py -3` first, reports failures with the exit code and log location instead of always printing "Finished!", and no longer enables delayed expansion (which dropped `!` from paths).

### Documentation
- README rewritten for accuracy: requirements, phone install steps, files the tool writes, troubleshooting, third-party licenses (UndertaleModCli is GPL v3) and the shared signing key; removed claims for features that don't ship (on-phone mod management, momentum scrolling).
- Technical specification: every section has an audit note measured against the shipped code; new glossary, engine-path table, Integration Map entries for Parts 6–9, Part 8 heading, and new sections DR-50 to DR-56 (pipeline, packaging, signing, pack skipping, additional injected features, adding a patch, environment).
- README, technical specification and `core/ENGINE_ARCHITECTURE_REPORT.md` reviewed together on 2026-11-16: touch-control claims corrected (a touch hold opens the radial menu only in manual mode; the unverified "dual-column pill menu" claim was removed), engine rules, file names and limits brought in line with the code, and this changelog regrouped.

---

## [Version 1.1.0] - 2026-11-13

### Highlights
- Implementation of the **3-Tier Duplicate Detection & Quarantine Pipeline** across mod discovery and packaging.
- Comprehensive integration of the **ToyBridge 1.5.3 Suite** supporting both Standalone Direct WebSocket toy clients (zero Termux required) and external UDP telemetry bridges.
- Implementation of **Anti-Hang Connection Retry Limits** across CLI non-blocking probes and in-engine GML runtime polling.
- **In-Engine Bluetooth Latency Compensation (Delay Fix)** with live on-screen Title HUD controls.
- Bi-directional character asset bridging, Base APK engine auto-detection, and enhanced packaging resilience.

### Added
- **Deeproom 4.0.3 Kiwami & ModRoom 3.3 Engine Compatibility**:
  * Added native traversal and asset ingestion for the new `custom_stuff/` root directory container.
  * Generates dual-path Android `_manifest.txt` index files for both `assets/custom_stuff/...` and root `assets/custom_...` so GameMaker engine variants find all packs on Android. (Replaced in 1.2.0: manifests are now written only where each engine reads them.)
  * Ingests, preserves, and normalizes new Deeproom 4.0.3 sprites (`custom_futa_deepthroat_0.png`, `custom_futa_xray_0.png`, `custom_wife_xray_0.png`) and rich INI blocks (`[personality]` with `climax`/`womb_fill`, `[gender]` with `is_male`, `[condom]`, `[colors]`, `[stats_alt_*]`).
  * Automatic engine detection recognizes Deeproom 4.0.3 and auto-pairs with `wifes_bedroom1_4.apk`.
  * Filters non-mod utility directories (`Templates/`, `texture_packs/`, `Ball Clench Stuff/`, `Custom Sperm/`) from being falsely treated as character packs.
- **3-Tier Cross-Folder & Multi-Content Duplicate Detection Engine**:
  * Detects duplicates **across different folders and categories** (e.g. same character in `custom/` and `custom_wives/`).
  * Deduplicates all custom content folders including bedrooms, SFX/voices (`custom_sounds/`), music (`custom_music/`), and dialogue packs (`dialogue_packs/`).
  * Renamed quarantine folder to **`!duplicates`** (pinned to the top of explorer listings).
  * **Tier 1 (Slug & Metadata Collision)**: Identifies normalized slug matches, OS copy suffixes (`- Copy`, ` (1)`), and internal descriptor `[info] name=` collisions.
  * **Tier 2 (Asset Fingerprinting)**: Computes SHA-256 hashes for core character sprites (`custom_portrait.png`, `custom_mating_press.png`, `background.png`) to detect identical characters under different folder names.
  * **Tier 3 (Canonical Selection & Scoring)**: Scores packs based on completeness, voice packs, poses, naming cleanliness, and recency, retaining the winner and isolating duplicates into `output/quarantine/!duplicates/`.
  * Generates `DUPLICATES_REPORT.txt` detailing quarantined packs, collision tier, and rationale.
  * Added `--quarantine-duplicates` (default True) and `--no-quarantine-duplicates` CLI flags.
- **Standalone Direct Toy Client (`--toy-mode direct`)**:
  - Direct WebSocket client in GML communicating natively with Intiface Central (`ws://127.0.0.1:12345`).
  * **Completely eliminates the requirement for Termux, Proot, or secondary background Linux bridges on Android.**
  * Implements Buttplug message protocol v3 (handles `RequestServerInfo`, `RequestDeviceList`, `StartScanning`, `ScalarCmd` vibrate/oscillate, and `LinearCmd` stroker positioning).
  * Actuator safety: automatically fires `StopAllDevices` if the app is suspended, minimized (`os_is_paused()`), or when a wall-clock gap (>1500ms) occurs.
- **Anti-Hang Connection Retry Limiter**:
  * **CLI Setup Probe (`probe_intiface_server`)**: Non-blocking TCP check on port 12345 (3 attempts, 0.4s timeout, <1.25s total). Prompts user immediately if Intiface is closed without stalling.
  * **In-Game GML Limiter**: Caps connection attempts at 5 (`tb_retry_max = 5`). Pauses background polling when reached to conserve battery and updates title HUD to `TOY: NOT FOUND (TAP RETRY)`.
  * **On-Screen Tap Controls**: Tapping the top HUD line instantly clears the counter and retries connection, or toggles toy mode on/off.
- **Bluetooth Latency Compensation (Delay Fix)**:
  * In-engine GML `LeadPredictor` compensating for typical 100–300ms Bluetooth latency on devices like Lovense, Fleshlight Launch, Handy, Kiiroo.
  * Presets: `0 ms (Off)`, `50 ms`, `100 ms`, `150 ms`, `200 ms (Recommended for BLE)`, `250 ms`, `300 ms`, `400 ms`, `500 ms`.
  * **Title Screen Cycle-Tap**: Tap `DELAY FIX: <MS> (TAP)` directly on the title screen to cycle latency compensation live.
  * **APK Pre-Seeding**: Automatically bundles `assets/toy_direct.ini` into the APK so preferred settings are active on first boot.
- **Title Screen Power Profiles**:
  * Tap `POWER: <PROFILE> (TAP)` to cycle through `DEFAULT` (0–100%), `EASY` (0–30%), `MID` (30–60%), `HARD` (60–100%), `MIDEASY` (0–50%), and `MIDHARD` (50–100%).
- **HMV Audio Beat-Sync Mode (`--hmv-mode`)**:
  * Real-time UDP port 45736 listener for dynamic thrust velocity and room tinting synced to music beats, with clickable in-game bed speakers transmitting pings on port 45737.
- **Companion Suite Export (`--export-toy-tools`)**:
  * Bundles and exports `output/ToyBridge_Suite/` containing `ToyLauncher.exe`, `ButtplugBridge.exe`, `GamePatcher.exe`, `HmvLive.exe`, `profiles.json`, `fake_intiface.py` mock testing server, and documentation guides.
- **Extended CLI Options**:
  * Added `--toy-integration`, `--toy-mode`, `--toy-profile`, `--toy-lead`, `--toy-port`, `--toy-retries`, `--hmv-mode`, and `--export-toy-tools`.

### Changed & Improved
- **Base APK Engine Auto-Detection**:
  * Intelligently selects between `wifes_bedroom1_4.apk` (for ModRoom v3.3 / Deeproom 4.0) and `wifes_bedroom1_5.apk` (for Wife's Bedroom v1.5).
- **Interactive Installation Setup**:
  * Prompts now include dedicated ToyBridge configuration submenus with recommended defaults.
- **Documentation**:
  * Added Part 7 to `TECHNICAL_SPECIFICATION.md` detailing technical specifications `[TB-07]` through `[TB-11]`.

---
