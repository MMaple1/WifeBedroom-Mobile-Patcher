# Engine Architecture & Sprite Loading Comparative Report
**Wife's Bedroom v1.5 vs. Deeproom 4.0.3 Kiwami vs. ModRoom v3.3**

---

## 1. Executive Summary

This report documents the internal GameMaker bytecode mechanisms, sprite loading routines (`sprite_add`), coordinate systems, descriptor schemas, and memory caching architectures across the three primary game engines:
1. **Wife's Bedroom v1.5** (Modern unified engine)
2. **Deeproom 4.0.3 Kiwami** (Expanded modded engine with 184-sprite atlas)
3. **ModRoom v3.3** (Legacy PC modding engine, ~8.1MB)

> **How to read this report (updated 2026-11-16).** Sections 2-7 are the original comparison. Sections 8-11 and Appendix A were added after checking each claim against the games' own code (UndertaleModCli dumps of ModRoom V3.3, Deeproom 4.0.3 and v1.5), the shipped bundle and the patcher: section 8 lists corrections to sections 2-7 and what the patcher does about them, section 9 the data files each version prefers, section 10 the plan for one converted descriptor per export, section 11 X-ray strips and origins, Appendix A the full key matrix. **Where they disagree, trust sections 8-11.** Nothing here was tested on a device.

---

## 2. Sprite Loading & Memory Architecture Comparison

| Architectural Feature | ModRoom v3.3 (Legacy) | Deeproom 4.0.3 Kiwami | Wife's Bedroom v1.5 |
| :--- | :--- | :--- | :--- |
| **Loading Mechanism** | Direct `sprite_add` per character load | Direct `sprite_add` per character load | Cached via `custom_sprite_storage` DS Map (`func_replace_custom_sprite`) |
| **Memory Cleanup** | `sprite_delete` before loading new pack | `sprite_delete` before loading new pack | Retained in DS Map to prevent redundant disk reads |
| **Audio Loading** | Direct file streaming | Direct file streaming | Streaming via `custom_audio_storage` DS Map (`func_get_moan_audio`) |
| **Startup Asset Indexing** | Loops all directories into `ds_list` | Loops all directories into `ds_list` | Loads all animations at boot (unpatched) / Metadata-only (patched) |

---

## 3. Sprite Frame Counts & Registration Origins

### A. Lover (Futa / Top) Sprites

| Sprite Type | Filename | ModRoom v3.3 | Deeproom 4.0.3 | Wife's Bedroom v1.5 |
| :--- | :--- | :--- | :--- | :--- |
| **Portrait** | `custom_portrait.png` / `custom_futa_portrait_0.png` | 10f or 17f `(64, 64)` | 10f or 17f `(64, 64)` | 10f `(64, 64)` |
| **Mating Press** | `custom_mating_press.png` / `custom_futa_mating_press_0.png` | 9f (1440px) or 24f | 9f (legacy) or 24f (Kiwami) | 9f (1440px) |
| **Cowgirl** | `custom_reverse_cowgirl.png` / `custom_futa_cowgirls_0.png` | 19f (single combined sheet) | 19f (`cowgirl_origin_x, y`) | 5f (or 7f if width > ox * 10) |
| **Deepthroat** | `custom_deepthroat.png` / `custom_futa_deepthroat_0.png` | Not Supported | 9f (partner) / 24f (futa) | 9f `(80, 84)` |
| **X-Ray** | `custom_xray.png` / `custom_futa_xray_0.png` | 3f (80, 84) or 18f | 3f (legacy) or 18f (Kiwami) | 3f `(xray_x, xray_y)` |
| **Condom Normal** | `custom_condom.png` | 2f `(80, 84)` | 2f `(sprite_origin_x, y)` | 2f `(80, 84)` |
| **Condom Broken** | `custom_condom_broken.png` | Not Supported | 2f `(sprite_origin_x, y)` | 2f `(80, 84)` |
| **Sperm Ejaculation**| `custom_sperm.png` | Not Supported | 4f (24, 24) | 4f `(0, 0)` |
| **Ball Clench** | `custom_futa_bc.png` / `custom_ballclench.png` | Not Supported | 5f `(22, 0)` or 6f `(79, 112)`| Not Supported |
| **Ball Clench Crest**| `custom_futa_bccrest.png` / `custom_ballclenchcrest.png` | Not Supported | 5f `(22, 0)` or 6f `(79, 112)`| Not Supported |

### B. Partner (Wife / Spouse / Bottom) Sprites

| Sprite Type | Filename | ModRoom v3.3 | Deeproom 4.0.3 | Wife's Bedroom v1.5 |
| :--- | :--- | :--- | :--- | :--- |
| **Portrait** | `custom_portrait.png` / `custom_wife_portrait_0.png` | 17f `(64, 64)` | 10f or 17f `(78, 80)` | 10f (`custom_portrait_alt.png`) |
| **Mating Press** | `custom_mating_press.png` / `custom_wife_mating_press_0.png`| 5f `(80, 84)` | 4f (legacy) or 5f (Kiwami) | 4f (`custom_mating_press_alt.png`)|
| **Forward Cowgirl**| `custom_cowgirl.png` / `custom_wife_cowgirl_0.png` | 11f `(80, 84)` | 11f `(cowgirl_origin_x, y)` | 6f (`custom_forward_cowgirl_alt.png`)|
| **Reverse Cowgirl**| `custom_reverse_cowgirl.png` / `custom_wife_reverse_cowgirl_0.png`| 10f `(80, 84)` | 10f `(cowgirl_origin_x, y)` | 5f (`custom_reverse_cowgirl_alt.png`)|
| **Deepthroat** | `custom_deepthroat.png` / `custom_wife_deepthroat_0.png` | Not Supported | 5f (`dt_origin_x, y`) | 5f (`custom_deepthroat_alt.png`)|
| **X-Ray** | `custom_xray.png` / `custom_wife_xray_0.png` | 3f `(80, 84)` | 4f (`xray_origin_x, y`) | 3f `(80, 84)` |

