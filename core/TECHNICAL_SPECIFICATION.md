# Deeproom 4.0 Mobile & ToyBridge Technical Architecture Specification

This specification is an exhaustive engineering reference for modders, tools developers, and upstream maintainers integrating mobile and touch systems directly into base builds of Deeproom or ToyBridge using UndertaleModTool (UTMT) or GameMaker Studio source repositories.

Every section specifies:
- **Component ID & Provenance**: `[Deeproom Mobile Custom]` or `[ToyBridge]`
- **Target Object & Event Hook**: Exact location in GameMaker's object hierarchy
- **Search Anchor / Context**: Surrounding vanilla code where the hook attaches
- **Complete Working GML / Java / AXML**: Drop-in code blocks ready for integration
- **Variables & Dependencies**: Prerequisites and initialization state

---

## Table of Contents

### Part 1: Core Engine & Lifecycle Enhancements
1. [DR-01] [Deeproom Mobile Custom] Native Manifest Stream Scanning (_manifest.txt)
2. [DR-02] [Deeproom Mobile Custom] Android Asset Path Normalization (tc_norm_path)
3. [DR-03] [Deeproom Mobile Custom] Multi-Directory Dialogue Scanning & Safe Parser
4. [DR-04] [Deeproom Mobile Custom] Custom Bedrooms Scanner & Touch Drag Scrolling Navigation
5. [DR-05] [Deeproom Mobile Custom] Sandboxed Storage & Persistent Session Redirection (setting_data.sav)

### Part 2: Character Rigging, Scaling & Pill Protections
6. [DR-06] [Deeproom Mobile Custom] Universal Origin-Based Model Scaling & Multi-Frame Slicing
7. [DR-07] [Deeproom Mobile Custom] Pill Custom Asset Protections, Sheath Fallbacks & Proportional Condom Scaling
8. [DR-08] [Deeproom Mobile Custom] Ovulation Disentanglement from Wife Climax (func_wife_climax)
9. [DR-09] [Deeproom Mobile Custom] Custom Spouse X-Ray Origin Coordinates Initialization

### Part 3: Rendering Pipeline Stability & Fallbacks
10. [DR-10] [Deeproom Mobile Custom] Lover-Wife Portrait Fallback Parity Architecture
11. [DR-11] [Deeproom Mobile Custom] Non-Negative Sprite Shield & Condom/X-ray Fallbacks
12. [DR-12] [Deeproom Mobile Custom] Clean Portrait Unloading & Cross-Character Isolation
13. [DR-13] [Deeproom Mobile Custom] Dynamic Composite Thumbnail Slicing & Frame Fallback

### Part 4: Touch UI, Character Selection Screen (CSS) & Navigation
14. [DR-14] [Deeproom Mobile Custom] CSS Auto-Scroll & Centering Math (Jump-to-Selected)
15. [DR-15] [Deeproom Mobile Custom] CSS Equipped Partner Pulsing Gold Border & Title Star
16. [DR-16] [Deeproom Mobile Custom] CSS Card Click Isolation & Star Hitbox Disentanglement (!_star_hover)
17. [DR-17] [Deeproom Mobile Custom] CSS Geometric Vector Star Badges, Silent Click Isolation & Dynamic Filter
18. [DR-18] [Deeproom Mobile Custom] CSS Modal Input Priority & Background Suppression
19. [DR-19] [Deeproom Mobile Custom] CSS Header Layout: Left Search Bar, Right-Side [FAV: ALL/ON] Toggle & Locked Close Button
20. [DR-20] [Deeproom Mobile Custom] CSS Mobile Virtual Keyboard Trigger & Auto-Dismissal
21. [DR-21] [Deeproom Mobile Custom] Mutual Panel Exclusivity & Radar Chart Isolation
22. [DR-22] [Deeproom Mobile Custom] Climax Screen Protection & Panel Auto-Closing
23. [DR-23] [Deeproom Mobile Custom] Translucent Mobile Overlay with Strict Modal Z-Ordering
24. [DR-24] [Deeproom Mobile Custom] Single-Trigger Overlay Action Execution
25. [DR-25] [Deeproom Mobile Custom] Uninterrupted 8-Mechanic Gameplay Interaction & Disclaimer One-Time Gate
26. [DR-26] [Deeproom Mobile Custom] Neutralization of Rickroll Fake Crash Loop in Step_0

### Part 5: Android Platform & ToyBridge Foundation Systems
27. [TB-01] [ToyBridge] Synthetic Right-Click & Touch Hold Engine
28. [TB-02] [ToyBridge] Dual-Column Vertical Menu Layout
29. [TB-03] [ToyBridge] Momentum Drag-to-Scroll Accumulator (menu_scroll_update)
30. [TB-04] [ToyBridge] SIZES Options Page Hyper-Scale Toggle (TouchHyperToggle)
31. [TB-05] [ToyBridge] On-Device Mod Sharing Activity (wbmods.PhoneImportActivity)
32. [DR-27] [Deeproom Mobile Custom] Pure Python Binary AXML Editor & APK DEX Bundling
33. [TB-06] [ToyBridge] Optional External UDP Telemetry Broadcast (buttplug_socket)
34. [DR-28] [Deeproom Mobile Custom] Pre-Flight Mod Pack Classification & Quarantine Architecture
35. [DR-29] [Deeproom Mobile Custom] Universal ModRoom & Legacy Spouse Format Detection (check_custom_wife)
36. [DR-30] [Deeproom Mobile Custom] Mobile Audio & Voice Pack Streaming (custom_music & custom_sounds)
37. [DR-31] [Deeproom Mobile Custom] Anatomy Sprite & Boob Box Pre-Flight Safety Guards
38. [DR-32] [Deeproom Mobile Custom] Screen Boundary Clamping for Mobile Dragging Menus
39. [DR-33] [Deeproom Mobile Custom] Dual-Engine Bytecode Ingestion, v1.5 Manifest Streaming & Unified Alphabetical Ingestion
40. [DR-34] [Deeproom Mobile Custom] Multi-Input Ingestion, Extended CLI, Modular Install Modes & Dynamic Naming

---

## Upstream Developer Integration Map (By Target Object & Event)

For downstream modders and engine maintainers integrating these features directly via UndertaleModTool or GameMaker Studio, this map groups all 40 subsystems by the exact object and event file you need to open:

### 1. File: `gml_Object_oFutaMatingPress_Create_0`
Open this script once to integrate all lifecycle, scaling, and initialization subsystems:
- **Variable Initializations**: Define `boob_box = false;`, `cowgirl_origin_y = 84;`, `selector_favs_only = false;`, `global.favs_futa = ds_map_create();`, `global.favs_wife = ds_map_create();` upfront.
- **`[DR-01]`**: Ingest `custom_futas/_manifest.txt` and `custom_wives/_manifest.txt` inside scanner functions.
- **`[DR-02]`**: Define `tc_norm_path(path)` leading-slash normalizer.
- **`[DR-05]`**: Ingest and save settings in `setting_data.sav` and `func_save_settings()`.
- **`[DR-06]`**: Dynamic multi-frame slicer and `160 / frame_w` scale normalization in `func_load_custom_futa()`.
- **`[DR-07]`**: Out-of-bounds frame guards in `func_get_futa_frame()` (shaft case 11, 15, 18).
- **`[DR-08]`**: Disentangle `func_ovulate()` from `func_wife_climax()`.
- **`[DR-09]`**: Initialize default `xray_origin_x = 80; xray_origin_y = 84;` in `func_load_custom_spouse()`.
- **`[DR-12]`**: Reset `legacy_custom_portrait = -1` when loading characters lacking portrait PNGs.
- **`[TB-03]`**: Add `menu_scroll_update(menu, max_items, visible_items)` momentum touch drag accumulator.
- **`[TB-06]`**: (Optional) Initialize `buttplug_socket = network_create_socket(network_socket_udp)`.
- **`[DR-29]`**: Add `check_custom_wife(path)` universal ModRoom and Legacy format validator.
- **`[DR-30]`**: Stream `custom_music/*.ogg` and `custom_sounds/futa/*` voice packs.
- **`[DR-31]`**: Set upfront safety booleans (`boob_box = false; cowgirl_origin_y = 84;`).

