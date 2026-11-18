# WB Mobile Patcher v1.2 — Technical Details & Reference

This document contains full technical specifications, CLI options, engine features, architectural notes, and troubleshooting records.

---

## Requirements

- **Windows** with **Python 3.8 or newer**. The launcher uses `py -3`, or `python` if the Python launcher isn't installed. Get Python from <https://www.python.org/> and tick *Add python.exe to PATH*.
- **Java** (any current runtime, e.g. Temurin 17 or 21 from <https://adoptium.net/>), used to sign the APK.
- The **base game APK** for your mod's engine (see the table in README.md).
- Everything else ships in `core/`: UndertaleModCli (reads and rewrites the game code), uber-apk-signer and the signing key.
## Engine Features & Additions

### Phone Mods Architecture
Option 7 of the custom install (enabled by default) injects an Android activity (`wbmods.PhoneImportActivity`) into the APK. When a `.zip` or `.json` file is shared to the game via "Share" or "Open with", the activity captures it and deposits it in the app's `files/phone_inbox/` directory. The title screen logic imports it from that inbox.
- **ADD MOD:** Accepts direct `https://` URLs to a `.zip` archive or absolute device paths (`/sdcard/...`, `/storage/emulated/0/...`, or `file://...`; spaces are supported). Local files are copied into `phone_inbox/` and processed identically to shared intents. If Android 11+ scoped storage blocks access, the user is prompted to use Share / Open with.
- **Mod Registry:** Imports append metadata to `phone_mods_registry.txt` in the game save directory. **REMOVE MOD**, **VOICES**, and game initialization routines read this file alongside folder scans to guarantee clean removal. Builds created before 2026-11-17 lack registry tracking; re-importing the mod once registers it safely as a duplicate.
- **File Browser Note:** A native built-in file picker requires source code for `phone_import.dex`, which is not bundled in this repository.

### Touch Controls per Engine
Features differ across target engines:
- **Deeproom 4.0.3 Kiwami:** Full touch overlay:
  - Touchscreen gameplay: taps, swipes, and drags with on-screen controls.
  - Accidental tap protection: ignores background taps while menus or character cards are open.
  - Touch and hold: hold gesture triggers the radial menu in manual mode (right-click actions lacking on-screen buttons, like portrait changes or outfit toggles, may not yet be reachable via touch).
  - Drag to scroll: vertical dragging through character lists, pill selections, and bedroom lists (one row per drag step).
  - Single-fire buttons: drawer buttons act once, on touch release, when the touch started in the drawer and did not scroll; a very quick tap counts too (fixed 2026-11-17: the buttons had stopped responding). Background list selects a room only if release is within 6 px of initial touch-down.
  - Single-finger gesture ownership: secondary touch inputs do not alter the active drag gesture.
  - Bedroom drawer: swipe or tap arrows to cycle custom backgrounds.
  - Climax scene protection: open menu dialogs automatically dismiss during climax scenes.
- **ModRoom v3.3:** Executes PC game code with touch mapped to mouse inputs:
  - Touch-drag list scrolling.
  - Two-column pill menu with enlarged buttons.
  - Release-based background selection (prevents accidental room shifts while scrolling).
  - No drawer or touch-and-hold radial menu.
- **Wife's Bedroom v1.5:** Uses its native mobile interface.

### Mod Loading & Optimization
- **Engine-Aware Pack Handling:** Files and descriptors adapt to the target: ModRoom native `custom_*_0.png` packs remain authored in ModRoom and Deeproom builds; standard-named packs are bridged when required; loose Vanilla v1.2 portraits map to `custom_portrait.png`. Wife's Bedroom v1.5 strictly reads standard names.
- **Smart Asset Storage Optimization (`ZIP_STORED`):** Pre-compressed media (`.png`, `.ogg`, `.wav`, `.mp3`) are written uncompressed into the APK. This accelerates packaging by ~2.5x and eliminates GameMaker runtime decompressor latency from Android's `libyoyo.so` AssetManager.
- **High-Signal Post-Build Summary Card:** Renders a terminal summary card confirming target engine, Dynamic Variable Shield activation, asset tallies, in-memory manifest tables, and cryptographically signed APK paths.
- **ModRoom v3.3 Android Loop Eradication & Fallback:** Replaces legacy `file_find_first` blocking loops in bytecode with native in-memory buffer streaming, permanently replaces the red disclaimer screen with standard white disclaimer, and falls back gracefully to vanilla characters if unmodded folders are compiled.
- **Cowgirl Bridging & Generic Slug Quarantine:** Automatic reverse cowgirl bridging and 11-frame padding for ModRoom, plus generic slug protection (`"example"`, `"partner"`).
- **One Descriptor per Pack in Target Format:** ModRoom builds output a single `custom_data.wife` (copying `.spouse` per-pose origins into flat keys); v1.5 builds generate a single `custom_data.spouse` / `.futa` with `[info] name`; Deeproom preserves native pack descriptors. Keys are strictly added, never altered.
- **Directory Isolation:** Files and manifests reside strictly in engine-designated folders (Deeproom `custom_stuff/`, ModRoom root `custom_*`, v1.5 `custom/`), avoiding redundant duplicate folders.
- **Pill Safeties:** Falls back to base animation frames rather than crashing or failing to draw for Equine, Knotted, and Knotted Horse pills.
- **UI Additions:** Character selection grid with thumbnail caching and star favorites; aspect-ratio scaled overlay buttons for fast-forward, menu toggles, and modes.

### Pack Validation, Alignment & Duplicate Skipping
- **Incompatible Packs:** Skipped before APK compilation and documented in `<apk>_skipped_packs.md`. Reasons include: missing `custom_data.futa/.wife/.spouse/.bedroom`; numbered `custom_data_1.futa` files; lover sprites inside partner folders (or vice versa); ModRoom-format `_0.png` names in v1.5 builds; or missing required sprites in ModRoom (lover needs portrait, mating press, cowgirl, X-ray; partner needs mating press, forward cowgirl, reverse cowgirl; single reverse-cowgirl partners are padded and mirrored).
- **Deeproom Frame Divisibility:** Sprites whose width does not divide cleanly into the fixed frame count (e.g., a 1412 px portrait requiring 10 or 17 frames) are skipped to prevent off-center rendering; partners lacking portraits are also skipped. Frame widths themselves (e.g., 256 px high-res) are valid. Condom strips are not checked.
- **X-ray Overlay Alignment (Deeproom):** Enabled by default (`--no-xray-origins` disables). Compares pack X-ray frames against mating-press art; if misaligned, writes corrected origins into the descriptor inside the APK without modifying source folders. Logged to `output/<apk>_xray_origins.txt`.
- **Duplicate Tiers:** Evaluates matching folder or `[info]` names, verifies SHA-256 hashes of key art (portraits, mating sheets, backgrounds, audio, dialogue), and scores copies to preserve the best version (correct engine category, richest content, avoiding "Copy"/"(2)"/"_old").
- **Preservation & Quarantine:** Skipped packs are never modified or deleted from your mod folder. Use `--no-quarantine-duplicates` to force-include all duplicate copies. Use `--move-skipped` to relocate skipped packs to `output/quarantine/<date-time>/` without overwriting or deleting existing data.
- **Frame Conversions:** Bridging sprite names between ModRoom (`_0.png`) and standard formats adjusts frame counts via blank padding by default. Frame dropping occurs only when `--approximate` is passed.

### Hardware Telemetry (Strictly Optional)
Disabled by default; the tool prompts before applying telemetry patches. Game-code hooks are embedded in the patcher (`wbp/toy_native.py` and `core/gml_patches/native_toy/`) across Deeproom, ModRoom, and v1.5 without external dependencies. Direct mode operates natively against Intiface Central. Bridge and beat-sync modes connect to external PC ToyBridge launcher binaries (`ToyLauncher.exe`, `ButtplugBridge.exe`, `HmvLive.exe`); `--export-toy-tools` copies these to `output/Telemetry_Suite/` from `tools/toybridge/` or `%LOCALAPPDATA%\Programs\ToyBridgeLauncher\`.
- **Direct Client (`--toy-mode direct`):** Integrated GML WebSocket client connecting directly to Intiface Central (`ws://127.0.0.1:12345`) without Termux or external bridge apps.
- **Retry Limiting (`--toy-retries`):** Halts polling attempts after 5 consecutive failures (default: 5).
- **Latency Compensation (`--toy-lead`, default: 200 ms):** Predicts stroke position 0–500 ms forward based on stroke velocity (capped at a quarter stroke period). Untested on live hardware.
- **HMV Beat-Sync (`--hmv-mode`):** Binds UDP ports 45736 and 45737 with clickable bed speaker controls.
- **Companion Suite (`--export-toy-tools`):** Exports support utilities to `output/Telemetry_Suite/` when telemetry is active.

---

## Command-Line Usage & Options

```text
usage: WB_Mobile_Patcher.py [-h] [-b BASE_APK] [-o OUTPUT] [-y] [--clean] [--fast]
                            [--validate-only] [--quarantine-duplicates] [--approximate] [--move-skipped]
                            [--no-quarantine-duplicates] [--no-xray-origins]
                            [--toy-integration {y,n}] [--toy-mode {direct,bridge,all,none}]
                            [--toy-profile {default,easy,mid,hard,mideasy,midhard}]
                            [--toy-lead {0,50,100,150,200,250,300,400,500}]
                            [--toy-port TOY_PORT] [--toy-retries TOY_RETRIES]
                            [--hmv-mode] [--export-toy-tools]
                            [inputs ...]
```

### Options Reference Table

| Argument | Description |
|---|---|
| `inputs` | Positional input paths: `.apk`, PC game folder, or mod folder + base APK. |
| `-b`, `--base-apk BASE_APK` | Base APK path (e.g., `-b input/wifes_bedroom1_4.apk`). |
| `-o`, `--output OUTPUT` | Destination APK path (default: `output/<input_name>_modded.apk`). |
| `-y`, `--yes` | Unattended mode: run defaults without interactive prompts. |
| `--clean` | Remove previous `.apk` and `.idsig` files from `output/` (preserves `.bak` backups). |
| `--fast` | Fast packaging using uncompressed assets for rapid iteration. |
| `--validate-only` | Read-only mod check; outputs skipped candidates to `output/<mod>_validation.md` without building. |
| `--quarantine-duplicates`| Skip duplicate packs (default behavior). |
| `--no-quarantine-duplicates` | Retain all duplicate pack copies in the build. |
| `--no-xray-origins` | Deeproom: disable automated X-ray overlay alignment. |
| `--approximate` | Allow frame-dropping conversions when bridging ModRoom (`_0.png`) and standard formats. Lossless padding is used by default. |
| `--move-skipped` | Move skipped packs into `output/quarantine/<date-time>/`. Never overwrites or deletes. |
| `--toy-integration {y,n}` | Toggle hardware telemetry support (y/n). |
| `--toy-mode {direct,bridge,all,none}` | Telemetry transport: `direct` (in-game WebSocket), `bridge` (UDP 45735), `all`, or `none`. |
| `--toy-profile {default,easy,mid,hard,mideasy,midhard}` | Default vibration/stroke intensity profile (default: `default`). |
| `--toy-lead {0,50,100,150,200,250,300,400,500}` | Latency compensation in ms (default: `200`). |
| `--toy-port TOY_PORT` | Intiface Central WebSocket port (default: `12345`). |
| `--toy-retries TOY_RETRIES` | Connection retry ceiling before pausing (default: `5`). |
| `--hmv-mode` | Enable HMV audio beat-sync (UDP 45736 and 45737, clickable bed speakers). |
| `--export-toy-tools` | Copy bridge binaries to `output/Telemetry_Suite/` (requires telemetry enabled). |

---

## File System & Output Layout

| Location | Purpose |
|---|---|
| `output/<name>_modded.apk` | Signed, installable APK (`<first>_and_<N>_more_modded.apk` for multi-inputs). |
| `output/*.apk.idsig` | V4 signature output from uber-apk-signer (not required on device). |
| `output/<base>_base_backup.apk.bak` | Untouched backup of the source base APK. |
| `output/<apk>_skipped_packs.md` / `.json` | Markdown and machine-readable lists of skipped packs and justifications. |
| `output/<mod>_validation.md` / `.json` | Pre-build report generated by `--validate-only`. |
| `output/quarantine/<date-time>/` | Destination directory for skipped packs when `--move-skipped` is used. |
| `output/<apk>_patch_report.txt` | Logs missing GML patch anchors (informational; see technical specification). |
| `output/<apk>_format_notes.txt` | Logs packs bridged between ModRoom and standard formats or unreadable v1.5 packs. |
| `output/<apk>_xray_origins.txt` | Deeproom X-ray alignment delta records (original vs adjusted origin offsets). |
| `patch_overlay_latest_error.log` | Detailed stack trace of the latest build failure (located adjacent to `.bat`). |

---

## Code Architecture & Repository Structure

`WB_Mobile_Patcher.py` serves as the entry CLI wrapper. Core implementation logic resides within `wbp/`:

| Submodule | Functionality |
|---|---|
| `wbp/common.py` | Logging infrastructure, `guarded_replace()`, patch-miss tracker, `gml()` loader, `ROOT_DIR`. |
| `wbp/axml.py` | Binary `AndroidManifest.xml` parsing and modification for intent/activity injection. |
| `wbp/detect.py`, `wbp/env.py` | Runtime environment discovery (Python, Java, UndertaleModCli, signer) and engine detection. |
| `wbp/profiles.py` | Engine profiles: naming schemes, pack capabilities, partner descriptor schemas. |
| `wbp/descriptors.py` | Descriptor translation and synthesis (ModRoom `.wife`, v1.5 `.spouse` / `.futa` with `[info]`). |
| `wbp/packs.py` | Asset categorization, filename bridging planner, duplicate/incompatibility filters, manifest writing. |
| `wbp/engines.py` | Bytecode patch injectors for ModRoom v3.3 and Wife's Bedroom v1.5; Dynamic Variable Shield. |
| `wbp/gml_patches.py` | Dynamic GML fallback patch routines. |
| `wbp/toy.py`, `wbp/toy_native.py` | Hardware telemetry hooks; applies native GML patches from `core/gml_patches/native_toy/`. |
| `wbp/wbconv.py` | Sprite strip padding, cropping, and naming normalization logic. |
| `wbp/apk.py` | APK repacking, asset assembly, cryptographic signing via `patch_game_apk()`. |
| `wbp/cli.py` | Interactive terminal UI, command-line parsing, prompt management, and main loop. (prompts and `main()`) |

### Source Synchronization & Bundle Maintenance
- **`wbconv.py` Rules:** `wbp/wbconv.py` is one of four synchronized copies (both converters, this patcher, and Custom Studio backend). Run `python tools/sync_wbconv.py` to synchronize, or add `--check` to verify consistency.
- **Deeproom Engine Bundle:** Deeproom GML code packaged in `core/mobile_engine.bundle` is maintained in `core/bundle_src/`. Rebuild using `python tools/bundle_tool.py pack` and validate using `python tools/bundle_tool.py check`.
- **Deepthroat repair:** `python tools/repair_deepthroat.py <custom_wives> [--apply]` undoes the `[deepthroat]` block that converters before 2026-11-17 added to Deeproom partners (`wbconv.repair_deepthroat_folder`; only blocks in the old converter's exact shape, dry run by default, originals zipped next to the folder).
- **GML Fallback Snippets:** Dynamic replacement scripts are stored as individual files under `core/gml_patches/<function>/<name>.gml` and read byte-for-byte. Line endings are enforced by `.gitattributes` as non-text binary data.
- **Regression Testing:**
  - `python -m unittest discover -s tests`: Runs test suites, verifying that documentation excerpts match implementation code.
  - `python tests/golden_harness.py`: Executes end-to-end builds against reference folders (`E:/MEGA/io` or via `--io`/`WBP_IO`), validating GML script hashes, APK contents, and patch anchor lists against `tests/golden.json`. Outputs `RESULT: IDENTICAL` on match.
  - `python tests/golden_harness.py --record`: Updates reference hashes after intentional alterations. Missing test fixtures are marked skipped.

---

## Third-Party Components & Licensing

| Component | Path | License |
|---|---|---|
| UndertaleModCli (UndertaleModTool) | `core/UndertaleModCli/` | GNU GPL v3 (`core/UndertaleModCli/LICENSE.txt`); source: <https://github.com/UnderminersTeam/UndertaleModTool> |
| uber-apk-signer | `core/uber-apk-signer.jar` | Apache License 2.0; source: <https://github.com/patrickfav/uber-apk-signer> |

**Signing Key:** `core/apkpatcher.keystore` and its credential file are distributed with the repository to ensure cross-compatible app updates. Consequently, any APK signed with this repository can install as an in-place upgrade.

---

## Known Limitations

- Builds are validated by compiling, repacking, signing, and inspecting bytecode/structure; physical on-device execution testing is limited. The `PhoneImportActivity` and specific touch mechanics remain unverified across diverse Android OEM skins.
- ModRoom (`_0.png`) and standard sprite strips differ in frame structures. Lossless padding avoids visual artifacts by default; downsampling (such as partner X-ray 4 to 3 frames) requires `--approximate`, without which strips retain original sizes and may appear misaligned. Wife's Bedroom v1.5 cannot parse ModRoom packs.
- ModRoom builds substitute missing forward cowgirl sprites in `.spouse` packs by mirroring and padding the reverse cowgirl to 11 frames.
- Descriptor translation injects needed keys but does not remap ModRoom hitboxes (`kiss_box_position`) to Deeproom offset vectors.
- ModRoom lacks the Deeproom radial menu and background drawer because ModRoom game logic lacks native touch overlay routines.
- Telemetry features (direct WebSocket, UDP, HMV, and predictive latency) compile into runtime bytecode but are untested against physical hardware.
- Touch long-press triggers for outfit/portrait switches, enlarged touch boundaries, and drawer momentum remain unimplemented pending device testbeds.
- Legacy fallback patchers miss multiple anchors in modern game builds (detailed in `output/<apk>_patch_report.txt`). Deeproom 4.0.3 relies directly on the bundled engine.

---

## Troubleshooting Guide

- **"Python is required" Error:** Python must be present in system PATH. Reinstall from python.org ensuring "Add python.exe to PATH" is ticked, or use the `py` launcher. Windows Store app stubs are not supported.
- **Build Interruptions:** Inspect `patch_overlay_latest_error.log` adjacent to `WB_Mobile_Patcher.bat` for exact stage failure points and stack traces.
- **Missing Content in-Game:** Inspect `output/<apk name>_skipped_packs.md` for exclusion justifications and remediation instructions. Missing required sprites are the primary cause in ModRoom.
- **Offset or Distorted Sprites:** Review `output/<apk name>_format_notes.txt` to identify packs bridged across inconsistent frame schemas.
- **ModRoom "Variable Index [0] out of range [0] - custom_background_name_array":** Patched in v1.2 via game-native bedroom checks. Recompile with current versions if encountered.
- **ModRoom "draw_sprite_ext ... requested -1":** Caused by missing pack sprites. Fixed by exclusion checks and draw guards in v1.2.
- **"Permission denied" in `output/`:** Occurs when previous APK builds are locked by external processes (cloud sync services, Explorer preview handlers, virus scanners). The tool retries, then falls back to `<name>_<date-time>.apk`. Pause file syncing on `output/` to prevent collisions.
- **Device Install Failure:** Verify "Install unknown apps" is granted to the installer app, and uninstall existing builds signed with differing keys.

---

## Further Documentation
- [`core/TECHNICAL_SPECIFICATION.md`](core/TECHNICAL_SPECIFICATION.md): Deep bytecode patching mechanics, memory offsets, and internal auditing notes.
- [`core/ENGINE_ARCHITECTURE_REPORT.md`](core/ENGINE_ARCHITECTURE_REPORT.md): Engine loading protocols, descriptor schemas, frame maps, and format bridging specs.
- [`core/CHANGELOG.md`](core/CHANGELOG.md): Historical version changelogs.