---

## 4. Facial Expression & Layering Innovations

### A. Deeproom 4.0.3 Subimage Compositing
Deeproom 4.0.3 composites portraits from a single 10- or 17-frame horizontal strip:
* **Frame 0**: Hair Back
* **Frame 1**: Head Base
* **Frame 2**: Boobs
* **Frame 3**: Torso
* **Frame 4**: Closed Mouth (Frame 5 = Open Mouth)
* **Frame 6**: Bangs
* **Frame 7**: Open Eyes (Frame 11 = Orgasm Eyes)
* **Frame 8**: Eyebrows
* **Frame 9**: Front Hair
* **Frame 12**: Facial Blush

### B. Wife's Bedroom v1.5 External Layer Overlays
In addition to the portrait strip, v1.5 supports standalone overlay files that are dynamically swapped during gameplay:
* `custom_eyes.png` (4 frames) / `custom_eyes_alt.png` (4 frames)
* `custom_mouth.png` (7 frames) / `custom_mouth_alt.png` (7 frames)
* `custom_nipple` coordinates: `[nipple_x, nipple_y]` defined in `[portrait]` section.
* `custom_flat` / `custom_flat_alt`: Boolean flag in `[stats]` that removes chest bounce physics for flat-chested characters.

---

## 5. Descriptor Schemas & INI Section Differences

### A. Root Descriptor Filenames
* **ModRoom v3.3**: `custom_data.futa`, `custom_data.wife`, `custom_data.bedroom`
* **Deeproom 4.0.3**: `custom_data.futa`, `custom_data.spouse` (or `custom_data.wife`), `custom_data.bedroom`
* **Wife's Bedroom v1.5**: `custom_data.futa`, `custom_data.spouse`, `custom_data.bedroom`

### B. Section-by-Section Key Mappings

#### 1. Identity & Metadata
* **v1.5 Only**: Requires `[info]` section (`name`, `desc`, `author`). Clamped to 36 characters.
* **ModRoom & Deeproom**: Character names are derived from the folder name on disk; `[info]` is ignored.

#### 2. Origins & Alignment Fallback Hierarchy
* **Deeproom 4.0.3**:
  ```ini
  [sprite]
  origin_x = 80       ; Global fallback
  origin_y = 84
  
  [mating_press]      ; Pose-specific overrides
  origin_x = 80
  origin_y = 84
  
  [deepthroat]
  origin_x = 80
  origin_y = 84
  
  [xray]
  origin_x = 80
  origin_y = 84
  ```
* **Wife's Bedroom v1.5**:
  ```ini
  [sprite]
  origin_x = 80
  origin_y = 84
  deepthroat_origin_y = 150
  xray_x = 80
  xray_y = 84
  condom_y = 78
  standing_condom_y = 0
  ```

#### 3. In-Game Dialogue Specifications
* **ModRoom v3.3**: Dialogue is written directly inside the INI file (`[dialogue]` section).
* **Deeproom 4.0.3**: Dialogue can be in the INI file OR in standalone scene override JSONs (`custom_stuff/dialogue_packs/<name>.json`).
* **Wife's Bedroom v1.5**: Dialogue is stored inside the character folder as `dialogue.json` (Lover) and `dialogue_alt.json` (Partner).

---

## 6. Directory Layouts Across Engines

### A. ModRoom v3.3 Architecture (Root-Level Categories)
```text
game_root/
├── custom_futas/
│   └── char_name/
│       ├── custom_futa_portrait_0.png
│       ├── custom_futa_mating_press_0.png
│       ├── custom_futa_cowgirls_0.png
│       ├── custom_futa_xray_0.png
│       └── custom_data.futa
├── custom_wives/
│   └── wife_name/
│       ├── custom_wife_portrait_0.png
│       ├── custom_wife_mating_press_0.png
│       ├── custom_wife_cowgirl_0.png
│       ├── custom_wife_reverse_cowgirl_0.png
│       └── custom_data.wife
└── custom_bedrooms/
```

### B. Deeproom 4.0.3 Kiwami Architecture (`custom_stuff/` Container)
```text
game_root/
└── custom_stuff/
    ├── custom_futas/
    │   └── char_name/
    │       ├── custom_portrait.png
    │       ├── custom_mating_press.png
    │       ├── custom_reverse_cowgirl.png
    │       ├── custom_deepthroat.png
    │       ├── custom_xray.png
    │       └── custom_data.futa
    ├── custom_wives/
    │   └── wife_name/
    │       └── custom_data.spouse
    ├── custom_bedrooms/
    ├── custom_sounds/
    └── dialogue_packs/
```

### C. Wife's Bedroom v1.5 Architecture (Unified `custom/`)
```text
game_root/
└── custom/
    ├── char_name/
    │   ├── custom_portrait.png
    │   ├── custom_mating_press.png
    │   ├── custom_reverse_cowgirl.png
    │   ├── custom_deepthroat.png
    │   ├── custom_xray.png
    │   ├── custom_eyes.png          ; (Optional v1.5 overlay)
    │   ├── custom_mouth.png         ; (Optional v1.5 overlay)
    │   ├── dialogue.json            ; (Character-assigned dialogue)
    │   └── custom_data.futa         ; (Contains [info] section)
    └── _manifest.txt
```

---