### 2. File: `gml_Object_oFutaMatingPress_Draw_0`
Open this script to integrate all rendering, UI modal gating, and touch controls:
- **`[DR-10]`**: Lover portrait fallback parity (`_is_custom_lover` conditional and `_lover_base_portrait`).
- **`[DR-11]`**: Non-negative sprite shields before `draw_sprite_ext` for `c_sprite`, `dt_c_sprite`, and `legacy_xray_sprite`.
- **`[DR-13]`**: Dynamic composite thumbnail loader with `max(1, round(pw / ph))` aspect ratio probing.
- **`[DR-14]`**: Centering auto-scroll math (`futa_selector_menu.scroll = clamp(...)`) on equipped partner upon CSS opening.
- **`[DR-15]`**: Equipped partner animated gold glow border (`0.35 + 0.15 * sin(current_time * 0.005)`) and header title star.
- **`[DR-16]`**: Card click isolation guard (`!_star_hover`) preventing accidental equipping when toggling bookmarks.
- **`[DR-17]`**: Geometric vector star badge ($14 \times 14$ px vector box) with immediate write/delete in `setting_data.sav`.
- **`[DR-18]`**: Modal input suppression on background buttons (`NEW LOVER`, `NEW WIFE`, Options) during CSS display.
- **`[DR-19]`**: Prioritized `[FAV: ALL/ON]` filter header layout on the left ($x = 20\text{--}95$) with touch precedence over search.
- **`[DR-20]`**: Mobile virtual keyboard trigger (`keyboard_virtual_show`) and dismiss handling on `vk_enter`/`vk_escape`.
- **`[DR-21]`**: Mutually exclusive radar stat graphs bound strictly to active panels (`portrait_number == 0` or `1`).
- **`[DR-22]`**: Climax screen auto-closing (force-closes floating panels and hides partner switch buttons during climax).
- **`[DR-23]`**: Translucent mobile overlay ($0.12$ idle, $0.40$ active) suppressed when CSS is open.
- **`[DR-24]`**: Consolidated single-loop quick actions (`[R]`, `[N]`, `[C]`, `[O]`) preventing double execution.
- **`[DR-25]`**: Remove modal lockouts (`&& newlover_menu_toggle == false && newwife_menu_toggle == false`) to unlock all 8 mechanics during open menus. One-time startup warning disclaimer gate.
- **`[TB-01]`**: Synthetic right-click touch hold timer (`mob_lp_timer == 22`).
- **`[TB-02]`**: Dual-column vertical menu pill layout calculation.
- **`[TB-04]`**: SIZES options page `[HYPER: ON/OFF]` toggle ($2.5\times$ slider range expansion).
- **`[TB-06]`**: (Optional) 30Hz UDP telemetry broadcast loop.
- **`[DR-31]`**: Anatomy render shield (`if (sprite_exists(anatomy_sprite))`).
- **`[DR-32]`**: Touch drag boundary clamping (`newlover_menu_cx = clamp(mouse_x + drag_offset_x, ...)`).

### 3. File: `gml_Object_oFutaMatingPress_Step_0`
- **`[DR-22]`**: Guard portrait hover hitboxes with `futa_selector_open == false && orgasm == false`.
- **`[DR-26]`**: Neutralize legacy desktop Rickroll fake crash trigger (`global.rg_chosen_pill == -1`).

### 4. File: `gml_Object_oBackground_Create_0`
- **`[DR-04]`**: Custom bedrooms scanner reading `custom_bedrooms/_manifest.txt` directly without `tc_wd`.

### 5. File: `gml_Object_oDialogueManager_Create_0`
- **`[DR-03]`**: Safe dialogue JSON parsing (`try / catch dialogue_json = json_parse(...)`).
- **`[DR-14]`**: Inverted dialogue pack hierarchy prioritizing `dialogue_packs/` over internal character text.

### 6. Android Platform Packaging Layer
- **`[TB-05]`**: Bundle `phone_import.dex` containing `wbmods.PhoneImportActivity` as secondary DEX (`classes2.dex`).
- **`[DR-27]`**: Binary AXML chunk injection into `AndroidManifest.xml` registering `wbmods.PhoneImportActivity` with `VIEW` and `SEND` intent filters.
- **`[DR-28]`**: Pre-flight folder auditor (`classify_custom_pack`) and quarantine isolator.

---

## Variable Scope & Initialization Master Reference

| Variable Name | Scope | Defined In | Default Value | Architectural Function |
| :--- | :--- | :--- | :--- | :--- |
| `custom_mating_press_scale` | Instance | `Create (0)` | `1.0` | Normalization scale factor ($160 / \text{frame\_w}$) applied to non-standard partner sprite sheets. |
| `global.favs_futa` | Global | `Create (0)` | `ds_map_create()` | Map containing names of bookmarked custom partners. Persists to `setting_data.sav`. |
| `global.favs_wife` | Global | `Create (0)` | `ds_map_create()` | Map containing names of bookmarked custom spouses. Persists to `setting_data.sav`. |
| `selector_favs_only` | Instance | `Create (0)` | `false` | Boolean toggle filtering CSS grid to show only starred cards. Persists to `setting_data.sav`. |
| `_sel_jump_done` | Instance | `Draw (0)` | `false` | One-shot latch ensuring CSS only auto-scrolls to the equipped partner once per menu opening. |
| `boob_box` | Instance | `Create (0)` | `false` | Safety initialization preventing early uninitialized variable lookup warnings. |
| `cowgirl_origin_y` | Instance | `Create (0)` | `84` | Default vertical origin coordinate preventing missing origin crashes. |
| `tc_hyper` | Instance | `Create (0)` | `false` | SIZES options page multiplier expanding slider limits to $2.5\times$. Persists to `setting_data.sav`. |
| `mob_expanded` | Instance | `Create (0)` | `false` | Toggle state for the mobile floating action drawer menu. |
| `mob_lp_timer` | Instance | `Create (0)` | `0` | Touch-hold frame counter used to synthesize desktop right-clicks on touchscreen. |
| `selector_search_focused`| Instance | `Create (0)` | `false` | Tracks whether the CSS search bar is focused, controlling on-screen keyboard display. |
| `buttplug_socket` | Instance | `Create (0)` | `-1` | (Optional) UDP socket descriptor for external Bluetooth toy telemetry broadcast. |
35. [DR-29] [Deeproom Mobile Custom] Universal ModRoom & Legacy Spouse Format Detection (check_custom_wife)
36. [DR-30] [Deeproom Mobile Custom] Mobile Audio & Voice Pack Streaming (custom_music & custom_sounds)
37. [DR-31] [Deeproom Mobile Custom] Anatomy Sprite & Boob Box Pre-Flight Safety Guards
38. [DR-32] [Deeproom Mobile Custom] Screen Boundary Clamping for Mobile Dragging Menus
39. [DR-33] [Deeproom Mobile Custom] Dynamic Engine Bytecode Ingestion & Multi-Target Compilation
40. [DR-34] [Deeproom Mobile Custom] Dynamic Output APK Naming & Character Sanitization

---

## Part 1: Core Engine & Lifecycle Enhancements

### 1. [DR-01] [Deeproom Mobile Custom] Native Manifest Stream Scanning (_manifest.txt)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Inside `func_scan_custom_futas()` and `func_scan_custom_wives()`

Bypasses slow, blocking filesystem loops (`file_find_first` / `file_find_next`) by streaming newline-delimited text manifests (`_manifest.txt`). Eliminates Android OS ANR watchdog timeouts (< 50ms startup).

```gml
// Read pre-indexed manifest stream for custom partners
ds_list_clear(custom_futas_folder);
var _mf_futas = "custom_futas/_manifest.txt";
if (file_exists(_mf_futas))
{
    var _f = file_text_open_read(_mf_futas);
    while (!file_text_eof(_f))
    {
        var _line = string_trim(file_text_read_string(_f));
        file_text_readln(_f);
        if (_line != "")
        {
            var _pack_path = "custom_futas/" + _line;
            ds_list_add(custom_futas_folder, _pack_path);
            if (variable_instance_exists(id, "futa_selector_names"))
                ds_list_add(futa_selector_names, _line);
        }
    }
    file_text_close(_f);
    custom_sprite_loaded = (ds_list_size(custom_futas_folder) > 0);
}

// Read pre-indexed manifest stream for custom spouses
ds_list_clear(custom_wives_folder);
var _mf_wives = "custom_wives/_manifest.txt";
if (file_exists(_mf_wives))
{
    var _f = file_text_open_read(_mf_wives);
    while (!file_text_eof(_f))
    {
        var _line = string_trim(file_text_read_string(_f));
        file_text_readln(_f);
        if (_line != "")
        {
            var _pack_path = "custom_wives/" + _line;
            ds_list_add(custom_wives_folder, _pack_path);
            if (variable_instance_exists(id, "wife_selector_names"))
                ds_list_add(wife_selector_names, _line);
        }
    }
    file_text_close(_f);
    custom_wife_loaded = (ds_list_size(custom_wives_folder) > 0);
}
```

