# WB Mobile Patcher v1.2

A Windows tool that turns your **Wife's Bedroom v1.5**, **Deeproom 4.0.3 Kiwami (November 2026)** and **ModRoom v3.3** PC game folders or mod `.zip` archives into signed Android apps (`.apk`) for phones and tablets.

It adds touch controls, a character selection grid, mod-format bridging, engine stability fixes, in-game offset calibration and custom sound effects. Hardware telemetry (toy integration) is strictly optional and off unless you turn it on.

---

## Start here (the short version)

**What it does:** turns the PC version of your game (plus a mod folder if you have one) into an Android app you can install on a phone or tablet.

1. Install two free things once: **Python** (python.org; tick *Add python.exe to PATH*) and **Java** (adoptium.net, "Temurin 17" or newer).
2. Put the original game's Android file (`wifes_bedroom1_4.apk`, or `wifes_bedroom1_5.apk` for Wife's Bedroom v1.5) in the **`input`** folder.
3. **Drag your game or mod folder (or its `.zip`) onto `WB_Mobile_Patcher.bat`.**
4. Press **Enter** at every question. The default answers are the recommended ones.
5. Wait a few minutes. When it says *Success*, your app is in the **`output`** folder. Copy the `.apk` file to your phone and open it to install.

**If something goes wrong**
- *"Python" or "Java" not found:* install it from the links above, then restart the computer and try again.
- *The window closes immediately:* open Command Prompt in this folder and run `python WB_Mobile_Patcher.py` to see the message.
- *Some characters are missing in the app:* open the file ending in `_skipped_packs.md` in `output`. It lists each skipped character and why (usually a duplicate or a missing picture).
- *Install fails on the phone:* uninstall an older copy of the game first, and allow "install unknown apps" for the app you opened the file with.
- *Anything else:* `patch_overlay_latest_error.log` (next to the `.bat`) holds the details of the last failed build.

**Using it on the phone (Deeproom builds)**
- *Add a mod:* on the title screen tap **ADD MOD** and paste a download link (`https://...`) or the file's location on the phone (for example `/sdcard/Download/mod.zip`). Easiest of all: in your phone's file manager, long-press the `.zip`, tap **Share** (or **Open with**) and pick the game.
- *Remove a mod:* tap **REMOVE MOD** and pick it. Only mods added on the phone can be removed this way; the game restarts afterwards.
- *Voices:* a voice pack you add appears under **VOICES**; pick it, then pick the character that should use it.
- If the game says it cannot open a file, Android is blocking that folder: use **Share / Open with** instead.

The toy and hardware features are **off** unless you say yes to them. The rest of this page is for people who want the details.

---

## Requirements