## 7. Actionable Recommendations for Tool Suite Implementation

1. **Custom Studio Support for v1.5 Separate Eye/Mouth Overlays**:
   * Add support in `drawCanvas()` and `loadActivePackSprites()` to check for `custom_eyes.png` and `custom_mouth.png` and render them as optional toggles over `custom_portrait.png`.
2. **Custom Studio `[xray]` Origin Sliders**:
   * Add specific sliders for `[xray] origin_x / origin_y` (partner) and `[sprite] xray_offset_y` (lover) in the Studio UI so modders can visually line up the cervix and shaft directly in the preview canvas.
3. **Patcher Auto-Conversion of v1.5 Eye/Mouth Overlays for ModRoom/Deeproom**:
   * When compiling for ModRoom or Deeproom, if a v1.5 pack uses separate `custom_eyes.png` or `custom_mouth.png` files, the patcher or converter can bake them into composite subimages so they appear in older engines.


---

## 8. Review notes (2026-11-16, checked against the games and the patcher)

Sources: native `data.win` of ModRoom V3.3, Deeproom 4.0.3 and Wife's Bedroom v1.5 (code dumped with UndertaleModCli), each game's templates and readme, the PNG widths of every example folder, the shipped Deeproom bundle and `wbp/packs.py`. Nothing was tested on a device.

**Confirmed**
- Section 3 frame counts. Measured strip widths (frames = width / 160 px for the usual 160 px frames; corrected 2026-11-17: the games cut a strip into a fixed NUMBER of frames whatever its width, so high-res packs with 256 px portraits or 220 px mating-press frames are valid, and portrait frames are usually 128 px): futa portrait 10 (standard) / 17 (`_0`), futa mating press 9 / 24, futa X-ray 3 / 18, wife portrait 10 / 17, wife mating press 4 / 5, wife reverse cowgirl 5 / 10, wife X-ray 4 / 3, wife forward cowgirl 11. Deepthroat is 5 frames for wives and 9 for futas.
- v1.5's partner format equals Deeproom's legacy **spouse** format (standard names; 4/10/5/5/4 frames; `.spouse`). v1.5's lover format equals the legacy futa format (10/9/3/2).

**Needs correction**
- Section 3B puts "Reverse Cowgirl 10f" and "X-Ray 4f" in the Deeproom column. Deeproom has both formats: 10f and 3f belong to `.wife` + `_0.png`; 5f and 4f belong to `.spouse` + standard names.
- Section 5B.2 shows the `[mating_press]` / `[deepthroat]` / `[xray]` origin sections as "the Deeproom schema". That is the **spouse** schema. The Deeproom **wife** loader reads flat `[sprite]` keys (`mating_press_origin_x/y`, `deepthroat_origin_x/y`, `cowgirl_origin_x/y`), `[stats] bottom_boob_size/bottom_ass_size` and `[gender] is_male`; the spouse loader also reads `[stats] max_orgasms`.
- Section 5A says Deeproom accepts `custom_data.spouse` "(or `custom_data.wife`)" and ModRoom `custom_data.wife`. ModRoom's native wife loader accepts **only** `.wife` (it has no `.spouse` support); the patched ModRoom build adds `.spouse`. Deeproom natively reads both, using different loaders. v1.5 natively reads `.futa`, `.spouse`, `.bedroom` only (the patcher adds `.wife`).
- Section 5B.1 says `[info]` is ignored by ModRoom and Deeproom. True for the engines' loaders; the patcher still reads `[info] name` from `.futa`, `.spouse`, `.wife`, `.bedroom` for display names.
- Missing: ModRoom's `[portrait]` hit boxes (`kiss_box_position`, `boob_box_position`, `portrait_change_position`, `portrait_eye_track_position`, pipe-separated) are not the same keys as Deeproom's (`kiss_x_offset/y`, `boob_x_offset/y`, `headpat_x_offset/y`).
- Missing: the loader routing rules. Deeproom's wife loader switches to the spouse loader when `custom_data.spouse` or `custom_mating_press.png` exists, or `custom_wife_mating_press_0.png` is missing; its futa loader takes the legacy 9-frame path whenever `custom_mating_press.png` exists.
- Section 6A shows ModRoom wives as `.wife`. The `ModRoom V3.3` example folder also holds `.spouse` packs; those only load in the patched build.