---

### 2. [DR-02] [Deeproom Mobile Custom] Android Asset Path Normalization (tc_norm_path)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Function definition `tc_norm_path(path)`

On Android APK runtime, GameMaker asset lookups fail when passed paths with a leading `/` (e.g. `/custom_futas/name`). This helper strips leading slashes.

```gml
function tc_norm_path(arg0)
{
    var _p = string_replace_all(string(arg0), "\\", "/");
    while (string_length(_p) > 0 && string_char_at(_p, 1) == "/")
    {
        _p = string_delete(_p, 1, 1);
    }
    return _p;
}
```

---

### 3. [DR-03] [Deeproom Mobile Custom] Multi-Directory Dialogue Scanning & Safe Parser

- **Target Object**: `oDialogueManager`
- **Target Event**: `Create (0)`
- **Anchor**: Initialization and inside `load_dialogue_file()`

Scans community dialogue packs across both `dialogue_packs/*.json` and `custom_dialogues/*.json`. Dynamically resolves file paths while safeguarding against malformed JSON syntax:

```gml
// 1. Dual directory scanner
dialogue_files = [];
var file_name = tc_ff_first("dialogue_packs/*.json", 0);
while (file_name != "") { array_push(dialogue_files, file_name); file_name = tc_ff_next(); }
tc_ff_close();

var file_name2 = tc_ff_first("custom_dialogues/*.json", 0);
while (file_name2 != "") { if (!array_contains(dialogue_files, file_name2)) array_push(dialogue_files, file_name2); file_name2 = tc_ff_next(); }
tc_ff_close();

// 2. Safe path resolver and parser
function load_dialogue_file()
{
    func_load_dialogue(chosen_dialogue);
    if (chosen_dialogue == "") return false;

    var _file_name = "dialogue_packs/" + chosen_dialogue;
    if (!file_exists(_file_name))
    {
        if (file_exists("custom_dialogues/" + chosen_dialogue)) _file_name = "custom_dialogues/" + chosen_dialogue;
        else if (file_exists("dialogue/" + chosen_dialogue)) _file_name = "dialogue/" + chosen_dialogue;
        else if (file_exists(chosen_dialogue)) _file_name = chosen_dialogue;
        else return false;
    }

    var _buffer = buffer_load(_file_name);
    if (_buffer == -1) return false;
    var _json_string = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);

    try
    {
        dialogue_json = json_parse(_json_string);
        return true;
    }
    catch (_err)
    {
        dialogue_json = {};
        return false;
    }
}
```

---

### 4. [DR-04] [Deeproom Mobile Custom] Custom Bedrooms Scanner & Touch Drag Scrolling Navigation

- **Target Object**: `oBackground` & `oFutaMatingPress`
- **Target Event**: `Create (0)` (oBackground) & `Draw (0)` (oFutaMatingPress)
- **Anchor**: Inside `func_scan_custom_backgrounds()` and bedroom menu drawing block (~line 841200)

Loads custom bedrooms without requiring native filesystem walking, and upgrades the bedroom drawer with full mobile touch-drag scrolling and clickable navigation arrows:

```gml
// 1. In-memory manifest bedroom scanner (oBackground Create_0)
function func_scan_custom_backgrounds()
{
    ds_list_clear(custom_background_folders);
    var _mf = "custom_bedrooms/_manifest.txt";
    if (file_exists(_mf))
    {
        var _f = file_text_open_read(_mf);
        while (!file_text_eof(_f))
        {
            var _line = string_trim(file_text_read_string(_f));
            file_text_readln(_f);
            if (_line != "")
            {
                var _full_path = "custom_bedrooms/" + _line;
                custom_background_loaded = true;
                ds_list_add(custom_background_folders, _full_path);
            }
        }
        file_text_close(_f);
    }
}

// 2. Touch-drag swipe scrolling and clickable arrows (oFutaMatingPress Draw_0)
var _bg_max_scroll = max(0, total_background_amount - 11);
var _bg_panel_x1 = room_width - 110;
var _bg_panel_y1 = 95;
var _bg_panel_x2 = room_width;
var _bg_panel_y2 = 120 + (12 * _visible) + 15;
var _bg_panel_hover = point_in_rectangle(mouse_x, mouse_y, _bg_panel_x1, _bg_panel_y1, _bg_panel_x2, _bg_panel_y2);

// Touch drag swipe accumulator
if (mouse_check_button_pressed(mb_left) && _bg_panel_hover)
{
    bg_menu_dragging = true;
    bg_menu_drag_start_y = mouse_y;
    bg_menu_drag_start_scroll = bg_menu.scroll;
}
if (bg_menu_dragging)
{
    if (mouse_check_button(mb_left))
    {
        var _bg_delta = (bg_menu_drag_start_y - mouse_y) / 12;
        bg_menu.scroll = clamp(bg_menu_drag_start_scroll + _bg_delta, 0, _bg_max_scroll);
    }
    else { bg_menu_dragging = false; }
}
bg_menu.scroll = clamp(bg_menu.scroll, 0, _bg_max_scroll);
bg_menu.scroll_lerp = lerp(bg_menu.scroll_lerp, bg_menu.scroll, 0.35);

// Clickable Up/Down arrow buttons with generous touch targets (60x24px)
if (bg_menu.scroll > 0 && mouse_check_button_pressed(mb_left) && point_in_rectangle(mouse_x, mouse_y, room_width - 86, 97, room_width - 26, 121))
{
    bg_menu.scroll = max(0, bg_menu.scroll - 3);
    mouse_clear(mb_left);
}
if (bg_menu.scroll < _bg_max_scroll && mouse_check_button_pressed(mb_left) && point_in_rectangle(mouse_x, mouse_y, room_width - 86, (120 + 12 * _visible) - 17, room_width - 26, (120 + 12 * _visible) + 7))
{
    bg_menu.scroll = min(_bg_max_scroll, bg_menu.scroll + 3);
    mouse_clear(mb_left);
}
```

---

### 5. [DR-05] [Deeproom Mobile Custom] Sandboxed Storage & Persistent Session Redirection (setting_data.sav)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)` & `Draw (0)`
- **Anchor**: Inside `func_save_settings()` and startup settings loader

Bypasses GameMaker mobile `working_directory` path resolution bugs by routing writes directly to relative sandboxed filenames. Persists all core gameplay options, audio volumes, `tc_hyper`, `selector_favs_only`, and character bookmarks into `setting_data.sav`.

```gml
// -------------------------------------------------------------------------
// Startup Settings Ingestion (Create_0)
// -------------------------------------------------------------------------
if (file_exists("setting_data.sav"))
{
    ini_open("setting_data.sav");
    // Standard game settings restoration...
    global.vol_master = ini_read_real("options", "master_audio", 1);
    global.vol_sfx = ini_read_real("options", "sound_sfx", 1);
    global.vol_voice = ini_read_real("options", "voice_fx", 1);
    continuous_toggle = ini_read_real("features", "continuous_toggle", 0);

    // Enhancement options restoration
    if (ini_key_exists("options", "hyper_sizes"))
        tc_hyper = bool(ini_read_real("options", "hyper_sizes", false));
    if (ini_key_exists("options", "selector_favs_only"))
        selector_favs_only = bool(ini_read_real("options", "selector_favs_only", false));

    // Restore bookmarked favorites
    for (var _fi = 0; _fi < ds_list_size(custom_futas_folder); _fi++)
    {
        var _fn = filename_name(ds_list_find_value(custom_futas_folder, _fi));
        if (ini_read_real("favs_futa", _fn, 0) == 1)
            ds_map_add(global.favs_futa, _fn, 1);
    }
    for (var _wi = 0; _wi < ds_list_size(custom_wives_folder); _wi++)
    {
        var _wn = filename_name(ds_list_find_value(custom_wives_folder, _wi));
        if (ini_read_real("favs_wife", _wn, 0) == 1)
            ds_map_add(global.favs_wife, _wn, 1);
    }
    ini_close();
}

// -------------------------------------------------------------------------
// Settings Saver (func_save_settings)
// -------------------------------------------------------------------------
function func_save_settings()
{
    ini_open("setting_data.sav");
    // Base audio and options writes...
    ini_write_real("features", "continuous_toggle", continuous_toggle);
    if (variable_instance_exists(id, "tc_hyper"))
        ini_write_real("options", "hyper_sizes", tc_hyper);
    if (variable_instance_exists(id, "selector_favs_only"))
        ini_write_real("options", "selector_favs_only", selector_favs_only);
    ini_close();
}
```