- **Windows** with **Python 3.8 or newer** (the launcher uses `py -3`, or `python` if the launcher isn't installed). Get it from <https://www.python.org/> and tick *Add python.exe to PATH*.
- **Java** (any current runtime, e.g. Temurin 17 or 21 from <https://adoptium.net/>), used to sign the APK.
- The **base game APK** for your mod's engine (see below).
- Everything else ships in `core/`: UndertaleModCli (reads and rewrites the game code), uber-apk-signer and the signing key.
- Toy integration needs nothing extra: the game-code patches are built into the patcher (see [Hardware telemetry](#4-hardware-telemetry-strictly-optional)).

## Required base game APK

The patcher only uses files you give it: your game's APK and your PC game or mod folder. No game files are included with it.

Place the APK that matches your mod's engine in the `input/` folder, or drag it onto `WB_Mobile_Patcher.bat` together with your mod folder:

| Your mod | Base APK to provide | Notes |
|---|---|---|
| **Deeproom 4.0.3 Kiwami** | `wifes_bedroom1_4.apk` (or `wifes_bedroom.apk`) | Uses the full mobile engine in `core/mobile_engine.bundle`: `custom_stuff/` container, pose origins, custom SFX/music, in-game offset calibrator. Reads both `.spouse` and `.wife` partner packs natively |
| **ModRoom v3.3** | `wifes_bedroom1_4.apk` (or `wifes_bedroom.apk`) | Detected as its own engine. Loads mods from an index instead of scanning folders (which phones cannot do), removes the red disclaimer error, and gives partners that only have a reverse cowgirl a forward one too |
| **Wife's Bedroom v1.5** | `wifes_bedroom1_5.apk` | Native v1.5 manifest streaming, unified `custom/` layout, safe `[info]` descriptor synthesis |

The tool also looks for a matching APK next to `WB_Mobile_Patcher.bat` itself.

---

## Quick start

1. Put your base APK (e.g. `wifes_bedroom1_4.apk`) in the `input/` folder.
2. Drag your mod folder (e.g. `Deeproom 4.0.3`) or mod `.zip` onto **`WB_Mobile_Patcher.bat`**.
3. Press **Enter** to accept the recommended *Default Installation*. A few short yes/no questions follow (skip duplicate packs, align X-ray overlays, clean old builds, fast packaging, toy integration); pressing **Enter** on each accepts the default. Long steps show a progress bar or a spinner with the elapsed time.

The signed APK is written to **`output/`**. If any mod packs were left out, a report named `<apk name>_skipped_packs.md` is written next to it.

### Installing on your phone

1. Copy the `.apk` from `output/` to your phone (USB, cloud drive, or chat-to-self).
2. Open it on the phone. If Android asks, allow your file manager or browser to *install unknown apps* (Settings → Apps → Special access).
3. If an older build is installed and the install fails, uninstall the old one first.

---

## What this tool adds

### Phone mods (details)

Option 7 of the custom install (on by default) adds an Android activity (`wbmods.PhoneImportActivity`) that receives a `.zip` or `.json` shared to the game ("Share" / "Open with") and puts it in the app's `files/phone_inbox/` folder; the title screen imports it from there.

- **ADD MOD** accepts an `https://` link to a `.zip`, or the path of a `.zip` / `.json` on the phone (`/sdcard/...`, `/storage/emulated/0/...` or `file://...`; spaces are fine). A local file is copied into `phone_inbox/` and imported like a shared one. Android 11 and later often block reading other folders; the game then says so and suggests Share / Open with.
- Every import also records what it created in `phone_mods_registry.txt` in the game's save folder. **REMOVE MOD**, **VOICES** and the reload at game start use that list as well as the folders, so mods added on the phone can always be found and removed. Mods added with a build older than 2026-11-17 are not in the list; if one cannot be removed, add it again once (it is recognised as a duplicate).
- A built-in file browser would need the source of `phone_import.dex`, which is not in this repository.

### 1. Touch controls

What each engine gets differs. **Deeproom** has the full touch overlay below. **ModRoom v3.3** runs the PC game code with touch mapped to the mouse, plus touch-drag scrolling in its lists, a two-column pill menu with larger buttons, and background selection on release (no accidental room change while scrolling); it has no drawer or touch-and-hold menu. **Wife's Bedroom v1.5** uses its own mobile interface.
- **Touchscreen play**: taps, swipes and drags with on-screen controls.
- **Accidental tap protection**: while menus or character cards are open, taps behind them are ignored.
- **Touch and hold**: a hold opens the radial menu, in manual mode only. Right-click actions that have no on-screen button (changing portrait, toggling the outfit) may not be reachable by touch yet.
- **Drag to scroll**: drag through character lists, pill selections and bedroom lists (one row per drag step).
- **Buttons act once** (Deeproom): the drawer buttons fire on release, only if the finger did not drag, and the background list only selects a room on a release within 6 px of the touch-down, so swiping to scroll does not trigger them.
- **One finger owns a gesture** (Deeproom): a second finger no longer moves the first finger's drag.
- **Bedroom drawer**: swipe or tap arrows to scroll through custom room backgrounds.
- **Climax scene protection**: open menu windows close automatically during climax scenes.

### 2. Mod loading
- **Engine-aware pack handling.** Each engine gets the file names and descriptor it reads: ModRoom's native `custom_*_0.png` packs are kept as authored in ModRoom and Deeproom builds, standard-named packs are bridged where an engine needs the other names, and loose Vanilla v1.2 portraits are mapped to `custom_portrait.png`. Wife's Bedroom v1.5 reads standard names only.
- **Smart Asset Storage Optimization (`ZIP_STORED`):** Pre-compressed media assets (`.png`, `.ogg`, `.wav`, `.mp3`) are packaged uncompressed inside the APK. This accelerates packaging by ~2.5x and eliminates GameMaker runtime decompressor latency from Android's `libyoyo.so` AssetManager during gameplay.
- **High-Signal Post-Build Summary Card:** Renders a clean terminal summary card confirming the exact engine target, Dynamic Variable Shield activation, asset counts, in-memory manifest tables, and cryptographically signed APK path.
- **ModRoom v3.3 Android Loop Eradication & Fallback:** Replaced legacy `file_find_first` blocking loops in bytecode with native in-memory buffer streaming, permanently replaced the red disclaimer screen with standard white disclaimer, and falls back gracefully to vanilla characters if unmodded folders are compiled.
- **Cowgirl Bridging & Generic Slug Quarantine:** Automatic reverse cowgirl bridging and 11-frame padding for ModRoom, plus generic slug protection (`"example"`, `"partner"`).
- **One descriptor per pack, in the target's format.** ModRoom builds write one `custom_data.wife` (a `.spouse` pack's per-pose origins are copied into the flat keys), v1.5 builds write one `custom_data.spouse` / `.futa` with an `[info] name`, and Deeproom keeps each pack's own file. Keys are only added, never changed.
- **No duplicate `custom_*` folders**: files and index manifests go only into the directory the engine reads (Deeproom `custom_stuff/`, ModRoom root `custom_*`, v1.5 `custom/`).
- **Pill safeties**: falls back to base frames instead of crashing or drawing nothing for Equine, Knotted and Knotted Horse pills.
- **Character selection grid** with thumbnail caching and star favorites.
- **Touch overlay** with buttons for fast-forward, menu toggles and interaction modes, scaled to the phone's aspect ratio.

### 3. Duplicate and incompatible packs are skipped, never moved

Before building, the tool checks your mod packs:

- **Incompatible packs** are skipped, with the reason in the report: no `custom_data.futa/.wife/.spouse/.bedroom` file; a numbered `custom_data_1.futa` file; partner sprites in a lover folder or the reverse; ModRoom-format `_0.png` names in a v1.5 build (v1.5 cannot read them); and, for ModRoom, a pack that lacks a sprite ModRoom needs (lover: portrait, mating press, cowgirl, X-ray; partner: mating press, forward cowgirl, reverse cowgirl; a partner that has only a reverse cowgirl gets it copied, padded, as the forward one), because ModRoom would list it and then fail when the missing sprite is drawn.
- **Deeproom packs the game would show cut up** are skipped too: the game cuts every strip into a fixed number of frames, so a strip whose width does not divide into that number (for example a 1412 px portrait, which must be 10 or 17 frames) shows off-centre frames; a partner without a portrait is also skipped. Frame width itself does not matter (high-res packs with 256 px portraits are fine), and condom strips are not checked.
- **X-ray overlays** (Deeproom, option asked right after the duplicate question, default Yes, `--no-xray-origins` to turn it off): each pack's X-ray is measured against its own mating-press sprite, and where it would be drawn off-centre a corrected origin is written into the copy of the descriptor inside the APK (your mod folder is not changed). The packs adjusted are listed in `output/<apk>_xray_origins.txt`.
- **Duplicates** are found in three tiers: matching folder or `[info]` names, identical key art (SHA-256 of portraits, mating sheets, backgrounds, audio, dialogue), then a score that keeps the best copy (correct category for the engine, more content, not named "Copy"/"(2)"/"_old").

Skipped packs are simply **left out of the APK. Your mod folder is not changed: nothing is moved or deleted.** Each build that skips anything writes two files next to the APK:

- `<apk name>_skipped_packs.md`: which packs were skipped, which copy was kept, why, and how to include a pack anyway.
- `<apk name>_skipped_packs.json`: the same list for scripts.

When a pack's sprite names are bridged between the ModRoom (`_0.png`) and standard formats, the frame count of each strip is converted too: padding with blank frames by default, and also frame dropping only with `--approximate` (the format notes file lists what happened).

To keep every copy of duplicates, build with `--no-quarantine-duplicates`. To physically move skipped packs out of your mod folder, add `--move-skipped`: they go to a new `output/quarantine/<date-time>/` folder and nothing is ever overwritten or deleted.

### 4. Hardware telemetry (strictly optional)

Off by default; the tool asks before adding any telemetry code. The game-code patches are built into the patcher (`wbp/toy_native.py` and `core/gml_patches/native_toy/`), the same for Deeproom, ModRoom and v1.5, so no extra program is needed. Direct mode (the default) needs no other program: the game talks to Intiface Central itself. The bridge and beat-sync modes also need a receiver on the PC, the ToyBridge launcher apps (`ToyLauncher.exe`, `ButtplugBridge.exe`, `HmvLive.exe`), which are not part of this tool; `--export-toy-tools` copies them to `output/Telemetry_Suite/` from `tools/toybridge/` or from an installed ToyBridge launcher (`%LOCALAPPDATA%\Programs\ToyBridgeLauncher\`) if you have one.

- **Direct client (`--toy-mode direct`)**: an in-game WebSocket client that talks to Intiface Central (`ws://127.0.0.1:12345`), no Termux or bridge app needed.
- **Retry limit**: connection attempts stop after 5 tries (`--toy-retries`) so the game doesn't keep polling.
- **Latency compensation** (`--toy-lead`, default 200 ms): the in-game client sends the predicted stroke position 0–500 ms ahead (extrapolated from the stroke's speed, at most a quarter of the stroke period). Not tested on a device.
- **HMV beat-sync** (`--hmv-mode`): UDP ports 45736 and 45737 and clickable bed speakers.
- **Companion tools** (`--export-toy-tools`): copied from `tools/toybridge/` to `output/Telemetry_Suite/`; only when telemetry is enabled.

---

## Files the tool writes

| Where | What |
|---|---|
| `output/<name>_modded.apk` | The signed APK (with several mod inputs: `<first>_and_<N>_more_modded.apk`) |
| `output/*.apk.idsig` | Signature file written by the signer; you don't need to copy it to the phone |
| `output/<base>_base_backup.apk.bak` | Untouched copy of your base APK |
| `output/<apk name>_skipped_packs.md` / `.json` | Packs left out of that build, and why |
| `output/<mod>_validation.md` / `.json` | From `--validate-only`, when any pack would be skipped |
| `output/quarantine/<date-time>/` | Only with `--move-skipped` |
| `output/<apk>_patch_report.txt` | Only when some patch anchors were not found in the game build (usually harmless; see the technical specification) |
| `output/<apk>_format_notes.txt` | Only when packs were renamed between the ModRoom (`_0.png`) and standard names, or a v1.5 build holds ModRoom-format packs it cannot read; the two formats cut animation frames differently, so check those characters in game |
| `output/<apk>_xray_origins.txt` | Deeproom builds with X-ray alignment on: packs whose X-ray origin was adjusted (old and new origin) |
| `patch_overlay_latest_error.log` | Details of the last failed build (next to the `.bat`) |

`--clean` removes old `.apk` and `.idsig` files from `output/` before building; base backups (`.bak`) are kept.

---

## Command-line reference

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

Positional arguments:
  inputs                    Input path(s): .apk, PC game folder, or mod folder + base APK

Options:
  -b, --base-apk            Base APK to use (e.g. -b input/wifes_bedroom1_4.apk)
  -o, --output              Output file path (default: output/<input_name>_modded.apk)
  -y, --yes                 Use default settings without interactive prompts
  --clean                   Remove old .apk/.idsig builds from output/ first (keeps .bak backups)
  --fast                    Fast packaging (uncompressed) for quick testing
  --validate-only           Read-only check of a mod folder; if packs would be skipped, lists them
                            in output/<mod>_validation.md. Builds nothing, moves nothing
  --quarantine-duplicates   Skip duplicate packs (this is the default)
  --no-quarantine-duplicates Keep every copy of duplicate packs
  --no-xray-origins     Deeproom: do not align X-ray overlays with the character sprites
  --approximate             Also convert sprite strips whose frame count must drop frames when bridging ModRoom (_0.png) and
                            standard names (default: lossless padding only; other strips are renamed unchanged and listed)
  --move-skipped            Also move skipped packs to output/quarantine/<date-time>/ (never deletes)
  --toy-integration {y,n}   Enable hardware telemetry (y/n)
  --toy-mode {direct,bridge,all,none}
                            'direct' (in-game WebSocket client), 'bridge' (UDP 45735), 'all', 'none'
  --toy-profile {default,easy,mid,hard,mideasy,midhard}
                            Default intensity profile (default: 'default')
  --toy-lead {0,50,100,150,200,250,300,400,500}
                            Bluetooth latency compensation in ms (default: 200)
  --toy-port TOY_PORT       Intiface Central WebSocket port (default: 12345)
  --toy-retries TOY_RETRIES Connection attempts before pausing (default: 5)
  --hmv-mode                HMV audio beat-sync (UDP 45736 and 45737, bed speakers)
  --export-toy-tools        Export companion tools to output/Telemetry_Suite/ (telemetry must be on)
```

---

## How the code is organised

`WB_Mobile_Patcher.py` is a thin launcher. The work is done by the `wbp/` package:

| Module | Contains |
|---|---|
| `wbp/common.py` | logger, `guarded_replace()` and the patch-miss list, `gml()` loader, `ROOT_DIR` |
| `wbp/axml.py` | binary `AndroidManifest.xml` editor (phone mod sharing) |
| `wbp/detect.py`, `wbp/env.py` | engine/base-APK detection; Python, Java, UndertaleModCli and signer lookup |
| `wbp/profiles.py` | one profile per engine: which names it reads natively, which packs it can list, how partner descriptors are written |
| `wbp/descriptors.py` | one descriptor per pack, converted for the target engine (ModRoom `.wife`, v1.5 `.spouse` / `.futa` with `[info]`) |
| `wbp/packs.py` | pack classification, the filename-bridge planner shared by the packer and the validator, duplicate/incompatible skipping, manifests, asset gathering |
| `wbp/engines.py` | ModRoom v3.3 and Wife's Bedroom v1.5 bytecode patchers, variable shield |
| `wbp/gml_patches.py` | the dynamic (fallback) GML patchers |
| `wbp/toy.py`, `wbp/toy_native.py` | ToyBridge / telemetry integration; `toy_native.py` applies the toy game-code patches (snippets in `core/gml_patches/native_toy/`) |
| `wbp/wbconv.py` | strip padding/cropping and name rules shared with the two converters (one of four identical copies: both converters, this tool and the Custom Studio backend; `python tools/sync_wbconv.py` keeps them equal, `--check` only reports) |
| `wbp/apk.py` | repackaging, signing, `patch_game_apk()` |
| `wbp/cli.py` | prompts and `main()` |

The Deeproom engine's GML (what `core/mobile_engine.bundle` contains) is edited as plain files in `core/bundle_src/`; run `python tools/bundle_tool.py pack` to rebuild the bundle and `python tools/bundle_tool.py check` to confirm it matches.

The GML text that the fallback patchers look for and insert is kept in `core/gml_patches/<function>/<name>.gml`, one file per string, read byte-for-byte. Edit those files to change a patch; do not re-wrap their line endings (`.gitattributes` marks them as non-text).

### Checking a change did not alter the output

`python -m unittest discover -s tests` runs the unit tests (including a check that every code excerpt in `core/TECHNICAL_SPECIFICATION.md` is shipped code). `python tests/golden_harness.py` runs the real pipeline on the example games (default folder `E:/MEGA/io`, override with `--io` or `WBP_IO`) and compares hashes of every patched GML script, every APK entry and the list of missed patch anchors with `tests/golden.json`. It prints `RESULT: IDENTICAL` when nothing changed. After an intended change, run `python tests/golden_harness.py --record` to accept the new output. Scenarios whose input folders are missing are reported as skipped, not passed.

## Known limitations

- Builds have been checked by compiling, signing and inspecting the APK, not by playing them on a phone. The phone mod-sharing activity and the touch fixes in particular are untested on a device.
- ModRoom (`_0.png`) and standard-name strips use different frame counts. When a pack is renamed between the two, the tool pads the strips with blank frames (nothing lost); strips that would need frames dropped (such as a partner X-ray 4 to 3) are only converted with `--approximate`, otherwise they are renamed as they are and may look offset. `output/<apk>_format_notes.txt` lists what happened. Wife's Bedroom v1.5 cannot read ModRoom-format packs at all.
- Most standard-format (`.spouse`) partner packs have no forward cowgirl; in ModRoom builds the reverse cowgirl is copied (padded to 11 frames) to stand in for it, so the animation may not look exactly as the author intended.
- Descriptor conversion adds keys but does not convert ModRoom's portrait hit boxes (`kiss_box_position` etc.) to Deeproom's offsets.
- ModRoom has no Deeproom-style touch overlay (drawer, touch-and-hold radial menu): its game code has no touch handling, and that overlay belongs to Deeproom's own code. It gets touch scrolling, the two-column pill menu and release-based background picks only.
- The toy features (direct client, UDP, HMV and the latency compensation) are applied and compile, but have not been tried with a real toy.
- Not changed because they need a device test: a touch long-press for portrait/outfit changes, larger touch targets, drawer scroll momentum.
- The fallback patchers for older game builds miss many anchors on current games (see `output/<apk>_patch_report.txt`); Deeproom 4.0.3 uses the bundled engine instead.

## Troubleshooting

- **"Python is required" although Python is installed**: reinstall with *Add python.exe to PATH*, or install the Python launcher (`py`). The Microsoft Store placeholder `python` doesn't count.
- **The build stops with an error**: open `patch_overlay_latest_error.log` next to the `.bat`; it names the failed stage and the reason.
- **A character or room is missing in the game**: check `output/<apk name>_skipped_packs.md`; it lists every pack that was left out and how to include it. In a ModRoom build the usual reason is a missing sprite.
- **A character looks offset or cut up**: check `output/<apk name>_format_notes.txt`; it lists packs whose strips were renamed between formats (the formats cut frames differently).
- **ModRoom shows "Variable Index [0] out of range [0] - custom_background_name_array"**: fixed in this version (the bedroom list is now filled by the game's own check). Rebuild; if it still appears, send the error text.
- **ModRoom shows "draw_sprite_ext ... requested -1"**: a pack with a missing sprite was listed. Rebuild with this version (it skips such packs and guards the draw) and send the error text if it still appears.
- **"Permission denied" on an APK in `output/`**: another program has the previous build open (a phone or cloud sync such as MEGA, the Explorer preview pane, an antivirus scan). The patcher waits a few seconds and, if the file is still locked, writes the new build as `<name>_<date-time>.apk` and tells you; delete the old file once it is released. Pausing sync for the `output/` folder avoids it.
- **The phone refuses to install**: allow *install unknown apps* for the app you opened the file with, and uninstall an older build that was signed differently.

## Third-party components

| Component | Location | License |
|---|---|---|
| UndertaleModCli (UndertaleModTool) | `core/UndertaleModCli/` | GNU GPL v3 (`core/UndertaleModCli/LICENSE.txt`); source at <https://github.com/UnderminersTeam/UndertaleModTool> |
| uber-apk-signer | `core/uber-apk-signer.jar` | Apache License 2.0; <https://github.com/patrickfav/uber-apk-signer> |

**Signing key:** `core/apkpatcher.keystore` and its password file are shared by everyone who uses this repository, so every build is signed with the same key. That lets builds from different people update each other, but it also means anyone with the repository can sign an APK that installs as an update.

Further reading:

- [`core/TECHNICAL_SPECIFICATION.md`](core/TECHNICAL_SPECIFICATION.md): how each enhancement works inside the game, with an audit note per section.
- [`core/ENGINE_ARCHITECTURE_REPORT.md`](core/ENGINE_ARCHITECTURE_REPORT.md): how ModRoom, Deeproom and v1.5 load packs, which descriptor files and keys each reads, frame counts, X-ray details and the conversion plan.
- [`core/CHANGELOG.md`](core/CHANGELOG.md): what changed in each version.