**Patcher consequences (changed 2026-11-16)**
- The pre-flight pack check no longer rejects ModRoom-style names (`_0.png`, `_alt_N.png`) for ModRoom and Deeproom targets. ModRoom's own loaders build exactly those names (`_suffix = "_0.png"` or `"_alt_" + N + ".png"`), and the check had been skipping 13 of 20 packs in the ModRoom V3.3 example folder. ModRoom's futa loader, like Deeproom's, switches to the legacy path when `custom_mating_press.png` exists, so native packs are also left without standard-named copies. v1.5 still skips them (it reads standard names only).
- ModRoom's own scan (`Create_0`) lists a lover pack only when `check_custom_futa` finds portrait, mating press, cowgirls and X-ray, and a partner pack only when `check_custom_wife` finds the descriptor plus forward cowgirl, reverse cowgirl and mating press (portrait is optional and only sets `custom_wife_has_portrait`). The Android patch replaced that scan with a manifest list that skipped these checks and forced `custom_wife_has_portrait = true`; the result was `draw_sprite_ext argument 1 invalid reference to (sprite) - requested -1` in `Draw_0`. The build now applies the same rules before it writes the manifest, `custom_wife_has_portrait` is set only on load, and `Draw_0` draws through a guard that skips a -1 sprite. Spouse-format partner packs (no forward cowgirl) are therefore skipped for ModRoom, with the reason in the skipped-packs report.
- ModRoom's `Draw_0` contains no touch handling at all (no `device_mouse_*`, `os_android` or touch code), and its `menu_scroll_update` reads only the mouse wheel. The tool therefore adds touch-drag scrolling to that function, lays the 14-pill menu out as two columns of 7, and picks a background on release. ModRoom's own bedroom scan calls `func_check_custom_background()` per folder, which fills `custom_background_name_array`; skipping that call (as the manifest loop did) made the Draw event read an empty array (`Variable Index [0] out of range [0]`).
- Each build now writes files and index manifests only into the directory its engine reads (Deeproom `custom_stuff/custom_*`, ModRoom root `custom_*`, v1.5 `custom/`). Deeproom's code prefers `custom_stuff/<category>/_manifest.txt` and treats the root `custom_*` path as a fallback; ModRoom reads the root path first. The old extra manifests created folders that held only manifests.
- Deeproom builds keep ModRoom-format packs as authored. The patcher used to add standard-named copies and a `.spouse` file, which sent them to the legacy loaders with the wrong frame counts. It also no longer adds a `.wife` clone to every `.spouse` pack.
- ModRoom builds no longer add futa-named files to wife packs or the reverse, and list renamed wife packs in `output/<apk>_format_notes.txt` (the renamed strip keeps its frame count).
- v1.5 builds list packs in the ModRoom (`_0.png`) format in the same notes file, because v1.5 reads standard names only. v1.5 handling of packs in its own format is unchanged (the v1.5 build output is byte-identical to before).
- See spec section 68 (DR-57) for the tables.

**Recommendations**
- Section 7 items 1-3 are not implemented in the patcher. Item 3 (baking overlays) and padding wife strips for ModRoom both need image processing, which the patcher does not use (standard library only).
- A converter that pads or crops strips to the target frame counts would make the cross-format copies correct instead of merely listed.


---

## 9. Which data files each version prefers