---

## Part 2: Character Rigging, Scaling & Pill Protections

### 6. [DR-06] [Deeproom Mobile Custom] Universal Origin-Based Model Scaling & Multi-Frame Slicing

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Inside `func_load_custom_futa()` & `func_load_custom_wife()`

#### Mathematical Formulation
$$\text{Frame Width} = \text{origin\_x} \times 2$$
$$\text{Frame Count} = \max\left(1, \text{round}\left(\frac{\text{Sheet Width}}{\text{Frame Width}}\right)\right)$$
$$\text{Scale Factor} = \frac{160}{\text{Frame Width}}$$

```gml
var f_mate = string(arg0) + "/custom_mating_press.png";
if (file_exists(f_mate))
{
    if (sprite_exists(legacy_custom_mating_press)) sprite_delete(legacy_custom_mating_press);

    // 1. Probe total sheet pixel dimensions
    var _temp_spr = sprite_add(f_mate, 1, false, false, 0, 0);
    var _sheet_w = sprite_get_width(_temp_spr);
    sprite_delete(_temp_spr);

    // 2. Derive frame metrics using author's origin_x
    var _frame_w = mp_origin_x * 2;
    var _frame_cnt = max(1, round(_sheet_w / _frame_w));

    // 3. Sliced multi-frame instantiation
    legacy_custom_mating_press = sprite_add(f_mate, _frame_cnt, false, false, mp_origin_x, mp_origin_y);

    // 4. Calculate 160px baseline normalization scale
    if (_frame_w > 0 && _frame_w != 160)
        custom_mating_press_scale = 160 / _frame_w;
    else
        custom_mating_press_scale = 1.0;
}
```

---

### 7. [DR-07] [Deeproom Mobile Custom] Pill Custom Asset Protections, Sheath Fallbacks & Proportional Condom Scaling

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)` & `Draw (0)`
- **Anchor**: Inside `func_get_futa_frame(type, frame_id)` and condom drawing blocks (~lines 68200 & 261000)

#### Technical Problem
When consuming pill items (Horse Pill, Knotted Pill, Knotted Horse Pill), the game engine requests frames 11, 15, or 18 from `top_sprite`. If a custom sprite sheet contains fewer frames, or if a legacy pack returns `-1` for sheaths, GameMaker crashes with out-of-bounds frame exceptions or renders the penis invisible. Furthermore, when pill art was missing or pills scaled the anatomy, condoms previously returned `-1` or mismatched the scaled penis dimensions, failing to display on top appropriately.

```gml
// 1. Shaft and condom pill art bounds protections (Create_0 func_get_futa_frame)
case "shaft":
    comment = "layer 1 (base/sheath) - safe fallback to base shaft if custom spritesheet lacks pill frames";
    var _spr_frames = sprite_get_number(top_sprite);
    if (penis_type_index == 1 && _spr_frames > 11) return 11;
    if (penis_type_index == 2 && _spr_frames > 15) return 15;
    if (penis_type_index == 3 && _spr_frames > 18) return 18;
    return (is_legacy_custom ? 2 : 7);

case "condom":
    comment = "condom - safely falls back to base condom frame 0 if pill art missing";
    return 0;

case "broken":
    comment = "broken condom - safely falls back to frame 0 if pill art missing";
    return 0;

// 2. Proportional condom scale locking (Draw_0)
if (custom_condom_scale <= 0 || custom_condom_scale != custom_mating_press_scale)
{
    custom_condom_scale = custom_mating_press_scale;
}

// 3. Proportional X-Ray condom pill fallback scaling (Draw_0)
if (condom == true)
{
    comment = "custom x-ray condom - scales along with pill fallbacks";
    if (_f_condom != -1)
    {
        draw_sprite_ext(custom_xray, _f_condom, x + xray_offset, draw_y, (1 + balls_jiggle) * top_penis_width * x_scale, top_penis_length * x_scale, 0, condom_color, 1);
    }
    else if (sprite_exists(xray_sprite))
    {
        draw_sprite_ext(xray_sprite, 0, x + xray_offset, draw_y, (1 + balls_jiggle) * top_penis_width * x_scale, top_penis_length * x_scale, 0, condom_color, 1);
    }
}
```

---

### 8. [DR-08] [Deeproom Mobile Custom] Ovulation Disentanglement from Wife Climax (func_wife_climax)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Inside `func_wife_climax()`

Desktop Deeproom hardcoded a call to `func_ovulate()` inside `func_wife_climax()`, forcing an ovulation cycle on every wife orgasm and breaking independent ovulation gameplay.

```gml
// Disentangled func_wife_climax:
if (sex_position != 3)
{
    for (var i = 0; i < wife_climax_stage; i++)
    {
        // Removed unconditional func_ovulate() call
        comment = "Ovulation triggered independently via [O] key/button or pill conditions";
    }
}
```

---

### 9. [DR-09] [Deeproom Mobile Custom] Custom Spouse X-Ray Origin Coordinates Initialization

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Inside `func_load_custom_spouse(folder, alt)`

```gml
// Default origin coordinates (160x168 baseline reference)
var xray_origin_x = 80;
var xray_origin_y = 84;

if (file_exists(string(arg0) + "/custom_data.spouse") || file_exists(string(arg0) + "/custom_data.wife") || (os_type == os_android || os_type == os_ios))
{
    var _spouse_ini = file_exists(string(arg0) + "/custom_data.wife") ? (string(arg0) + "/custom_data.wife") : (string(arg0) + "/custom_data.spouse");
    ini_open(_spouse_ini);
    var _def_xo = ini_read_real("sprite", "xray_x", ini_read_real("xray", "origin_x", 80));
    var _def_yo = ini_read_real("sprite", "xray_y", ini_read_real("xray", "origin_y", 84));
    if (_def_xo <= 120 && _def_xo >= 40) xray_origin_x = _def_xo;
    if (_def_yo <= 120 && _def_yo >= 40) xray_origin_y = _def_yo;
    ini_close();
}

var f_xray = string(arg0) + "/custom_xray.png";
if (file_exists(f_xray))
{
    if (sprite_exists(legacy_custom_wife_xray)) sprite_delete(legacy_custom_wife_xray);
    legacy_custom_wife_xray = sprite_add(f_xray, 4, false, false, xray_origin_x, xray_origin_y);
    var _lcwx_w = sprite_get_width(legacy_custom_wife_xray);
    if (_lcwx_w > 0 && _lcwx_w != 160)
    {
        var _lcwx_sc = 160 / _lcwx_w;
        sprite_set_offset(legacy_custom_wife_xray, xray_origin_x / _lcwx_sc, xray_origin_y / _lcwx_sc);
    }
}
```

---

## Part 3: Rendering Pipeline Stability & Fallbacks

### 10. [DR-10] [Deeproom Mobile Custom] Lover-Wife Portrait Fallback Parity Architecture

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Lines ~7690-7870 (Lover portrait draw routines)

#### Technical Problem
If custom portrait art is uninitialized or absent, drawing unconditionally using custom sprite IDs results in `requested -1` runner crashes. Conversely, substituting custom IDs unconditionally without gating causes custom assets to render underneath vanilla characters (`DEVIL`, `FURRY`, `CLOWN`).

```gml
// 1. Determine active partner mode
var _is_custom_lover = (custom_lover_toggle == true || top_sprite == legacy_custom_mating_press || top_sprite == custom_mating_press);
var _spr_custom_lover_portrait = _is_custom_lover && (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1);
var _spr_custom_lover_portrait_new = _is_custom_lover && (sprite_exists(custom_portrait) && custom_portrait != -1);

