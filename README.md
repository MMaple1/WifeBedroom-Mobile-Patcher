# WB Mobile Patcher v1.2

WB Mobile Patcher turns your PC game folder or mod zip archive into a signed Android app you can install and play on your phone or tablet.

## Start here

1. Install two free programs: Python (from python.org; check "Add python.exe to PATH") and Java (from adoptium.net, version 17 or newer).
2. Put your original Android game file (`wifes_bedroom1_4.apk` or `wifes_bedroom1_5.apk`) into the `input` folder.
3. Drag your game or mod folder (or its `.zip` file) onto `WB_Mobile_Patcher.bat`.
4. Press Enter for every question to accept the recommended default settings.
5. Wait a few minutes. When you see "Success", open the `output` folder to find your finished app. Copy it to your phone and install it.

**If something goes wrong:**
- *"Python" or "Java" not found:* Install them from the links above, restart your computer, and try again.
- *The window closes immediately:* Open Command Prompt in this folder and type `py -3 WB_Mobile_Patcher.py` to view the error message.
- *Characters are missing:* Check the `_skipped_packs.md` file in `output` to see which ones were skipped and why.
- *Install fails on phone:* Remove older versions of the game from your phone first, and make sure your file manager has permission to install unknown apps.
- *Other issues:* Check `patch_overlay_latest_error.log` next to the `.bat` file for full failure details.

## Using it on the phone

- *Add a mod:* Tap **ADD MOD** on the title screen and paste a link (`https://...`) or the file's location on the phone (for example `/sdcard/Download/mod.zip`), or use **Share / Open with** on a `.zip` file in your phone file manager.
- *Remove a mod:* Tap **REMOVE MOD** and choose the mod to delete; the game will restart.
- *Voices:* Added voice packs show up under **VOICES**; select the pack and assign it to a character.
- *Storage access issues:* If the game cannot open a file directly, send it using **Share / Open with** instead.

## The questions it asks

- **Default installation:** Choose yes for standard settings (Default: Yes).
- **Skip duplicate packs:** Avoids duplicate content by keeping only the best copy (Default: Yes).
- **Align X-ray overlays:** Fixes off-center X-ray graphics for Deeproom characters (Default: Yes).
- **Clean old builds:** Deletes previous APK builds from the output folder before starting (Default: No).
- **Fast packaging:** Skips asset compression to create test builds more quickly (Default: No).
- **Toy integration:** Enables optional interactive hardware support (Default: No).

## What you get in output/

- **Signed APK file:** Your finished Android game app ready to install on your device.
- **Skipped-packs report:** A list explaining any mod packs that were left out and why.
- **X-ray origins list:** Deeproom notes showing which character overlays were realigned.
- **Format notes:** Explanations of animation strips adjusted between different game formats.
- **Error log** (next to the `.bat`, not in `output/`): `patch_overlay_latest_error.log` explains the last failed build.

## Which game file to use

| Your mod | Base APK to provide | Notes |
|---|---|---|
| **Deeproom 4.0.3 Kiwami** | `wifes_bedroom1_4.apk` (or `wifes_bedroom.apk`) | Full mobile touch controls, custom backgrounds, audio support, and in-game calibration. |
| **ModRoom v3.3** | `wifes_bedroom1_4.apk` (or `wifes_bedroom.apk`) | Mobile mod index loading, clean disclaimers, and auto-generated forward cowgirl animations. |
| **Wife's Bedroom v1.5** | `wifes_bedroom1_5.apk` | Native mobile layout, streamlined file streaming, and unified mod packaging. |

## Command line

```text
py -3 WB_Mobile_Patcher.py -b input/wifes_bedroom1_4.apk "My Mod Folder"
py -3 WB_Mobile_Patcher.py -y -b input/wifes_bedroom1_4.apk "My Mod.zip"
py -3 WB_Mobile_Patcher.py --clean --fast -b input/wifes_bedroom1_5.apk "Mod_v15"
py -3 WB_Mobile_Patcher.py --validate-only "My Mod Folder"
```
See DETAILS.md for all options.

**Signing:** your first build makes a personal signing key in `%USERPROFILE%\.wb_mobile_patcher`; back that folder up, because only the same key can update an app you installed. An app built before 2026-11-18 used a shared key: uninstall it before installing a new build (back up your saves first), or keep updating it with `--legacy-key`.

**Deeproom partners' deepthroat too high?** Packs converted for Deeproom before 2026-11-17 carry a `[deepthroat]` block that draws it 66-70 px high, on PC and in the APK. Before building, run the WB_Converters tool: `py -3 WB_1.5_to_Modded.py --repair-deepthroat "<Deeproom>/custom_stuff/custom_wives"` lists them and asks before fixing (`-y` applies, `--dry-run` only lists; originals are backed up to a zip next to the folder).

For technical architecture and in-depth modding details, see DETAILS.md and core/TECHNICAL_SPECIFICATION.md.