Verified from the native `data.win` code of each game (UndertaleModCli dump of `func_load_custom_futa/wife/spouse` and v1.5's `func_load_custom`). "Preferred" means the file the engine's own loader and templates are built around.

| | ModRoom V3.3 | Deeproom 4.0.3 | Wife's Bedroom v1.5 |
|---|---|---|---|
| Lover descriptor | `custom_data.futa` | `custom_data.futa` | `custom_data.futa` |
| Partner descriptor | `custom_data.wife` (the only one it knows) | `custom_data.spouse` preferred; `custom_data.wife` only for modern `_0.png` packs | `custom_data.spouse` (no `.wife`) |
| Bedroom descriptor | not checked | `custom_data.bedroom` | `custom_data.bedroom` |
| Sprite names | lover: standard = legacy, `custom_futa_*_0.png` = modern; partner: `custom_wife_*_0.png` only | both sets; standard names win (legacy loader) when `custom_mating_press.png` exists | standard names only; partner strips of a lover folder use `_alt` names |
| Folder | `custom_futas/`, `custom_wives/`, `custom_bedrooms/` next to the exe | `custom_stuff/custom_*` | `custom/` (or next to the exe), one folder per character, type found from the descriptor |
| `[info]` block | not read | not read | read (`name`, `desc`, `author`) |
| Templates in the game folder | `custom.futa`, `custom.wife` | `Templates/Futa`, `Templates/Wife` (ModRoom style, `.wife` + `_0.png`) | `templates/custom lover|partner|bedroom template` (`.futa` / `.spouse` / `.bedroom`, standard names) |

Notes:
- ModRoom's native wife loader has no `.spouse` branch. Deeproom has two partner loaders, chosen by file presence (see section 8). v1.5 patched by this tool also accepts `.wife`.
- Patched Deeproom bundle (2026-11-17): sprite origins are read exactly as in the native game (packs are tuned against it); only X-ray origins may be replaced by measured ones (install option). The lover loader uses the standard names when `custom_mating_press.png` exists or `custom_futa_mating_press_0.png` is missing (the same rule on PC and phone; an earlier patch had forced the standard-name loader on Android); select-screen and in-game portraits use the same choice, with 10 or 17 frames picked by which count divides the width.
- A v1.5 partner pack and a Deeproom legacy spouse pack are the same format (standard names; 4/10/5/5/4 frames). ModRoom's wife format is Deeproom's modern wife format.
- Deeproom's patched bundle also accepts v1.5's `[sprite] xray_x/xray_y` for the X-ray origin, as a fallback: since 2026-11-16 `[xray] origin_x/y` (the native Deeproom key) is read first. See section 11.

## 10. Goal: one descriptor per export, variables converted

Target state: for each pack, a build writes exactly one descriptor, in the name and key layout the target engine reads, with sprites named and cut for that engine.

**Where the tool is today (implemented 2026-11-16 in `wbp/descriptors.py`)**

| Target | Descriptor written now | Conversion |
|---|---|---|
| Deeproom | the pack's own file, untouched | none (it reads `.spouse` and `.wife` natively) |
| ModRoom | one `custom_data.wife` per partner pack. A `.spouse` pack is converted; a real `.wife` is kept and any `.spouse` next to it is dropped | per-pose origins copied into the flat `[sprite]` keys (class 2) |
| v1.5 | one descriptor per pack: a `.wife` pack becomes `custom_data.spouse`; `.spouse` and `.futa` files get `[info] name` (the folder name) when they have none | flat `[sprite]` keys copied into per-pose sections; `[xray]` origin and deepthroat height copied into `[sprite] xray_x/xray_y/deepthroat_origin_y` |

The conversion is additive: every source key is kept, only absent keys are added, values are never changed, line endings, BOM and unknown lines are preserved, and a file that needs no change is passed through byte for byte. Packs holding both a `.futa` and a `.spouse`/`.wife` descriptor are left alone. Classes 3 (portrait hit boxes) and 5 (strip frame counts) below are still not converted.

**What a conversion has to do** (key matrix in Appendix A; `x` = the loader reads it)

1. *Same name, same meaning: copy.* Partner: `[sprite] origin_x/y`, `[portrait] origin_x/y` (all four loaders). Lover: `[portrait] origin_x/y`, `[sprite] origin_x/y`, `[sprite] condom_y`, `[stats] max_orgasms`. The `[personality]` block is shared by the ModRoom wife, Deeproom spouse and Deeproom wife loaders.
2. *Same meaning, different layout: rename.* Partner pose origins: Deeproom spouse `[mating_press] origin_x/y`, `[deepthroat]`, `[reverse_cowgirl]`, `[xray]` map to Deeproom wife `[sprite] mating_press_origin_x/y`, `deepthroat_origin_x/y`, `cowgirl_origin_x/y`; v1.5 uses `[sprite] xray_x/xray_y` and `[sprite] deepthroat_origin_y`. ModRoom's `.wife` has only `[sprite] origin_x/y`, so per-pose origins have nowhere to go when exporting to ModRoom.
3. *Different representation: needs a decision.* Portrait hit boxes: ModRoom stores `kiss_box_position`, `boob_box_position`, `portrait_change_position`, `portrait_eye_track_position`; Deeproom stores `kiss_x/y_offset`, `boob_x/y_offset`, `headpat_x/y_offset`; v1.5 stores `head_offset` and `nipple_x/y/size`. The meaning of ModRoom's pipe values has not been checked against the other two, so no automatic conversion is safe yet.
4. *Engine-only keys: keep or drop.* `[info] name/desc/author` exist only for v1.5 (fill `name` from the folder name when exporting to v1.5; drop elsewhere). Deeproom-only keys (`womb_fill`, `climax`, extra pills, `[CondomPos]`, `[CumPos]`, `[BallClench]`) have no ModRoom or v1.5 counterpart.
5. *Sprites change with the descriptor.* Each format cuts a strip into a different number of frames (section 8 and spec section 68). A descriptor can only be converted completely if the strips are padded or cropped to match, which needs image processing; the patcher is standard-library only today.

**How the tool is organised for this (2026-11-16).** `wbp/profiles.py` holds the per-engine rules (native names, which packs the engine can list, partner descriptor name). `plan_name_bridge()` is the one planner of filename copies, shared by the packer and the pre-flight check; a pack is judged on its files plus those copies. A pack is skipped only for what conversion cannot fix: no descriptor, sprites in the wrong folder, a numbered `custom_data_N` file, a strip format the engine cannot read (v1.5 and `_0.png`), or sprites the engine needs and the pack lacks (ModRoom).

**Frame maps learned from hybrid packs (2026-11-16).** Packs that carry both naming sets show which frames correspond: lover mating press 24 to 9 is modern frames 0-7 and 19 (4 packs, every frame agreed), lover cowgirl 19 to 5 is 0, 1, 2, 14, 17 (4 packs), partner mating press 5 to 4 is 0-3 (10 packs). Portraits (17 to 10) and several other strips do not map frame for frame. The converters use these maps only in `--approximate` mode.

**Converters (2026-11-16).** The sibling converters `Modded_to_WB_1.5` and `WB_1.5_to_Modded` (v1.2) now implement the strip and descriptor side of this plan with a shared, tested, standard-library-only module (`core/wbconv.py`): PNG pad/crop, the frame table of section 8, one descriptor per pack, ModRoom's admission rules, and a per-pack conversion report. They pad where nothing is dropped, crop only the partner X-ray, and leave other strips and all portraits to `--approximate`. Not tested in the game.

**Suggested order of work**
1. **Done:** `wbp/descriptors.py` (classes 1, 2 and 4, no value changes; one file per pack).
2. **Done:** `tests/test_descriptors.py` (14 unit tests) and the golden harness (hashes every APK entry).
3. Settle class 3 by reading the ModRoom hit-box code and checking against Deeproom offsets on a device.
4. A small pure-Python PNG pad/crop step, then enable the strip conversions for packs whose descriptor was converted.

**Current limit to remember:** the descriptor now matches the target, but the strips next to it still keep the source format's frame counts (section 8); the loader choice depends on filenames. The ModRoom and v1.5 notes file (`output/<apk>_format_notes.txt`) lists affected packs.


## 11. X-ray sprites and origins (Deeproom)

Found while checking a modern `.wife` pack (`!Azure Dogwife`: `custom_data.wife`, `custom_wife_*_0.png` plus `_alt_1` / `_alt_2` variants) whose X-ray did not display correctly in Deeproom. Checked in the Deeproom bundle (`func_load_custom_wife`, `func_load_custom_spouse`, `func_get_wife_xray` and the X-ray drawing in `Draw_0`) and by measuring the strips. The frame roles below are read from the draw code; nothing was run on a device.

**Which sprites are drawn.** `func_get_wife_xray(bottom_sprite)` returns the wife X-ray strip that belongs to the mating-press sprite in use: `custom_wife_xray` when it is the modern wife mating press, `legacy_custom_wife_xray` when it is the legacy spouse one. That strip becomes `anatomy_sprite`; without a wife strip the lover's X-ray sprite (`xray_sprite`, e.g. `sFutaXray`) is used.

| Wife X-ray frame | Role (`Draw_0`) | Modern strip | Legacy strip |
|---|---|---|---|
| 0 | canal (`draw_sprite_ext(anatomy_sprite, 0, ...)`) | yes | yes |
| 1 | womb (`womb_frame = 1` when a wife strip exists) | yes | yes |
| 2 | cervix (`cervix_frame = 2`) | yes | yes; also the cum-pool layer (`draw_sprite_part_ext(anatomy_sprite, 2, ...)`) |
| 3 | not drawn anywhere | - | present in the file, unused |

In modern mode the cum-pool layer is taken from the **lover's** X-ray sprite (`xray_sprite`, frame 1), not from the wife strip. So a modern wife strip needs exactly frames 0, 1 and 2, and a 4-frame legacy strip has the same three frames in the same order plus an unused fourth.

**Frame counts per loader**

| Loader | X-ray file | Frames |
|---|---|---|
| Spouse (legacy) | `custom_xray.png` | 4 (640 px) |
| Modern wife | `custom_wife_xray_0.png` (and `_alt_N`) | 3 (480 px); 1-8 from the strip width since 2026-11-16 |
| ModRoom V3.3 | `custom_wife_xray_0.png` | 3 |
| v1.5 | `custom_xray.png` / `custom_xray_alt.png` | 3 (lover), 4 (partner `_alt`) |

**What went wrong with the example pack.** Every X-ray strip in it is 640 x 168 px (4 frames of 160 px, the legacy layout) but the pack is otherwise modern (cowgirl 11, mating press 5, reverse cowgirl 10, deepthroat 5, portrait 17 frames) and uses `.wife` + `_0.png`. The modern wife loader called `sprite_add(file, 3, ...)` for every X-ray, so the 640 px strip was cut into three 213 px slices and the canal, womb and cervix frames were cut at the wrong places.

**Origin keys.** The pack's descriptor holds both `[sprite] xray_x=50, xray_y=88` and `[xray] origin_x=90, origin_y=88`.
- Native Deeproom reads `[xray] origin_x/y` in the spouse loader. Native v1.5 reads `[sprite] xray_x/xray_y`. The native modern wife loader reads neither key.
- The bundle reads both in both partner loaders, clamps each to 40..120 (outside that range the default 80 / 84 is used), and rescales the offset when the loaded sprite is not 160 px wide.
- Before 2026-11-16 the bundle read `[sprite] xray_x` first. It now reads `[xray] origin_x/y` first and falls back to `[sprite] xray_x/xray_y`, so for this pack the origin is 90 / 88, not 50 / 88.

**Loader change (2026-11-16).** The modern wife loader now takes the X-ray frame count from the strip width: it loads the file once as a single frame, reads its width, deletes that probe sprite, and uses `width div 160` frames (1 to 8) when the width is a multiple of 160; otherwise it keeps 3. A 4-frame strip is therefore cut at 160 px, so frames 0, 1 and 2 (canal, womb, cervix) are the right ones, and the unused fourth frame is ignored. Because the draw code only uses frames 0-2 of a wife strip and takes the cum pool from the lover sprite in modern mode, such a pack should display correctly after the change. This follows from the code; it has not been seen in the game.

**Caveat (2026-11-16): pixel evidence from packs that ship both formats.** Comparing the 4-frame standard X-ray with the 3-frame modern X-ray of the same character (6 packs) matched standard frames 0, 1, 2, 3 to modern frames 0, 1, 1, 2 (the best match of standard frame 2 is the womb frame, and standard frame 3 resembles the modern cervix). That does not fit the reading above that standard frames 0-2 play the same roles as modern 0-2 and the 4th is unused, so which standard frame is the cervix is **unresolved**; the draw code and the pixel comparison disagree. The converters therefore treat the 4 to 3 X-ray crop as the first three frames and report it; check X-rays after converting.

**Fixing a pack by hand.** Cropping each X-ray strip to its first 3 frames (480 x 168 px) gives a valid modern strip with the same content. Alternatively make it a legacy pack: `custom_data.spouse` with standard names (`custom_xray.png` at 4 frames, and the other strips at 4/10/5/5 frames).

**Tool support still missing.** A pack converter that pads or crops strips to the target frame counts (section 10, class 5) would do this automatically. It needs image processing, which the patcher does not use yet (standard library only). For the X-ray strip the crop rule is now known: keep frames 0-2.

## Appendix A. Descriptor key matrix (generated from the native game code)

Generated 2026-11-16 by listing every `ini_read_real` / `ini_read_string` call in each loader. v1.5 has one loader that opens the `.futa` and `.spouse` files at different points; its keys are split by the file opened. Deeproom's partner loaders are the legacy `.spouse` one and the modern `.wife` one.

**Partner (wife / spouse) descriptor keys** (67 keys; x = read by that loader)

| Section | Key | ModRoom `.wife` | Deeproom `.spouse` (legacy) | Deeproom `.wife` (modern) | v1.5 `.spouse` |
|---|---|---|---|---|---|
| `[debug]` | `show_debug` | x |  |  |  |
| `[deepthroat]` | `origin_x` |  | x |  |  |
| `[deepthroat]` | `origin_y` |  | x |  |  |
| `[gender]` | `is_male` | x |  | x |  |
| `[info]` | `author` |  |  |  | x |
| `[info]` | `desc` |  |  |  | x |
| `[info]` | `name` |  |  |  | x |
| `[mating_press]` | `origin_x` |  | x |  |  |
| `[mating_press]` | `origin_y` |  | x |  |  |
| `[personality]` | `affection_response` | x | x | x |  |
| `[personality]` | `climax` |  | x | x |  |
| `[personality]` | `cum_response` | x | x | x |  |
| `[personality]` | `intensity_response` | x | x | x |  |
| `[personality]` | `pain_response` | x | x | x |  |
| `[personality]` | `reproductive_response` | x | x | x |  |
| `[personality]` | `size_response` | x | x | x |  |
| `[personality]` | `womb_fill` |  | x | x |  |
| `[pills]` | `contraceptive_pill` | x | x | x |  |
| `[pills]` | `eggxcelent_pill` |  | x | x |  |
| `[pills]` | `greedy_womb_pill` |  | x | x |  |
| `[pills]` | `ovulation_pill` | x | x | x |  |
| `[portrait]` | `boob_box_position` | x |  |  |  |
| `[portrait]` | `boob_x_offset` |  | x | x |  |
| `[portrait]` | `boob_y_offset` |  | x | x |  |
| `[portrait]` | `head_offset` |  |  |  | x |
| `[portrait]` | `headpat_x_offset` |  | x | x |  |
| `[portrait]` | `headpat_y_offset` |  | x | x |  |
| `[portrait]` | `kiss_box_position` | x |  |  |  |
| `[portrait]` | `kiss_x_offset` |  | x | x |  |
| `[portrait]` | `kiss_y_offset` |  | x | x |  |
| `[portrait]` | `nipple_size` |  |  |  | x |
| `[portrait]` | `nipple_x` |  |  |  | x |
| `[portrait]` | `nipple_y` |  |  |  | x |
| `[portrait]` | `origin_x` | x | x | x | x |
| `[portrait]` | `origin_y` | x | x | x | x |
| `[portrait]` | `portrait_change_position` | x |  |  |  |
| `[portrait]` | `portrait_eye_track_position` | x |  |  |  |
| `[reverse_cowgirl]` | `origin_x` |  | x |  |  |
| `[reverse_cowgirl]` | `origin_y` |  | x |  |  |
| `[sprite]` | `cowgirl_origin_x` |  |  | x |  |
| `[sprite]` | `cowgirl_origin_y` |  |  | x |  |
| `[sprite]` | `deepthroat_origin_x` |  |  | x |  |
| `[sprite]` | `deepthroat_origin_y` |  |  | x | x |
| `[sprite]` | `mating_press_origin_x` |  |  | x |  |
| `[sprite]` | `mating_press_origin_y` |  |  | x |  |
| `[sprite]` | `origin_x` | x | x | x | x |
| `[sprite]` | `origin_y` | x | x | x | x |
| `[sprite]` | `xray_x` |  |  |  | x |
| `[sprite]` | `xray_y` |  |  |  | x |
| `[stats]` | `bottom_ass_size` | x |  | x |  |
| `[stats]` | `bottom_boob_size` | x |  | x |  |
| `[stats]` | `dialogue_b` |  |  |  | x |
| `[stats]` | `dialogue_g` |  |  |  | x |
| `[stats]` | `dialogue_r` |  |  |  | x |
| `[stats]` | `egg_b` |  |  |  | x |
| `[stats]` | `egg_g` |  |  |  | x |
| `[stats]` | `egg_r` |  |  |  | x |
| `[stats]` | `enable_xray` |  |  |  | x |
| `[stats]` | `fertile` |  |  |  | x |
| `[stats]` | `fertility` |  |  |  | x |
| `[stats]` | `flat` |  |  |  | x |
| `[stats]` | `lactate` |  |  |  | x |
| `[stats]` | `max_eggs` |  |  |  | x |
| `[stats]` | `max_orgasms` |  | x |  |  |
| `[workshop]` | `submission_id` |  |  |  | x |
| `[xray]` | `origin_x` |  | x |  |  |
| `[xray]` | `origin_y` |  | x |  |  |

**Lover (futa) descriptor keys** (120 keys; x = read by that loader)

| Section | Key | ModRoom `.futa` | Deeproom `.futa` | v1.5 `.futa` |
|---|---|---|---|---|
| `[BallClench]` | `bc_cg_off_y` |  | x |  |
| `[BallClench]` | `bc_dt_off_y` |  | x |  |
| `[BallClench]` | `bc_mp_off_y` |  | x |  |
| `[BallClench]` | `bc_rc_off_y` |  | x |  |
| `[CondomPos]` | `condom_y_cowgirls` |  | x |  |
| `[CondomPos]` | `condom_y_mpress` |  | x |  |
| `[CondomPos]` | `deepthroat_condom_offset` |  | x |  |
| `[CumPos]` | `cg_and_rcg_cum_offset` |  | x |  |
| `[CumPos]` | `deepthroat_cum_offset` |  | x |  |
| `[CumPos]` | `mating_press_cum_offset` |  | x |  |
| `[colors]` | `condom` |  | x |  |
| `[colors]` | `cum` |  | x |  |
| `[condom]` | `condom_color` | x | x |  |
| `[condom]` | `condom_y_cowgirls` | x |  |  |
| `[condom]` | `condom_y_mpress` | x |  |  |
| `[cum]` | `cum_color` | x |  |  |
| `[debug]` | `show_debug` | x |  |  |
| `[info]` | `author` |  |  | x |
| `[info]` | `desc` |  |  | x |
| `[info]` | `name` |  |  | x |
| `[penis]` | `penis_type_index` | x | x |  |
| `[pills]` | `blockage_pill` | x | x |  |
| `[pills]` | `diphallia_pill` | x | x |  |
| `[pills]` | `edge_addicted_pill` | x | x |  |
| `[pills]` | `edge_lover_pill` |  | x |  |
| `[pills]` | `equine_pill` | x | x |  |
| `[pills]` | `extra_thick_pill` | x | x |  |
| `[pills]` | `growth_cascade_pill` |  | x |  |
| `[pills]` | `hyper_breeding_pill` | x | x |  |
| `[pills]` | `knotted_pill` | x | x |  |
| `[pills]` | `leaky_pill` | x | x |  |
| `[pills]` | `livestream_pill` |  | x |  |
| `[pills]` | `mega_sperm_pill` | x | x |  |
| `[pills]` | `pound_town_pill` |  | x |  |
| `[pills]` | `premature_pill` |  | x |  |
| `[pills]` | `quickshot_pill` | x | x |  |
| `[pills]` | `reverse_speed_pill` | x | x |  |
| `[pills]` | `stamina_pill` | x | x |  |
| `[pills]` | `three_pump_champ_pill` |  | x |  |
| `[portrait]` | `boob_box_position` | x |  |  |
| `[portrait]` | `boob_x_offset` |  | x |  |
| `[portrait]` | `boob_y_offset` |  | x |  |
| `[portrait]` | `head_offset` |  |  | x |
| `[portrait]` | `head_offset_alt` |  |  | x |
| `[portrait]` | `headpat_x_offset` |  | x |  |
| `[portrait]` | `headpat_y_offset` |  | x |  |
| `[portrait]` | `kiss_box_position` | x |  |  |
| `[portrait]` | `kiss_x_offset` |  | x |  |
| `[portrait]` | `kiss_y_offset` |  | x |  |
| `[portrait]` | `nipple_size` |  |  | x |
| `[portrait]` | `nipple_size_alt` |  |  | x |
| `[portrait]` | `nipple_x` |  |  | x |
| `[portrait]` | `nipple_x_alt` |  |  | x |
| `[portrait]` | `nipple_y` |  |  | x |
| `[portrait]` | `nipple_y_alt` |  |  | x |
| `[portrait]` | `origin_x` | x | x | x |
| `[portrait]` | `origin_y` | x | x | x |
| `[portrait]` | `portrait_change_position` | x |  |  |
| `[portrait]` | `portrait_eye_track_position` | x |  |  |
| `[sprite]` | `bulge_height` |  |  | x |
| `[sprite]` | `bulge_width` |  |  | x |
| `[sprite]` | `condom_y` | x | x | x |
| `[sprite]` | `cowgirl_origin_x` | x | x |  |
| `[sprite]` | `cowgirl_origin_y` | x | x |  |
| `[sprite]` | `cum_y_offset` |  | x |  |
| `[sprite]` | `deepthroat_origin_x` |  | x |  |
| `[sprite]` | `deepthroat_origin_y` |  | x | x |
| `[sprite]` | `deepthroat_y_offset` |  | x |  |
| `[sprite]` | `heavy_boobs` |  |  | x |
| `[sprite]` | `mating_press_origin_x` |  | x |  |
| `[sprite]` | `mating_press_origin_y` |  | x |  |
| `[sprite]` | `origin_x` | x | x | x |
| `[sprite]` | `origin_y` | x | x | x |
| `[sprite]` | `standing_condom_y` |  |  | x |
| `[sprite]` | `xray_offset_y` | x | x |  |
| `[sprite]` | `xray_x` |  |  | x |
| `[sprite]` | `xray_y` |  |  | x |
| `[stats]` | `ball_size` | x | x |  |
| `[stats]` | `condom_b` |  |  | x |
| `[stats]` | `condom_g` |  |  | x |
| `[stats]` | `condom_r` |  |  | x |
| `[stats]` | `cum_b` |  |  | x |
| `[stats]` | `cum_g` |  |  | x |
| `[stats]` | `cum_r` |  |  | x |
| `[stats]` | `cum_volume_modifier` | x | x |  |
| `[stats]` | `cum_volume_mult` | x |  |  |
| `[stats]` | `cumshot_mult` |  | x |  |
| `[stats]` | `default_moans` |  |  | x |
| `[stats]` | `dialogue_alt_b` |  |  | x |
| `[stats]` | `dialogue_alt_g` |  |  | x |
| `[stats]` | `dialogue_alt_r` |  |  | x |
| `[stats]` | `dialogue_b` |  |  | x |
| `[stats]` | `dialogue_g` |  |  | x |
| `[stats]` | `dialogue_r` |  |  | x |
| `[stats]` | `egg_b` |  |  | x |
| `[stats]` | `egg_g` |  |  | x |
| `[stats]` | `egg_r` |  |  | x |
| `[stats]` | `enable_xray` |  |  | x |
| `[stats]` | `fertile` |  |  | x |
| `[stats]` | `fertility` |  |  | x |
| `[stats]` | `flat` |  |  | x |
| `[stats]` | `flat_alt` |  |  | x |
| `[stats]` | `lactate` |  |  | x |
| `[stats]` | `lactate_alt` |  |  | x |
| `[stats]` | `max_eggs` |  |  | x |
| `[stats]` | `max_orgasms` | x | x | x |
| `[stats]` | `max_pumps` |  | x | x |
| `[stats]` | `pump_base_volume` | x |  |  |
| `[stats]` | `pump_delay` | x | x |  |
| `[stats]` | `pump_delay_max` |  | x |  |
| `[stats]` | `pump_delay_min` |  | x |  |
| `[stats]` | `stamina` |  | x |  |
| `[stats]` | `stroke_depth` | x | x |  |
| `[stats]` | `stroke_speed` | x | x |  |
| `[stats]` | `top_ass_size` | x | x |  |
| `[stats]` | `top_boob_size` | x | x |  |
| `[stats]` | `top_penis_length` | x | x |  |
| `[stats]` | `top_penis_width` | x | x |  |
| `[stats]` | `virility_modifier` | x | x |  |
| `[workshop]` | `submission_id` |  |  | x |