// 2. Resolve base portrait: custom art if custom mode, native sprite if vanilla
var _lover_base_portrait = _spr_custom_lover_portrait ? legacy_custom_portrait : (_spr_custom_lover_portrait_new ? custom_portrait : func_get_portrait(top_sprite, 0));
if (!sprite_exists(_lover_base_portrait) || _lover_base_portrait == -1) _lover_base_portrait = sFutaPortrait1;

// 3. Resolve hair base
var _lover_hair_base = (sprite_exists(hair_sprite) && hair_sprite != -1) ? func_get_portrait(hair_sprite, 0) : _lover_base_portrait;
if (!sprite_exists(_lover_hair_base) || _lover_hair_base == -1) _lover_hair_base = _lover_base_portrait;

// 4. Render layers with safe fallbacks
comment = "layer 0: hair (back)";
draw_sprite_ext(_lover_hair_base, 0, portrait_x - face_x, (portrait_y - face_y) + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);

comment = "layer 1: torso";
draw_sprite_ext(_lover_base_portrait, 1, portrait_x, portrait_y + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);
```

---

### 11. [DR-11] [Deeproom Mobile Custom] Non-Negative Sprite Shield & Condom/X-ray Fallbacks

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Condom draw (~line 1770) & X-ray draw (~line 5200)

```gml
// Condom assignments with existence verification
if (sprite_exists(legacy_custom_condom) && legacy_custom_condom != -1) c_sprite = legacy_custom_condom;
if (sprite_exists(legacy_custom_condom) && legacy_custom_condom != -1) dt_c_sprite = legacy_custom_condom;

// Guard before drawing
if (!sprite_exists(c_sprite) || c_sprite == -1) c_sprite = sFutaCondom;
if (!sprite_exists(dt_c_sprite) || dt_c_sprite == -1) dt_c_sprite = sFutaCondom;

// Guarded X-Ray draw
var _lx = (sprite_exists(legacy_xray_sprite) && legacy_xray_sprite != -1) ? legacy_xray_sprite : sFutaXray;
draw_sprite_ext(_lx, 0, draw_x, draw_y, scale_x, scale_y, 0, c_white, 1);
```

---

### 12. [DR-12] [Deeproom Mobile Custom] Clean Portrait Unloading & Cross-Character Isolation

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Inside `func_load_custom_futa()`

Prevents previously loaded custom character portraits from persisting in memory when switching to another pack that lacks portrait art.

```gml
f_port = string(arg0) + "/custom_portrait.png";
if (file_exists(f_port))
{
    if (sprite_exists(legacy_custom_portrait)) sprite_delete(legacy_custom_portrait);
    legacy_custom_portrait = sprite_add(f_port, 10, false, false, portrait_origin_x, portrait_origin_y);
}
else
{
    legacy_custom_portrait = -1; // Clean reset prevents asset bleeding
}
```

---

### 13. [DR-13] [Deeproom Mobile Custom] Dynamic Composite Thumbnail Slicing & Frame Fallback

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Inside Character Selector thumbnail lazy loader

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
}
```

---

## Part 4: Touch UI, Character Selection Screen (CSS) & Navigation

### 14. [DR-14] [Deeproom Mobile Custom] CSS Auto-Scroll & Centering Math (Jump-to-Selected)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Character selection modal opening block (~line 16600)

Calculates the horizontal scroll position to center the currently equipped partner upon opening the 2-row character grid:

```gml
var _max_scroll = max(0, _total_content_w - room_width);
if (!variable_instance_exists(id, "_sel_jump_done") || !_sel_jump_done)
{
    _sel_jump_done = true;
    var _cur_idx = (selector_mode == 0) ? custom_futa_index : custom_wife_index;
    if (_cur_idx >= 0 && _cur_idx < _futa_count)
    {
        var _jump_pair = _cur_idx div 2;
        var _jump_scroll = clamp((_jump_pair * (_cell_w + _pad)) - (room_width * 0.5) + (_cell_w * 0.5), 0, _max_scroll);
        futa_selector_menu.scroll = _jump_scroll;
        futa_selector_menu.scroll_lerp = _jump_scroll;
    }
}

if (!futa_selector_open) { _sel_jump_done = false; selector_favs_only = false; }
```

---

### 15. [DR-15] [Deeproom Mobile Custom] CSS Equipped Partner Pulsing Gold Border & Title Star

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Thumbnail card border rendering loop (~line 16750)

Draws an animated pulsing gold glow border and a gold star label above the card of the currently equipped partner:

```gml
var _is_equipped = (_ci == ((selector_mode == 0) ? custom_futa_index : custom_wife_index));
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

---

### 16. [DR-16] [Deeproom Mobile Custom] CSS Card Click Isolation & Star Hitbox Disentanglement (!_star_hover)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Character selection modal card loop (~lines 20950–21050)

Guarantees that tapping the top-right star bookmark icon does NOT trigger character card selection or close the modal:

```gml
// 1. Star button hitbox and click consumption
var _star_w = 18;
var _star_h = 18;
var _star_x1 = (_cx + _cell_w) - _star_w;
var _star_y1 = _cy;
var _star_x2 = _cx + _cell_w;
var _star_y2 = _cy + _star_h;

var _star_hover = point_in_rectangle(mouse_x, mouse_y, _star_x1 - 2, _star_y1 - 2, _star_x2 + 2, _star_y2 + 2);
if (os_type == os_android || os_type == os_ios)
{
    if (point_in_rectangle(device_mouse_x(0), device_mouse_y(0), _star_x1 - 2, _star_y1 - 2, _star_x2 + 2, _star_y2 + 2))
    {
        _star_hover = true;
    }
}

// 2. Star click consumes input so card selection is not fired
if ((mouse_check_button_pressed(mb_left) || device_mouse_check_button_pressed(0, mb_left)) && _star_hover)
{
    ini_open("setting_data.sav");
    var _sec = (selector_mode == 0) ? "favs_futa" : "favs_wife";
    if (_is_fav) { ds_map_delete(_fav_map, _fname); ini_key_delete(_sec, _fname); }
    else { ds_map_add(_fav_map, _fname, 1); ini_write_real(_sec, _fname, 1); }
    ini_close();
    mouse_clear(mb_left); // Consumes click
}

// 3. Isolated card equip check with !_star_hover guard
var _cell_hover = point_in_rectangle(mouse_x, mouse_y, _cx, _cy, _cx + _cell_w, _cy + _cell_h) && !_star_hover;
if (mouse_check_button_pressed(mb_left) && !title && !_star_hover && _cell_hover)
{
    // Equip character immediately and close modal
}
```

---

### 17. [DR-17] [Deeproom Mobile Custom] CSS Geometric Vector Star Badges, Silent Click Isolation & Dynamic Filter

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Thumbnail card drawing loop (~lines 20950–21050)

Draws crisp 8-point geometric vector star badges on thumbnails without font atlas dependencies. Tapping the star executes `mouse_clear(mb_left);` to consume the click, toggling favorites silently without equipping the character or closing the menu:

```gml
// 1. Star badge geometry & vector burst rendering
var _star_w = 18;
var _star_h = 18;
var _star_x1 = (_cx + _cell_w) - _star_w;
var _star_y1 = _cy;
var _star_x2 = _cx + _cell_w;
var _star_y2 = _cy + _star_h;

var _bcx = (_star_x1 + _star_x2) * 0.5;
var _bcy = (_star_y1 + _star_y2) * 0.5;
draw_set_color(_is_fav ? make_color_rgb(255, 215, 0) : make_color_rgb(35, 35, 35));
draw_rectangle(_star_x1, _star_y1, _star_x2, _star_y2, false);
draw_set_color(_is_fav ? c_white : make_color_rgb(130, 130, 130));
draw_rectangle(_star_x1, _star_y1, _star_x2, _star_y2, true);

// 8-point geometric vector lines
draw_set_color(_is_fav ? c_black : make_color_rgb(200, 200, 200));
draw_line_width(_bcx - 5, _bcy, _bcx + 5, _bcy, 2);
draw_line_width(_bcx, _bcy - 5, _bcx, _bcy + 5, 2);
draw_line_width(_bcx - 3, _bcy - 3, _bcx + 3, _bcy + 3, 2);
draw_line_width(_bcx - 3, _bcy + 3, _bcx + 3, _bcy - 3, 2);

// 2. Silent bookmark toggle with click consumption
if ((mouse_check_button_pressed(mb_left) || device_mouse_check_button_pressed(0, mb_left)) && _star_hover)
{
    ini_open("setting_data.sav");
    var _sec = (selector_mode == 0) ? "favs_futa" : "favs_wife";
    if (_is_fav) { ds_map_delete(_fav_map, _fname); ini_key_delete(_sec, _fname); }
    else { ds_map_add(_fav_map, _fname, 1); ini_write_real(_sec, _fname, 1); }
    ini_close();
    mouse_clear(mb_left); // Consumes click so character is NOT equipped
}

// 3. Isolated card equip check
var _cell_hover = point_in_rectangle(mouse_x, mouse_y, _cx, _cy, _cx + _cell_w, _cy + _cell_h) && !_star_hover;
if (mouse_check_button_pressed(mb_left) && !title && !_star_hover && _cell_hover)
{
    // Equip character immediately and close modal
}
```

---

### 18. [DR-18] [Deeproom Mobile Custom] CSS Modal Input Priority & Background Suppression

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)` & `Step (0)`
- **Anchor**: Background button checks (~lines 8092, 14251, 20830)

When `futa_selector_open == true`, all background UI buttons and the floating overlay are suppressed to give 100% exclusive touch capture to the character grid:

```gml
// Master Modal Supremacy & Total Input Isolation Shield (Top of Step_0 and Draw_0)
if ((variable_instance_exists(id, "futa_selector_open") && futa_selector_open) || (variable_instance_exists(id, "mob_expanded") && mob_expanded))
{
    // Force close every single vanilla menu panel instantly
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

// Full 100% opaque black backdrop inside CSS:
draw_set_alpha(1.0);
draw_rectangle_color(0, 0, room_width, room_height, c_black, c_black, c_black, c_black, false);

// Selector close cleanup:
futa_selector_open = false;
_sel_jump_done = false;
selector_favs_only = false;
```

---

### 19. [DR-19] [Deeproom Mobile Custom] CSS Header Layout: Left Search Bar, Right-Side [FAV: ALL/ON] Toggle & Locked Close Button

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Character selector header bar (~lines 20850–21100)

Establishes clean non-colliding header geometry with search bar on left, favorite filter toggle to the right, and close button locked globally to `fntFontSmall`:

```gml
// 1. Header geometry
var _bar_x1 = 20;
var _bar_x2 = room_width - 120;
var _bar_y1 = 4;
var _bar_y2 = 20;

var _fav_btn_x1 = room_width - 114;
var _fav_btn_x2 = room_width - 48;
var _fav_btn_hover = point_in_rectangle(mouse_x, mouse_y, _fav_btn_x1 - 2, _bar_y1 - 2, _fav_btn_x2 + 2, _bar_y2 + 2);
var _bar_hover = point_in_rectangle(mouse_x, mouse_y, _bar_x1 - 2, _bar_y1 - 2, _bar_x2 + 2, _bar_y2 + 2);

// Toggle [FAV: ALL] / [FAV: ON]
if (mouse_check_button_pressed(mb_left))
{
    if (_fav_btn_hover)
    {
        selector_favs_only = !selector_favs_only;
        futa_selector_menu.scroll = 0;
        futa_selector_menu.scroll_lerp = 0;
        if (selector_search_focused && (os_type == os_android || os_type == os_ios)) keyboard_virtual_hide();
        selector_search_focused = false;
        mouse_clear(mb_left);
    }
    else if (_bar_hover)
    {
        if (selector_search_focused == false)
        {
            selector_search_focused = true;
            keyboard_string = selector_search_string;
            if (os_type == os_android || os_type == os_ios) keyboard_virtual_show(0, 0, 0, false);
        }
    }
    else
    {
        if (selector_search_focused && (os_type == os_android || os_type == os_ios)) keyboard_virtual_hide();
        selector_search_focused = false;
    }
}

// 2. Draw Filter Button to right of search bar
draw_set_color(selector_favs_only ? make_color_rgb(255, 215, 0) : make_color_rgb(45, 45, 45));
draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, false);
draw_set_color(selector_favs_only ? c_white : make_color_rgb(140, 140, 140));
draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, true);
draw_set_font(fntFontSmall);
draw_set_halign(fa_center);
draw_set_valign(fa_middle);
draw_set_color(selector_favs_only ? c_black : c_white);
draw_text((_fav_btn_x1 + _fav_btn_x2) * 0.5, (_bar_y1 + _bar_y2) * 0.5, selector_favs_only ? "FAV: ON" : "FAV: ALL");

// 3. Close button 'X' locked to fntFontSmall globally
comment = "X close button top right";
var _close_x = room_width - 20;
var _close_y = 12;
var _close_hover = point_in_rectangle(mouse_x, mouse_y, _close_x - 10, _close_y - 10, _close_x + 10, _close_y + 10);
draw_set_font(fntFontSmall); // Locked across all states
draw_set_halign(fa_center);
draw_set_valign(fa_middle);
draw_set_color(_close_hover ? c_purple : c_white);
draw_text_transformed(_close_x, _close_y, "X", 0.85, 0.85, 0);

// 4. Automatic filter reset on close
if (mouse_check_button_pressed(mb_left) && _close_hover)
{
    futa_selector_open = false;
    _sel_jump_done = false;
    selector_favs_only = false;
}
```

---

### 20. [DR-20] [Deeproom Mobile Custom] CSS Mobile Virtual Keyboard Trigger & Auto-Dismissal

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Search input loop (~line 16670)

```gml
if (selector_search_focused)
{
    selector_search_string = keyboard_string;
}

if ((keyboard_check_pressed(vk_escape) || keyboard_check_pressed(vk_enter)) && selector_search_focused)
{
    if (os_type == os_android || os_type == os_ios) keyboard_virtual_hide();
    selector_search_focused = false;
    if (keyboard_check_pressed(vk_escape))
    {
        selector_search_string = "";
        keyboard_string = "";
    }
}
```

---

### 21. [DR-21] [Deeproom Mobile Custom] Mutual Panel Exclusivity & Radar Chart Isolation

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Stat graph rendering blocks (~lines 9800, 15500)

```gml
// Lover radar chart condition
if (newlover_menu_toggle == true && newwife_menu_toggle == false && options_toggle == false && orgasm == false && futa_selector_open == false)
{
    // Render Lover Stat Radar Chart
}

// Wife radar chart condition
if (newwife_menu_toggle == true && newlover_menu_toggle == false && options_toggle == false && orgasm == false && futa_selector_open == false)
{
    // Render Wife Stat Radar Chart
}
```

---

### 22. [DR-22] [Deeproom Mobile Custom] Climax Screen Protection & Panel Auto-Closing

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Climax trigger check (~line 5880) and partner switch buttons (~lines 8092, 14251)

```gml
// 1. Force close floating panels upon climax trigger
if (orgasm_start == true || orgasm == true)
{
    newlover_menu_toggle = false;
    newwife_menu_toggle = false;
}

// 2. Hide partner switch buttons entirely during climax animation
if (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)
{
    // Draw NEW LOVER Button
}

if (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)
{
    // Draw NEW WIFE Button
}
```

---

### 23. [DR-23] [Deeproom Mobile Custom] Translucent Mobile Overlay with Strict Modal Z-Ordering

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Mobile touch overlay root block (~line 20830)

```gml
// Suppress overlay rendering whenever character selector is open
if (futa_selector_open == false)
{
    var _fab_alpha = (mob_expanded || _fab_over) ? 0.40 : 0.12;
    // Render floating action button and quick drawer
}
```

---

### 24. [DR-24] [Deeproom Mobile Custom] Single-Trigger Overlay Action Execution

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Quick bar touch handler (~line 20920)

```gml
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
}
```

---

### 25. [DR-25] [Deeproom Mobile Custom] Uninterrupted 8-Mechanic Gameplay Interaction & Disclaimer One-Time Gate

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Gameplay interaction input checks (~lines 6000-7500)

```gml
// Unlocked continuous gameplay interactions while panels are open:
if (manual_mode > 0 && radial_menu_open == false && radial_manual_ui_mode == false)
{
    // Evaluate simultaneous touch interactions (thrust, pump, slap, kiss, etc.)
}

// Gate startup warning disclaimer to show only ONCE on boot (preserves [T] peek mode):
if (mouse_check_button_pressed(mb_left) && point_in_rectangle(mouse_x, mouse_y, _ok_x1, _ok_y1, _ok_x2, _ok_y2))
{
    title = false;
    peek_closed_during_play = true; // Prevents disclaimer from ever showing during keyhole/door peek mode
    disclaimer = false;
}
```

---

### 26. [DR-26] [Deeproom Mobile Custom] Neutralization of Rickroll Fake Crash Loop in Step_0

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Step (0)`
- **Anchor**: Pill interaction handler (~line 2700)

```gml
if (variable_global_exists("rg_chosen_pill") && global.rg_chosen_pill == 99)
{
    global.rg_chosen_pill = -1;
}
```

---

## Part 5: Android Platform & ToyBridge Foundation Systems

### 27. [TB-01] [ToyBridge] Synthetic Right-Click & Touch Hold Engine

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Mobile touch loop (~line 20850)

```gml
if (_mob_touch_d)
{
    mob_lp_timer++;
    if (mob_lp_timer == 22 && !radial_menu_open && title == false && orgasm == false)
    {
        mouse_x = mob_lp_start_x;
        mouse_y = mob_lp_start_y;
        touch_long_press_synthetic = true;
    }
}
```

---

### 28. [TB-02] [ToyBridge] Dual-Column Vertical Menu Layout

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: NEW LOVER and NEW WIFE menu draw loops (~lines 8280, 14450)

```gml
var col_w_px = (panel_w - (menu_pad * 3)) * 0.5;
var col1_x = panel_x + menu_pad + (col_w_px * 0.5);
var col2_x = panel_x + (menu_pad * 2) + col_w_px + (col_w_px * 0.5);

for (var mi = 0; mi < 10; mi++)
{
    var in_col2 = (mi >= 5);
    var menu_cx = in_col2 ? col2_x : col1_x;
    var row_idx = in_col2 ? (mi - 5) : mi;
    var item_cy = items_start_y + (item_h * 0.5) + (row_idx * item_step);
    // Render dual-column touch buttons
}
```

---

### 29. [TB-03] [ToyBridge] Momentum Drag-to-Scroll Accumulator (menu_scroll_update)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Function definition `menu_scroll_update`

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
            arg0.touch_drag_accum += (mouse_y - arg0.touch_drag_last_y);
            arg0.touch_drag_last_y = mouse_y;
            var _row_height = 64;
            while (arg0.touch_drag_accum <= -_row_height)
            {
                arg0.scroll = min(arg0.scroll + 1, max(0, arg1 - arg2));
                arg0.touch_drag_accum += _row_height;
            }
            while (arg0.touch_drag_accum >= _row_height)
            {
                arg0.scroll = max(arg0.scroll - 1, 0);
                arg0.touch_drag_accum -= _row_height;
            }
        }
    }
}
```

---

### 30. [TB-04] [ToyBridge] SIZES Options Page Hyper-Scale Toggle (TouchHyperToggle)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Options page 2 (SIZES), under wife sliders

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
    func_save_settings();
}
```

---

### 31. [TB-05] [ToyBridge] On-Device Mod Sharing Activity (wbmods.PhoneImportActivity)

- **Target Platform**: Android Dalvik / ART Runtime (`classes2.dex`)
- **Package**: `wbmods.PhoneImportActivity`

```java
package wbmods;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;

public class PhoneImportActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent intent = getIntent();
        Uri uri = intent.getData();
        if (uri != null) {
            File inbox = new File(getFilesDir(), "phone_inbox");
            inbox.mkdirs();
            File dest = new File(inbox, "import_" + System.currentTimeMillis() + ".zip");
            try (InputStream in = getContentResolver().openInputStream(uri);
                 FileOutputStream out = new FileOutputStream(dest)) {
                byte[] buf = new byte[8192];
                int len;
                while ((len = in.read(buf)) > 0) out.write(buf, 0, len);
            } catch (Exception ignored) {}
        }
        Intent launch = getPackageManager().getLaunchIntentForPackage(getPackageName());
        if (launch != null) startActivity(launch);
        finish();
    }
}
```

---

### 32. [DR-27] [Deeproom Mobile Custom] Pure Python Binary AXML Editor & APK DEX Bundling

- **Target File**: `AndroidManifest.xml` (inside APK root)
- **Module**: `AxmlEditor` in `WB_Mobile_Patcher.py`

Directly edits binary XML chunks without `apktool` or `aapt2`:
- Type `0x0001` (String Pool): Appends `wbmods.PhoneImportActivity`, intent action strings (`android.intent.action.VIEW`, `android.intent.action.SEND`), and MIME types.
- Type `0x0180` (Resource Map): Maps attribute IDs (`android:name`, `android:exported`, `android:mimeType`).
- Type `0x0102` (Start Element): Injects `<activity>` and `<intent-filter>` tags into `<application>`.
- Secondary DEX Injection: Bundles `phone_import.dex` into the APK root as `classes2.dex`.

```xml
<activity
    android:name="wbmods.PhoneImportActivity"
    android:exported="true"
    android:theme="@android:style/Theme.NoDisplay">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="application/zip" />
        <data android:mimeType="application/x-zip-compressed" />
        <data android:mimeType="application/octet-stream" />
    </intent-filter>
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="application/zip" />
        <data android:mimeType="*/*" />
    </intent-filter>
</activity>
```

---

### 33. [TB-06] [ToyBridge] Optional External UDP Telemetry Broadcast (buttplug_socket)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)` & `Draw (0)`
- **Port**: UDP `45735` to `127.0.0.1`

```gml
// Create_0 Socket Initialization
buttplug_socket = network_create_socket(network_socket_udp);
buttplug_buffer = buffer_create(256, buffer_grow, 1);
buttplug_last_send = 0;
buttplug_port = 45735;

// Draw_0 Telemetry Broadcast Loop (30Hz cap)
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

---

### 34. [DR-28] [Deeproom Mobile Custom] Pre-Flight Mod Pack Classification & Quarantine Architecture

- **Target Module**: `WB_Mobile_Patcher.py`
- **Functions**: `classify_custom_pack(folder)` & `quarantine_incompatible_packs(mods_dir, quarantine_dir)`

Audits custom pack folders before ingestion to prevent APK build aborts or runtime crashes:
1. Numbered-Alt Check: Flags `r"^custom_data_[0-9]+\.(futa|wife|spouse|bedroom)$"`.
2. Missing Descriptor Check: Flags packs lacking `custom_data.*`.
3. Legacy Numbered Sprite Check: Flags `r"^custom_(futa|wife|spouse)_[a-z0-9_]+_[0-9]+\.png$"`.
4. Automated Isolation: Non-portable packs are relocated to `output/quarantine/<category>/<pack_name>`, preserving valid packs for packaging.

---

### 35. [DR-29] [Deeproom Mobile Custom] Universal ModRoom & Legacy Spouse Format Detection (check_custom_wife)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Inside `check_custom_wife(path)`

#### Architectural Role
Desktop ModRoom only checked for `custom_wife_mating_press.png`. Legacy Wife's Bedroom spouse packs use `custom_mating_press.png` and `custom_data.spouse` or `custom_data.wife`. This universal checker bridges both conventions so all community packs load seamlessly:

```gml
function check_custom_wife(arg0)
{
    var check_struct = {};
    check_struct.custom_wife_mating_press = file_exists(string(arg0) + "/custom_wife_mating_press.png");
    check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_mating_press.png");
    check_struct.custom_data_spouse = file_exists(string(arg0) + "/custom_data.spouse");
    check_struct.custom_data_wife = file_exists(string(arg0) + "/custom_data.wife");

    // Returns true if either ModRoom or Legacy Spouse format is verified
    return (check_struct.custom_wife_mating_press || (check_struct.custom_mating_press && (check_struct.custom_data_spouse || check_struct.custom_data_wife)));
}
```

---

### 36. [DR-30] [Deeproom Mobile Custom] Mobile Audio & Voice Pack Streaming (custom_music & custom_sounds)

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)`
- **Anchor**: Audio initialization block (~line 180)

#### Architectural Role
Dynamically enumerates and streams custom background music (`custom_music/*.ogg`) and custom voice packs (`custom_sounds/futa/*` and `custom_sounds/wife/*`) using manifest-compatible virtual directory search (`tc_ff_first`):

```gml
// -------------------------------------------------------------------------
// Custom Background Music Scanner
// -------------------------------------------------------------------------
var _music_base = tc_wd + "/custom_music";
var _f = tc_ff_first(_music_base + "/*.ogg", 0);
while (_f != "")
{
    var _full_music = _music_base + "/" + _f;
    if (file_exists(_full_music))
    {
        ds_list_add(custom_music_list, _full_music);
    }
    _f = tc_ff_next();
}
tc_ff_close();

// -------------------------------------------------------------------------
// Custom Voice Pack Scanner
// -------------------------------------------------------------------------
var _voice_base = tc_wd + "/custom_sounds/futa";
var _vf = tc_ff_first(_voice_base + "/*", 16);
while (_vf != "")
{
    var _full_vf = _voice_base + "/" + _vf;
    if (tc_dir_exists(_full_vf))
    {
        ds_list_add(custom_voice_folders, _full_vf);
    }
    _vf = tc_ff_next();
}
tc_ff_close();
```

---

### 37. [DR-31] [Deeproom Mobile Custom] Anatomy Sprite & Boob Box Pre-Flight Safety Guards

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Create (0)` & `Draw (0)`
- **Anchor**: Event start of `Create (0)` and anatomy draw routines (~line 2800)

#### Architectural Role
Prevents unhandled GameMaker runner crashes when evaluating uninitialized variables (`boob_box`) or drawing anatomy accessories when sprite assets are missing:

```gml
// Create_0 upfront variable initialization
boob_box = false;
cowgirl_origin_y = 84;

// Draw_0 anatomy render shield
if (variable_instance_exists(id, "anatomy_sprite") && sprite_exists(anatomy_sprite) && anatomy_sprite != -1)
{
    draw_sprite_ext(anatomy_sprite, 0, draw_x, draw_y, scale_x, scale_y, 0, c_white, 1);
}
```

---

### 38. [DR-32] [Deeproom Mobile Custom] Screen Boundary Clamping for Mobile Dragging Menus

- **Target Object**: `oFutaMatingPress`
- **Target Event**: `Draw (0)`
- **Anchor**: Floating menu drag update loops (~lines 8220, 14380)

#### Architectural Role
Restricts floating panels (`NEW LOVER` and `NEW WIFE`) within visible screen coordinates during touchscreen drag interactions, preventing panels from being dragged off-screen:

```gml
if (newlover_dragging)
{
    var _min_cx = (menu_w_px * 0.5) + 4;
    var _max_cx = room_width - ((menu_w_px * 0.5) + 4);
    newlover_menu_cx = clamp(mouse_x + drag_offset_x, _min_cx, _max_cx);
}

if (newwife_dragging)
{
    var _min_cx = (menu_w_px * 0.5) + 4;
    var _max_cx = room_width - ((menu_w_px * 0.5) + 4);
    newwife_menu_cx = clamp(mouse_x + drag_offset_x, _min_cx, _max_cx);
}
```

---

### 39. [DR-33] [Deeproom Mobile Custom] Dual-Engine Bytecode Ingestion, v1.5 Manifest Streaming & Unified Alphabetical Ingestion

- **Target Module**: `WB_Mobile_Patcher.py`
- **Functions**: `patch_game_apk()`, `detect_mod_engine_version()`, `find_matching_base_apk()`, `gather_custom_assets()`, `generate_manifest_data()`

#### Architectural Role
Eliminates static binary `.droid` backups and machine-specific hardcoded paths from the distribution suite. Dynamically inspects user-provided inputs to automatically determine engine versions, apply dual-engine compilation, and pair with matching base templates:
1. **Intelligent Version Detection**: Evaluates folder nomenclature, unified `custom/` directory structure, and `data.win` binary sizes (v1.5 is ~22.4 MB vs Deeproom 4.0 / v1.4 at ~71.4 MB) via `detect_mod_engine_version()`.
2. **Deeproom 4.0 (v1.4) Engine Pipeline**:
   - Replaces GameMaker scripts with `mobile_engine.bundle` into the provided v1.4 base APK.
   - Ingests v1.5 `custom/` packs directly into `custom_futas/`, `custom_wives/`, and `custom_bedrooms/`, seamlessly merging them into single alphabetical sets (`sorted(set(existing + packs_v))`).
   - Isolates asset output to omit `assets/custom/` in Deeproom builds, preventing duplicate character displays.
3. **Wife's Bedroom v1.5 Engine Pipeline (Standalone)**:
   - Retains 100% native v1.5 bytecode parity without injecting Deeproom-exclusive objects (e.g. `oDialogueManager`), eliminating boot crashes.
   - Surgically patches `func_get_custom_characters()` in native `Create_0` to read `custom/_manifest.txt` directly on Android, populates `custom_lover_folders`, `custom_partner_folders`, and `custom_bedroom_folders`, and activates `custom_sprite_loaded = true`.
4. **Zero Base APKs in Repository Core**: Base APKs are strictly user-supplied via `input/` or drag-and-drop, keeping the repository clean and free of copyrighted game binaries.
5. **Pure Relative Resolution**: All tool, keystore, input, and output lookups resolve strictly relative to `patcher_dir` (`core/`, `input/`, `output/`), eliminating all hardcoded machine drives, user paths, or environment variables.

---

### 40. [DR-34] [Deeproom Mobile Custom] Multi-Input Ingestion, Extended CLI, Modular Install Modes & Dynamic Naming

- **Target Module**: `WB_Mobile_Patcher.py`
- **Functions**: `main()`, `prompt_install_options()`, `clean_output_dir()`

#### Architectural Role
Delivers a flexible workflow supporting one-click drag-and-drop, multi-package discovery, interactive setup prompts, and advanced developer CLI automation flags:

1. **Multi-Input Ingestion & Package Selection Architecture**:
   - **Interactive Package Selector**: When multiple game installations or `.zip` archives exist concurrently in `input/`, the tool discovers all candidate packages, detects their engine versions, and renders an interactive numbered menu (defaulting to package [1] on ENTER or in headless `-y` mode).
   - **Multi-Source Mod Merging**: When multiple mod folders or `.zip` archives are dragged together onto the launcher or provided as arguments, the engine accumulates and merges all sources into a unified staging environment, compiling an APK containing all dragged mods combined rather than dropping subsequent inputs.
   - **Loose Pack Aggregation**: If individual character folders (e.g. `input/ankha/custom_data.futa`) are placed directly into `input/` without a parent container, the scanner identifies them as loose packs and ingests `input/` directly as an aggregated mod container.

2. **Extended CLI Toolset**:
   - `--clean`: Automatically purges stale `.apk`, `.idsig`, and `.bak` files from `output/` before compiling.
   - `--fast`: Uses uncompressed storage (`zipfile.ZIP_STORED`), reducing asset packaging time from ~35s to under 6s for rapid local testing.
   - `--validate-only`: Runs a dry-run pre-flight audit of mod folders, verifying pack portability and generating in-memory manifests in 2s without packaging.
   - `-y`, `--yes`: Headless non-interactive execution for automated build scripts.

3. **Interactive Setup Prompts**:
   - **Explicit Default Navigation**: Pressing ENTER on any prompt automatically selects the indicated default choice (capitalized in brackets, e.g. `[Y/n]` = Yes, `[y/N]` = No).
   - **Default Install (`[Y]`)**: Automatically deploys the full mobile engine suite, with optional prompts for output cleaning, toy telemetry, and fast packaging.
   - **Custom Install (`[N]`)**: Granular 9-point component selector allowing individual toggling of Core Engine, Universal Scaling, Stability Guards, Climax Auto-Closing, CSS Grid, Phone Mod Sharing, Toy Telemetry, Output Cleaning, and Fast Mode.

4. **Dynamic Output APK Naming**:
   - Evaluates `original_mod_name` from input `.zip` stem or folder name (e.g. `Misaka_Deeproom 4.0(up to date)_modded.apk`).
   - Automatically sanitizes illegal filesystem characters (`[\/:*?"<>|]`) into underscores.
   - Preserves explicit destination overrides when `-o` / `--output` is provided.
