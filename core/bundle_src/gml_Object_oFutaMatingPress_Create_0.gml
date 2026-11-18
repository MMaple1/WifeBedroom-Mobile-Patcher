// Legacy X-Ray & Kiwami Custom Sperm Sprite Initialization
legacy_xray_sprite = -1;
legacy_custom_xray = -1;
custom_sperm_sprite = -1;
custom_sperm_big_sprite = -1;

// Mobile Anti-Sleep / Display Timeout Prevention
if (os_type == os_android || os_type == os_ios)
{
    os_powersave_enable(false);
}

// Mobile Overlay State Initialization
mob_init = true;
mob_expanded = false;
mob_hitbox_active = false;
mob_release_key = -1;
mob_scroll_y = 0;
mob_drag_start_y = 0;
mob_is_dragging = false;
mob_drag_last_y = 0;
global.mob_touching_menu = false;
mob_lp_timer = 0;
mob_touch_dev = -1;
wife_dt_cache_key = "";
wife_dt_cache_val = false;
mob_lp_start_x = 0;
mob_lp_start_y = 0;

boob_box = false;

function tc_is_save_path(arg0)
{
    // true for a path inside the game's own save folder (folders created on the phone)
    var _gs = game_save_id;
    while (string_length(_gs) > 1 && string_char_at(_gs, string_length(_gs)) == "/")
    {
        _gs = string_copy(_gs, 1, string_length(_gs) - 1);
    }
    return string_length(_gs) > 1 && string_pos(_gs, string(arg0)) == 1;
}

function tc_ini_open_desc(arg0)
{
    // Open a pack descriptor. On Android/iOS GameMaker reads a file from the save area when a copy exists there,
    // and never again from the APK. Older builds opened custom_data.spouse even where it did not exist, which
    // left an empty copy in the save area: every origin then fell back to its default (deepthroat 84 instead
    // of the pack's 150). A shipped descriptor always has [sprite], so a copy without it is such a leftover:
    // delete it and read the APK's file.
    ini_open(arg0);
    if ((os_type == os_android || os_type == os_ios) && !tc_is_save_path(arg0) && !ini_section_exists("sprite"))
    {
        ini_close();
        file_delete(arg0);
        ini_open(arg0);
    }
}

function pm_registry_file()
{
    var _s = game_save_id;
    while (string_length(_s) > 1 && string_char_at(_s, string_length(_s)) == "/")
    {
        _s = string_copy(_s, 1, string_length(_s) - 1);
    }
    return _s + "/phone_mods_registry.txt";
}

function pm_registry_read()
{
    // folders and files created by phone imports, one path per line (no folder listing needed)
    var _out = [];
    var _rf = pm_registry_file();
    if (!file_exists(_rf))
    {
        return _out;
    }
    var _h = file_text_open_read(_rf);
    if (_h != -1)
    {
        while (!file_text_eof(_h))
        {
            var _l = string_replace_all(string_replace_all(file_text_readln(_h), "\r", ""), "\n", "");
            if (_l != "" && !array_contains(_out, _l))
            {
                array_push(_out, _l);
            }
        }
        file_text_close(_h);
    }
    return _out;
}

function pm_registry_write(arg0)
{
    var _h = file_text_open_write(pm_registry_file());
    if (_h != -1)
    {
        for (var _i = 0; _i < array_length(arg0); _i++)
        {
            file_text_write_string(_h, arg0[_i]);
            file_text_writeln(_h);
        }
        file_text_close(_h);
    }
}

function pm_registry_add(arg0)
{
    var _p = string(arg0);
    if (!tc_is_save_path(_p))
    {
        return;
    }
    var _r = pm_registry_read();
    if (!array_contains(_r, _p))
    {
        array_push(_r, _p);
        pm_registry_write(_r);
    }
}

function pm_registry_remove(arg0)
{
    var _p = string(arg0);
    var _r = pm_registry_read();
    var _keep = [];
    for (var _i = 0; _i < array_length(_r); _i++)
    {
        if (_r[_i] != _p && string_pos(_p + "/", _r[_i]) != 1)
        {
            array_push(_keep, _r[_i]);
        }
    }
    pm_registry_write(_keep);
}

function pm_registry_base(arg0)
{
    var _n = string(arg0);
    while (string_pos("/", _n) > 0)
    {
        _n = string_delete(_n, 1, string_pos("/", _n));
    }
    return _n;
}

function tc_norm_path(arg0)
{
    arg0 = string(arg0);
    while (string_pos("//", arg0) > 0)
    {
        arg0 = string_replace_all(arg0, "//", "/");
    }
    if ((os_type == os_android || os_type == os_ios) && !tc_is_save_path(arg0))
    {
        while (string_char_at(arg0, 1) == "/")
        {
            arg0 = string_delete(arg0, 1, 1);
        }
    }
    return arg0;
}

function tc_dir_exists(arg0)
{
    arg0 = tc_norm_path(arg0);
    if (string_char_at(arg0, string_length(arg0)) == "/")
    {
        arg0 = string_copy(arg0, 1, string_length(arg0) - 1);
    }
    if (directory_exists(arg0) || file_exists(arg0 + "/_manifest.txt") || file_exists(arg0)) return true;
    if (string_pos("custom_stuff/", arg0) == 1)
    {
        var _alt = string_delete(arg0, 1, 13);
        if (directory_exists(_alt) || file_exists(_alt + "/_manifest.txt") || file_exists(_alt)) return true;
    }
    else
    {
        var _alt = "custom_stuff/" + arg0;
        if (directory_exists(_alt) || file_exists(_alt + "/_manifest.txt") || file_exists(_alt)) return true;
    }
    return false;
}

function tc_ff_first(arg0, arg1)
{
    tc_ff_items = -1;
    if ((os_type == os_android || os_type == os_ios) && tc_is_save_path(arg0))
    {
        // folders created on the phone have no _manifest.txt: list them with the real file search
        tc_ff_items = [];
        var _real_m = file_find_first(arg0, arg1);
        while (_real_m != "")
        {
            array_push(tc_ff_items, _real_m);
            _real_m = file_find_next();
        }
        file_find_close();
        tc_ff_pos = 0;
        return tc_ff_next();
    }
    var _m = tc_norm_path(arg0);
    var _cut = string_last_pos("/", _m);
    var _mf = (_cut > 0) ? (string_copy(_m, 1, _cut) + "_manifest.txt") : "_manifest.txt";
    if (!file_exists(_mf))
    {
        if (string_pos("custom_stuff/", _mf) == 1)
        {
            var _alt = string_delete(_mf, 1, 13);
            if (file_exists(_alt)) _mf = _alt;
        }
        else
        {
            var _alt = "custom_stuff/" + _mf;
            if (file_exists(_alt)) _mf = _alt;
        }
    }
    if (!file_exists(_mf))
    {
        if (os_type == os_android || os_type == os_ios)
        {
            return "";
        }
        return file_find_first(arg0, arg1);
    }
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
    if (os_type != os_android && os_type != os_ios)
    {
        var _real = file_find_first(arg0, arg1);
        while (_real != "")
        {
            if (!array_contains(tc_ff_items, _real))
            {
                array_push(tc_ff_items, _real);
            }
            _real = file_find_next();
        }
        file_find_close();
    }
    tc_ff_pos = 0;
    return tc_ff_next();
}

function tc_ff_next()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type == os_android || os_type == os_ios)
        {
            return "";
        }
        return file_find_next();
    }
    if (tc_ff_pos >= array_length(tc_ff_items))
    {
        return "";
    }
    tc_ff_pos++;
    return tc_ff_items[tc_ff_pos - 1];
}

function tc_ff_close()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type != os_android && os_type != os_ios)
        {
            file_find_close();
        }
    }
    tc_ff_items = -1;
    tc_ff_pos = 0;
}

tc_ff_items = -1;
tc_ff_pos = 0;
tc_wd = working_directory;
if (string_char_at(tc_wd, string_length(tc_wd)) == "/")
{
    tc_wd = string_copy(tc_wd, 1, string_length(tc_wd) - 1);
}
if (!instance_exists(oDialogueManager))
{
    instance_create_depth(0, 0, 0, oDialogueManager);
}
if (!instance_exists(oAudioManager))
{
    instance_create_layer(0, 0, 0, oAudioManager);
}
default_x = x;
default_y = y;
mouse_draw_x = -1;
mouse_draw_y = -1;
cursor_id = 0;
peek_mode = 0;
prev_peek_mode = -1;
peek_closed_during_play = false;
peek_door_alpha = 0.65;
peek_door_vol = 0.5;
peek_door_zoom = 1.55;
peek_keyhole_zoom = 1.1;
peek_keyhole_vol = 0.6;
peek_keyhole_muffle_cutoff = 1000;
peek_keyhole_muffle_q = 0.8;
insert = false;
halfway_spoken = false;
window_set_cursor(cr_none);
comment = "pullout mechanics";
pullout_flag = false;
action_lock = false;
comment = "sex, movement and edging";
thrust = 0;
thrust_speed = 2;
thrust_strength = 3;
thrust_middle = 0.5;
thrust_time = 0;
tc_kbv = false;
tc_kbv_seen = false;
tc_edit_for = -1;
tc_orig = "";
tc_commit = 0;
tc_hyper = file_exists(game_save_id + "hyper_sizes.on");
touch_hold_start = 0;
touch_long_press_fired = false;
touch_long_press_synthetic = false;
thrust_set = 0;
stroke_depth = 1;
stroke_speed = 1;
plap = false;
plap_scale = 0;
plap_x = 0;
plap_y = 0;
drip_pump_scale = 0;
pump_scale = 0;
womb_spurts = [];
schlick_timer = 0;
ball_size = 1;
womb_size = 1;
womb_size_lerp = 1;
balls_jiggle = 0;
balls_jiggle_move = 0;
ball_set = 0;
top_ass_jiggle = 0;
top_ass_jiggle_move = 0;
bottom_ass_jiggle = 0;
bottom_ass_jiggle_move = 0;
top_boob_jiggle = 0;
top_boob_jiggle_move = 0;
bottom_boob_jiggle = 0;
bottom_boob_jiggle_move = 0;
loads = 0;
max_loads = 3;
top_body_jiggle = 0;
body_jiggle = 0;
body_jiggle_move = 0;
condom_jiggle = 0;
condom_jiggle_move = 0;
sperm_jiggle = 0;
sperm_jiggle_move = 0;
slap_boost = 1;
sex_position = 0;
position_menu_toggle = false;
orgasm = false;
orgasm_start = false;
orgasm_pumps = 0;
orgasm_moan_chance = 0.45;
orgasm_last_moan = -1;
orgasm_sound_played = false;
orgasm_sound_cooldown = 0;
orgasm_pumps_max = 15;
pending_orgasm = false;
shot_queue = 0;
shot_interval_timer = 0;
shot_interval = 8;
shot_burst_size = 2;
shot_dir = 1;
shot_internal = false;
shot_volume_per_particle = 0;
shot_clench_only = false;
shot_condom_volume_per_particle = 0;
shot_fill_per_particle = 0;
moan_sound = -1;
moan_pitch = 1;
moan_previous = -1;
moaning = true;
moan_slow_list = ds_list_create();
moan_fast_list = ds_list_create();
orgasm_list = ds_list_create();
custom_moan_slow_list = ds_list_create();
custom_moan_fast_list = ds_list_create();
custom_orgasm_list = ds_list_create();
custom_default_moans = false;
moan_threshold = 0.6;
radio_toggle = false;
radio_track_list = ds_list_create();
radio_track_index = 0;
radio_stream = -1;
radio_instance = -1;
radio_volume = 1;
radio_has_tracks = false;
radio_slider_dragging = false;
radio_seek_dragging = false;
radio_marquee_offset = 0;
radio_marquee_timer = 0;
radio_is_playing = false;
radio_shuffle = false;
radio_advance_cooldown = 0;

function func_radio_scan()
{
    ds_list_clear(radio_track_list);
    var _base = (os_type == os_android || os_type == os_ios) ? "custom_stuff/custom_music" : (tc_wd + "/custom_stuff/custom_music");
    var _f = tc_ff_first(_base + "/*.ogg", 0);
    if (_f == "")
    {
        tc_ff_close();
        _base = (os_type == os_android || os_type == os_ios) ? "custom_music" : (tc_wd + "/custom_music");
        _f = tc_ff_first(_base + "/*.ogg", 0);
    }
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

function func_radio_get_track_name(arg0)
{
    var _full = ds_list_find_value(radio_track_list, arg0);
    var _name = filename_name(_full);
    var _dot = string_last_pos(".", _name);
    if (_dot > 0)
    {
        _name = string_copy(_name, 1, _dot - 1);
    }
    return _name;
}

function func_radio_play(arg0)
{
    if (!radio_has_tracks)
    {
        exit;
    }
    var _count = ds_list_size(radio_track_list);
    if (arg0 < 0)
    {
        arg0 = _count - 1;
    }
    if (arg0 >= _count)
    {
        arg0 = 0;
    }
    radio_track_index = arg0;
    if (audio_exists(radio_stream))
    {
        audio_stop_sound(radio_stream);
    }
    var _path = ds_list_find_value(radio_track_list, radio_track_index);
    radio_stream = audio_create_stream(_path);
    if (audio_exists(radio_stream))
    {
        radio_instance = audio_play_sound(radio_stream, 1, false);
        if (audio_exists(radio_instance))
        {
            audio_sound_gain(radio_instance, radio_volume, 0);
        }
    }
    radio_is_playing = audio_exists(radio_stream);
    radio_marquee_offset = 0;
    radio_marquee_timer = 60;
}

function func_radio_stop()
{
    if (audio_exists(radio_instance))
    {
        audio_stop_sound(radio_instance);
    }
    if (audio_exists(radio_stream))
    {
        audio_stop_sound(radio_stream);
    }
    radio_instance = -1;
    radio_stream = -1;
    radio_is_playing = false;
}

func_radio_scan();
cs_toggle = false;
cs_panel_tab = 0;
cs_futa_packs = ds_list_create();
cs_futa_pack_names = ds_list_create();
cs_futa_pack_index = 0;
cs_futa_alt_index = 0;
cs_futa_alt_names = ds_list_create();
cs_moan_slow_list = ds_list_create();
cs_moan_fast_list = ds_list_create();
cs_orgasm_list = ds_list_create();
cs_orgasm_alt_list = ds_list_create();
cs_moan_chance_slow = 0.4;
cs_moan_chance_fast = 0.55;
cs_orgasm_grunt_chance = 0.45;
cs_orgasm_playing = false;
cs_wife_pack_index = 0;
cs_wife_alt_index = 0;
cs_wife_alt_names = ds_list_create();
cs_wife_moan_slow_list = ds_list_create();
cs_wife_moan_fast_list = ds_list_create();
cs_wife_orgasm_list = ds_list_create();
cs_wife_orgasm_alt_list = ds_list_create();
cs_wife_moan_chance_slow = 0.35;
cs_wife_moan_chance_fast = 0.55;
cs_wife_moan_sound = -1;
cs_wife_moan_previous = -1;
cs_wife_orgasm_sound_played = false;
cs_wife_kiss_enabled = true;
cs_slider_dragging = -1;
custom_audio_storage = ds_map_create();
cs_last_moan_slow = -1;
cs_last_moan_fast = -1;
cs_last_orgasm = -1;
encouraged = false;
pump_delay = 90;
orgasm_timer_max = pump_delay;
orgasm_timer = pump_delay;
orgasm_sec_timer = 60;
clench_hold_timer = 0;
clench_relax_timer = 0;
edge_boost = 1;
edge_charge = 0;
edge_snap_timer = 0;
slam_timer = 0;
slam_pending = false;
is_dragging = false;
comment = "pull resistance and desperate edge sequence";
uninserted_timer = 0;
desperate_edge_state = 0;
desperate_edge_timer = 0;
desperate_had_condom = false;
desperate_had_broken_condom = false;
condom_strain_played = false;
desperate_condom_size = 0;
desperate_condom_volume = 0;
edge_control_lock = false;
comment = "snap dark overlay alpha";
snap_dark_alpha = 0;
comment = "ball-click orgasm speed mechanic";
ball_click_boost = 0;
ball_holding = false;
comment = "snap: save player stroke sliders before overriding, restore after ejaculation";
snap_saved_stroke_speed = 0;
snap_saved_stroke_depth = 0;
snap_delay_timer = 0;
comment = "snap stage machine state";
snap_stage = 0;
snap_stage_timer = 0;
snap_had_condom = false;
snap_had_broken_condom = false;
snap_condom_size = 0;
snap_condom_volume = 0;
condom = false;
condom_size = 0;
condom_volume = 0;
condom_color = make_color_rgb(random_range(16, 255), random_range(16, 255), random_range(16, 255));
futa_score = 0;
score_combo = 0;
score_combo_timer = 0;
score_combo_scale = 0;
score_combo_mult = 0;
score_combo_mods = ds_list_create();
impregnate = false;
impregnation_timer = 0;
impregnation_scale = 0;
impregnation_counter = 0;
wife_climax_counter = 0;
impregnation_combo = 0;
breeding_milestone_count = [5, 8, 13, 21, 30, 40, 50, 60, 75, 100, 150, 200, 300, 500, 1000, 2000, 4000, 9001];
milestone_index = -1;
last_milestone_index = -1;
climax_combo = 0;
sperm_choice = -1;
bottom_ass_size = 1;
bottom_boob_size = 1;
comment = "kissing";
kiss_timer = 0;
kiss_flag = false;
kiss_flag_prev = false;
kiss_toggle = 1;
dynamic_kiss_toggle = true;
last_kiss_tier = 0;
comment = "reenter mechanic";
reenter_flag = false;
reenter_max_timer = 180;
reenter_timer = 0;
reenter_toggle = false;
options_toggle = false;
actions_menu_toggle = false;
options_page = 0;
last_valid_options_page = 0;
tab_quicknav_open = false;
tab_quicknav_cooldown = 0;
bg_randomize_colors = true;
saved_bg_wallpaper = -1;
bunny_panel_x_saved = 300;
bunny_panel_y_saved = 30;
bunny_small_x_saved = 300;
bunny_small_y_saved = 25;
saved_bg_carpet = -1;
saved_bg_trim = -1;
saved_bg_dresser = -1;
saved_bg_mattress = -1;
saved_bg_frame = -1;
saved_bg_ship = -1;
saved_bg_console = -1;
saved_bg_screen = -1;
saved_bg_glass = -1;
saved_bg_vip_wall = -1;
saved_bg_vip_stage = -1;
saved_bg_vip_pole = -1;
saved_bg_vip_underwear = -1;
saved_bg_vip_condoms = -1;
saved_bg_vip_lotion = -1;
saved_bg_vip_mattress = -1;
saved_bg_vip_frame = -1;
saved_bg_beach_water = -1;
saved_bg_beach_sky = -1;
saved_bg_beach_sun = -1;
saved_bg_beach_clouds = -1;
saved_bg_beach_sand = -1;
saved_bg_beach_stuff = -1;
saved_bg_office_wall = -1;
saved_bg_office_floor = -1;
saved_bg_office_desk = -1;
saved_bg_dungeon_floor = -1;
saved_bg_dungeon_wall = -1;
saved_bg_dungeon_gate = -1;
saved_bg_dungeon_chest = -1;
saved_bg_dungeon_chesttrim = -1;
saved_bg_dungeon_torch = -1;
saved_bg_dungeon_flame = -1;
prev_background_id = -1;
hearts_toggle = true;
global.pop_sound_toggle = true;
manual_mode = 0;
manual_auto_pumps = false;
manual_cursor_free = false;
manual_prev_mouse_y = mouse_y;
manual_progress_delta = 0;
manual_plap_delta = 0;
manual_pump_cooldown = 0;
manual_pump_cooldown_max = 17;
manual_pump_windup = 50;
manual_pump_speed = 3;
manual_full_orgasm_cooldown = 0;
manual_full_orgasm_cooldown_max = 60;
manual_mode_text_x = 0;
manual_mode_text_y = 0;
manual_mode_text_x = 0;
manual_mode_text_y = 0;
manual_last_mode = 1;
manual_label_hover = false;
manual_orgasm_inside_pending = false;
edge_hold_timer = 0;
edge_hold_threshold = 18;
edge_hold_active = false;
edge_hold_charge = 0;
edge_hold_charge_speed = 0.009;
radial_menu_open = false;
radial_sub_menu = "";
radial_rc_hold_timer = 0;
radial_rc_hold_threshold = 10;
radial_rc_held = false;
radial_saved_open = false;
radial_saved_sub = "";
radial_reopen_timer = 0;
radial_val_dragging = -1;
radial_val_inputting = -1;
radial_sz_dragging = -1;
radial_sz_inputting = -1;
radial_settings_dragging = -1;
radial_values_tab = 0;
radial_mg_dragging = -1;
radial_mg_inputting = -1;
radial_manual_ui_mode = false;
radial_panel_from_radial = false;
radial_panel_close_grace = 0;
radial_lc_close_grace = 0;
radial_panel_return_sub = "";
radial_panel_return_wait = 0;
manual_thrust_sens = 0.05;
manual_thrust_strength = 2;
manual_hip_sens = 0.5;
combo_text_max = 0;
frustration_toggle = true;
rand_pumps_toggle = false;
rand_pump_delay_min = 130;
rand_pump_delay_max = 600;
continuous_toggle = false;
continuous_timer = 0;
custom_clench_toggle = 0;
char_dialogue_toggle = true;
comment = "slipping mechanic";
slip_chance = 1;
slip_flag = false;
slip_toggle = false;
slip_immunity = false;
hair_slider_grab = "";
top_slider_grab = "";
bottom_slider_grab = "";
length_slider_grab = "";
girth_slider_grab = "";
balls_slider_grab = "";
stockings_slider_grab = "";
cum_slider_grab = "";
womb_inflation_slider_grab = "";
condom_break_slider_grab = "";
top_ass_slider_grab = "";
top_boob_slider_grab = "";
bottom_ass_slider_grab = "";
bottom_legs_slider_grab = "";
bottom_boob_slider_grab = "";
any_slider_grab = false;
virility_modifier = 1;
cum_volume_modifier = 1;
drink_timer = 0;
old_value = 0;
womb_inflation_toggle = true;
womb_inflation_scale = 1;
cum_batching_toggle = false;
condom_break_threshold = 10;
condom_break_toggle = true;
broken_condom = false;
comment = "dripping stuff";
drip_toggle = true;
drip_timer = 300;
drip_repeat = 0;
drip_repeat_timer = 0;
drain_timer = 0;
drain_target = -1;
drain_speed = irandom_range(30, 90);
outfit_sprite = sOutfitMatingPress1;
wife_outfit_sprite = sWifeNormalCowgirlOutfit1;
outfit_body_color = 4210752;
outfit_hips_color = 4210752;
outfit_legs_color = 4210752;
wife_outfit_body_color = 4210752;
wife_outfit_hips_color = 4210752;
wife_outfit_legs_color = 4210752;
outfit_body_slider_grab = "";
outfit_hips_slider_grab = "";
outfit_legs_slider_grab = "";
penis_shaft_slider_grab = "";
penis_head_slider_grab = "";
womb_slider_grab = "";
virility_slider_grab = "";
cum_modifier_slider_grab = "";
comment = "knotting variables";
knotted = false;
knot_attempt = 0;
knot_state = 0;
knot_delay = 0;
knotted_timer = -1;
knotted_max_time = 600;
knotting_toggle = true;
knotted_slider_grab = "";
knotted_scale = 1;
knot_ratio = 0;
smooth_lock_drop = 0;
knot_pull_count = 0;
smooth_struggle_depth = 0;
comment = "deep pause and balls clench";
insert_prev = false;
deep_pause_timer = 0;
deep_clench_count = 0;
has_paused_thrust = false;
clench_ratio = 0;
clench_prev = false;
comment = "alarm0 value smoothing";
target_thrust_middle = 0;
target_thrust_strength = 0;
target_thrust_speed = 0;
comment = "humping variables";
humping_prev = 0;
current_hump_pullback = 0.1;
air_hump_count = 0;
hump_ratio = 0;
comment = "edge boost idle air hump settings";
eb_idle_hump = false;
eb_idle_hump_timer = 2;
eb_idle_hump_min_boost = 3;
eb_idle_hump_chance_base = 0.17;
eb_idle_hump_chance_per_level = 0.065;
eb_idle_hump_count_min = 2;
eb_idle_hump_count_max = 6;
eb_idle_hump_speed = 3.6;
eb_idle_hump_lerp = 1.15;
eb_idle_hump_pullback = 0.27;
jerking = false;
jerking_distance = 0;
mouse_mode = 0;
cum_splash = 4;
cum_shot_mult = 1;
cum_splash_slider_grab = "";
sex_progress_max = 180;
user_pumps_max = 10;
dripping = 0;
max_combo_display = 0;
hard_thrust_count = 0;
edge_boost_max = 10;
bottom_male_chance = 0.2;
base_multipreg_chance = 10;
fertilization_max = 3;
display_condom_stats_toggle = true;
display_bucket_stats_toggle = true;
pill_menu_toggle = false;
total_pill_amount = 0;
newlover_menu_toggle = false;
background_menu_toggle = false;
comment = "wife climax refactor";
wife_climax = false;
wife_climax_timer = 0;
wife_pleasure = 0;
wife_climax_stamina = 100;
wife_pleasure_max = wife_climax_stamina;
wife_pleasure_threshold = wife_pleasure_max;
wife_climax_stage = 0;
wife_climax_stage_max = 5;
wife_climax_type = "";
wife_size_response = 1;
wife_intensity_response = 1;
wife_cum_response = 1;
wife_reproductive_response = 1;
wife_affection_response = 1;
wife_pain_response = 1;
slap_pleasure_timer = 0;
comment = "orgasm denial";
denial_active = false;
denial_squeeze_progress = 0;
denial_window_timer = 0;
denial_window_max = 90;
denial_success = false;
comment = "ovulation system variables";
ovum_count = 1;
ovulation_timer = 1;
last_pill_milestone = 0;
comment = "types page indices";
futa_body_index = 0;
penis_type_index = 0;
base_penis_type_index = 0;
hair_index = 0;
bangs_index = 0;
outfit_index = 1;
eyes_index = 0;
mouth_index = 0;
wife_body_index = 0;
wife_hair_index = 0;
wife_outfit_index = 0;
custom_wife_index = 0;
custom_wife_alt_index = 0;
custom_wife_alt_max = 1;
custom_futa_index = 0;
custom_futa_alt_index = 0;
custom_futa_alt_max = 1;
comment = "types buttons toggle";
custom_lover_toggle = false;
custom_wife_toggle = false;
socks_toggle = true;
futa_pussy_toggle = true;
futa_boob_index = 0;
outfit_toggle = true;
wife_outfit_toggle = true;
futa_ghost_toggle = false;
futa_ghost_alpha = 1;
comment = "slider stuff";
customize_slider_dragging = -1;
customize_selected_input = -1;
comment = "color square";
color_picker_active = false;
color_picker_target = -1;
current_color = 16777215;
preview_color = 16777215;
picker_value = 255;
ui_y_offset = 15;
comment = "actions menu";
actions_x = room_width - 321;
actions_y = room_height - 130;
actions_dragging = false;
in_action_menu = false;
drag_offset_x = 0;
drag_offset_y = 0;
bunny_panel_drag_x = 0;
bunny_panel_drag_y = 0;
bunny_panel_dragging = false;
bunny_small_drag_x = 0;
bunny_small_drag_y = 0;
bunny_small_dragging = false;
comment = "new lover menu drag state";
newlover_menu_cx = 65;
newlover_menu_cy_end_offset = 50;
newlover_dragging = false;
comment = "new wife menu drag state";
newwife_menu_toggle = false;
newwife_menu_x = room_width - 260;
newwife_menu_y = room_height - 100;
newwife_dragging = false;
comment = "dialogue menu";
dialogue_menu_toggle = false;
text_scale_l = 1;
text_scale_w = 1;
max_lover_dialogue_width = 200;
max_wife_dialogue_width = 200;
top_dlg_x = 0;
top_dlg_y = 0;
wife_dlg_x = 3;
wife_dlg_y = 0;
dlg_drag_offset_x = 0;
dlg_drag_offset_y = 0;
dlg_color_picker_active = 0;
dlg_picker_value = 0;
dlg_preview_color = 16777215;
dlg_current_color = 16777215;
dlg_color_surface = -1;
dlg_last_picker_value = -1;
global.dialogue_display_index = 0;
global.speaker_type_index = 0;
global.rg_active = false;
global.rg_instance = -1;
global.rg_was_playing = false;
global.rg_locked = false;
global.rg_chosen_pill = "";
global.rg_chosen_idx = -1;
global.rg_pill_prev = false;
global.rg_cry_val = 0;
rg_chance = 0;
comment = "mystery pills";
mystery_pilled_futa = -1;
premature_pill = false;
edge_lover_pill = false;
edge_lover_pill_prev = edge_lover_pill;
edge_lover_threshold = 0;
edge_lover_triggered = false;
edge_lover_pullout_flag = false;
edge_lover_animating = false;
edge_lover_last_max = 0;
premature_pill_prev = premature_pill;
premature_check_timer = 0;
contraceptive_pill = false;
mega_sperm_pill = false;
equine_pill = false;
knotted_pill = false;
extra_thick_pill = false;
diphallia_pill = false;
ovulation_pill = false;
mg_score_pool = 0;
mg_score_total_shots = 1;
mg_impreg_counter = irandom_range(4, 10);
machinegun_toggle = false;
mg_interval_min = 4;
mg_interval_max = 14;
mg_spread = 0.2;
mg_burst_min = 1;
mg_burst_max = 2;
overflow_delay = 0;
overflow_queue = [];
shot_pump_cost_per_particle = 0;
shot_condom_jiggle_per_particle = 0;
mg_condom_jiggle_strength = 0.015;
mg_spread = 0.2;
stamina_pill = false;
leaky_pill = false;
hyper_breeding_pill = false;
quickshot_pill = false;
blockage_pill = false;
saved_ball_size = 1;
giga_pump = false;
reverse_speed_pill = false;
edge_addict_pill = false;
pound_town_pill = false;
greedy_womb_pill = false;
greedy_womb_pill_prev = false;
growth_cascade_pill = false;
growth_cascade_pill_prev = false;
savor_pill = false;
savor_pill_prev = false;
savor_active = false;
savor_timer = -1;
savor_pull_count = 0;
savor_smooth_depth = 0;
savor_rest_min = 30;
savor_rest_max = 120;
savor_pull_min = 40;
savor_pull_max = 90;
savor_lock_depth = -0.2;
savor_pull_target = 0.45;
savor_duration_min = 300;
savor_duration_max = 600;
savor_cycle_timer = 0;
savor_in_pull = false;
savor_pull_count_min = 3;
savor_pull_count_max = 12;
three_pump_champ_pill = false;
three_pump_champ_pill_prev = false;
three_pump_champ_saved_pumps = user_pumps_max;
eggxcelent_pill = false;
eggxcelent_pill_prev = false;
contraceptive_pill_prev = contraceptive_pill;
mega_sperm_pill_prev = mega_sperm_pill;
equine_pill_prev = equine_pill;
knotted_pill_prev = knotted_pill;
extra_thick_pill_prev = extra_thick_pill;
diphallia_pill_prev = diphallia_pill;
ovulation_pill_prev = ovulation_pill;
stamina_pill_prev = stamina_pill;
leaky_pill_prev = leaky_pill;
hyper_breeding_pill_prev = hyper_breeding_pill;
quickshot_pill_prev = quickshot_pill;
blockage_pill_prev = blockage_pill;
reverse_speed_pill_prev = reverse_speed_pill;
edge_addict_pill_prev = edge_addict_pill;
pound_town_pill_prev = pound_town_pill;
saved_sex_progress_max_pound_town = sex_progress_max;
livestream_pill = false;
livestream_pill_prev = false;
livestream_chat = ds_list_create();
livestream_timer = 180;
livestream_viewers = random_range(4, 12);
livestream_new_viewer = 180;
livestream_hype = 1;
stat_livestream_viewers = 0;
stat_total_bunny_money = 0;
livestream_dialogue = 
{
    username_start: ["juicy", "jizzyjr", "NPC", "A-ko", "chavez", "a.love", "fallker", "miska", "milky", "big", "cock", "pussy", "boob", "yummy", "slutty", "cum", "thick", "goth", "hung", "huge", "tiny", "sperm", "dommy", "mrmoneybags", "xXxtremegmrXxX", "fisto", "ben", "J-silverballs"],
    username_end: ["cock", "daddy", "mommy", "lover", "futa", "femboy", "bimbo", "slut", "succubus", "kitty", "bunny", "machine", "tits", "booty", "cow", "pegged", "paypig", "tired", "dover"],
    message_normal: ["hello", "hey guys", "jerking off rn", "stroking it", "<3", "woah :O", "haaiii", ":3", "yummers", "brb", "i love boobs", "i'm gay", "subscribed"],
    message_sex: ["faster!!", "i wish that was me...", "such a great view", "move the camera closer", "i wish my cock was that big", "so deep...", "plap plap plap"],
    message_sex_halfway: ["orgasm incoming!!", "almost there"],
    message_orgasm: ["god yes", "oughh", "cumming!!", "yessssss", "keep pumping!!", "more!!", "so much cum", "get pregnant!!", "POG", "LESS GOOOO!!!", "YEAHHH"],
    message_waiting: ["drooling", "such a huge cock!!", "stop teasing us and put it in!!", "guys how do i install 1.4 in modroom?", "i wanna suck it so bad", "8======D", "guyzzz where male?!!?", "Fallker keeps breaking shiet", "staph breaking DeepRoom Fallker!!1!1"],
    message_slime_normal: ["hello", "hey guys", "jerking off rn", "stroking it", "<3", "woah :O", "haaiii", ":3", "yummers", "brb", "i love boobs", "i'm gay", "subscribed"],
    message_slime_sex: ["faster!!", "i wish that was me...", "such a great view", "move the camera closer", "i wish my cock was that big", "so deep...", "plap plap plap"],
    message_slime_sex_halfway: ["orgasm incoming!!", "almost there"],
    message_slime_orgasm: ["god yes", "oughh", "cumming!!", "yessssss", "keep pumping!!", "more!!", "so much cum", "get pregnant!!", "POG", "LESS GOOOO!!!", "YEAHHH"],
    message_devil_normal: ["hello", "hey guys", "jerking off rn", "stroking it", "<3", "woah :O", "haaiii", ":3", "yummers", "brb", "i love boobs", "i'm gay", "subscribed"],
    message_devil_sex: ["faster!!", "i wish that was me...", "such a great view", "move the camera closer", "i wish my cock was that big", "so deep...", "plap plap plap"],
    message_devil_sex_halfway: ["orgasm incoming!!", "almost there"],
    message_devil_orgasm: ["god yes", "oughh", "cumming!!", "yessssss", "keep pumping!!", "more!!", "so much cum", "get pregnant!!", "POG", "LESS GOOOO!!!", "YEAHHH"],
    message_furry_normal: ["hello", "hey guys", "jerking off rn", "stroking it", "<3", "woah :O", "haaiii", ":3", "yummers", "brb", "i love boobs", "i'm gay", "subscribed"],
    message_furry_sex: ["faster!!", "i wish that was me...", "such a great view", "move the camera closer", "i wish my cock was that big", "so deep...", "plap plap plap"],
    message_furry_sex_halfway: ["orgasm incoming!!", "almost there"],
    message_furry_orgasm: ["god yes", "oughh", "cumming!!", "yessssss", "keep pumping!!", "more!!", "so much cum", "get pregnant!!", "POG", "LESS GOOOO!!!", "YEAHHH"],
    message_android_normal: ["hello", "hey guys", "jerking off rn", "stroking it", "<3", "woah :O", "haaiii", ":3", "yummers", "brb", "i love boobs", "i'm gay", "subscribed"],
    message_android_sex: ["faster!!", "i wish that was me...", "such a great view", "move the camera closer", "i wish my cock was that big", "so deep...", "plap plap plap"],
    message_android_sex_halfway: ["orgasm incoming!!", "almost there"],
    message_android_orgasm: ["god yes", "oughh", "cumming!!", "yessssss", "keep pumping!!", "more!!", "so much cum", "get pregnant!!", "POG", "LESS GOOOO!!!", "YEAHHH"]
};
var _ls_json_path = tc_wd + "/custom_stuff/dialogue/livestream.json"; // Deeproom 4.0.3 location
if (!file_exists(_ls_json_path)) _ls_json_path = file_exists("custom_stuff/dialogue/livestream.json") ? "custom_stuff/dialogue/livestream.json" : (tc_wd + "/dialogue/livestream.json");
if (file_exists(_ls_json_path))
{
    var _ls_file = file_text_open_read(_ls_json_path);
    var _ls_json_string = "";
    while (!file_text_eof(_ls_file))
    {
        _ls_json_string += file_text_read_string(_ls_file);
        file_text_readln(_ls_file);
    }
    file_text_close(_ls_file);
    try
    {
        livestream_dialogue = json_parse(_ls_json_string);
    }
    catch (_err)
    {
        show_debug_message("Livestream JSON parse error bypassed safely");
    }
}
comment = "texture pack variables";
texture_pack_loaded = false;
texture_pack_sprites = ds_list_create();
texture_pack_number = 0;
chosen_texture_pack = "default";
comment = "scroller variables";
bg_menu = 
{
    scroll: 0,
    scroll_lerp: 0
};
pill_menu = 
{
    scroll: 0,
    scroll_lerp: 0
};
futa_selector_menu = 
{
    scroll: 0,
    scroll_lerp: 0
};
futa_selector_saved_scroll = 0;
wife_selector_saved_scroll = 0;
futa_selector_saved_scroll = 0;
wife_selector_saved_scroll = 0;
selector_search_string = "";
selector_search_focused = false;
futa_selector_open = false;
futa_selector_drag = false;
futa_selector_arrow_left = false;
futa_selector_arrow_right = false;
futa_selector_arrow_speed = 13;
futa_selector_open_timer = 0;
futa_selector_close_timer = 0;
futa_selector_portraits = ds_list_create();
futa_selector_has_deepthroat = ds_list_create();
futa_selector_has_alts = ds_list_create();
futa_selector_names = ds_list_create();
wife_selector_portraits = ds_list_create();
wife_selector_has_cowgirl = ds_list_create();
wife_selector_names = ds_list_create();
selector_mode = 0;
comment = "background things";
max_default_bg = 6;
custom_bg_size = 0;
total_background_amount = 0;
for (var i = 0; i < 12; i++)
{
    sperm[i] = 0;
    sperm_speed[i] = 0;
}
alarm[0] = 120 + irandom(120);
futa_icon_color = 12976127;
wife_icon_color = 13408767;
top_skin = 16777215;
top_hair = 16776960;
top_stockings = 8421504;
bottom_skin = 16777215;
bottom_hair = 16776960;
comment = "old version has a different value: 4210752. seems arbitrary";
bottom_stockings = 8421504;
face_x = 0;
face_y = 0;
cum_color = 16777215;
prev_cum_color = -1;
cum_fill_color = 16777215;
top_ass_size = 1;
top_penis_width = 1;
top_penis_length = 1;
top_boob_size = 1;
rare_guarantee = 0;
top_sprite = sFutaMatingPress;
bottom_sprite = sWifeMatingPress;
top_deepthroat = sFutaDeepthroat;
bottom_deepthroat = sWifeDeepthroat;
penis_sprite = sFutaMatingPress;
penis_color = 16777215;
penis_head_color = 16777215;
hair_sprite = choose(sFutaMatingPress, sFutaMatingPress2, sFutaMatingPress3, sFutaMatingPress4, sFutaMatingPressAndroid, sFutaMatingPressDevil, sFutaMatingPressClown);
wife_hair_sprite = choose(sWifeNormalCowgirl1, sWifeNormalCowgirl2, sWifeNormalCowgirl3, sWifeNormalCowgirl4, sWifeNormalCowgirlAndroid, sWifeNormalCowgirlDevil);
portrait_number = 0;
portrait_x = 48;
portrait_y = room_height - (59 + ui_y_offset);
top_breath = -1;
bottom_breath = -1;
insert_thrust = 0;
wife_shake_x = 0;
wife_shake_y = 0;
mm_press4 = false;
mm_press5 = false;
holding_object = false;
penis_grab = false;
comment = "hovers";
hover_portrait = -1;
kiss_box = -1;
comment = "custom lover stuff";
custom_sprite_loaded = false;
custom_portrait = -1;
custom_mating_press = -1;
custom_cowgirl = -1;
custom_deepthroat = -1;
custom_futa_deepthroat = -1;
custom_deepthroat_alt = -1;
comment = "custom ball clench sprites";
custom_bc_mating_press = -1;
custom_bc_cowgirl = -1;
custom_bc_crest = -1;
custom_bc_crest_mp = -1;
custom_bc_crest_cg = -1;
custom_bc_crest_dt = -1;
custom_bc_loaded = false;
custom_bc_mp_off_y = 0;
custom_bc_cg_off_y = 0;
custom_bc_rc_off_y = 0;
custom_bc_dt_off_y = 0;
custom_condom_broken = -1;
legacy_custom_xray_broken = -1;
custom_condom = -1;
custom_xray = -1;
legacy_bc_mating_press = -1;
legacy_bc_cowgirl = -1;
legacy_bc_deepthroat = -1;
legacy_bc_crest = -1;
legacy_bc_loaded = false;
is_legacy_custom = false;
legacy_custom_portrait = -1;
legacy_custom_mating_press = -1;
legacy_custom_cowgirl = -1;
legacy_custom_condom = -1;
legacy_custom_xray = -1;
custom_portrait_scale = 1;
custom_mating_press_scale = 1;
custom_futa_dt_y_offset = 0;
custom_cowgirl_scale = 1;
custom_condom_scale = 1;
custom_xray_scale = 1;
custom_xray_offset_y = 0;
xray_length_nudge = 70;
custom_kiss_y_offset = 0;
custom_kiss_x_offset = 0;
custom_boob_y_offset = 0;
custom_boob_x_offset = 0;
custom_headpat_y_offset = 0;
custom_headpat_x_offset = 0;
futa_saved_kiss_x_offset = 0;
futa_saved_kiss_y_offset = 0;
futa_saved_boob_x_offset = 0;
futa_saved_boob_y_offset = 0;
futa_saved_headpat_x_offset = 0;
futa_saved_headpat_y_offset = 0;
wife_saved_kiss_x_offset = 0;
wife_saved_kiss_y_offset = 0;
wife_saved_boob_x_offset = 0;
wife_saved_boob_y_offset = 0;
wife_saved_headpat_x_offset = 0;
wife_saved_headpat_y_offset = 0;
offset_panel_open = false;
offset_panel_mode = "";
offset_click_guard = false;
offset_click_guard_timer = 0;
offset_panel_x_saved = 0;
offset_panel_y_saved = 0;
wife_offset_panel_open = false;
wife_offset_panel_mode = "";
wife_offset_click_guard = false;
wife_offset_click_guard_timer = 0;
wife_offset_panel_x_saved = 0;
wife_offset_panel_y_saved = 0;
custom_cum_y_offset_dt = 0;
custom_cum_y_offset_cg = 0;
custom_cum_y_offset_mp = 0;
condom_offset_deepthroat = 0;
custom_condom_offset_deepthroat = 0;
last_condom_break_snd = -1;
insert_snd_last = 0;
pullout_snd_last = 0;
custom_insert_list = ds_list_create();
custom_pullout_list = ds_list_create();
custom_condom_break_list = ds_list_create();
headpat = 0;
headpat_delay = 0;
headpat_press = false;
skip_disclaimer = false;
debug_boxes_top_ass_left = 0;
debug_boxes_top_ass_top = 0;
debug_boxes_top_ass_right = 0;
debug_boxes_top_ass_bottom = 0;
debug_boxes_bottom_ass_left = 0;
debug_boxes_bottom_ass_top = 0;
debug_boxes_bottom_ass_right = 0;
debug_boxes_bottom_ass_bottom = 0;
debug_boxes_grab_left = 0;
debug_boxes_grab_top = 0;
debug_boxes_grab_right = 0;
debug_boxes_grab_bottom = 0;
custom_cum_y_offset = 0;
custom_max_loads = 5;
custom_top_boob_size = 1;
custom_top_ass_size = 1;
custom_top_penis_length = 1;
custom_top_penis_width = 1;
custom_ball_size = 1;
custom_virility_modifier = 1;
custom_cum_volume_modifier = 1;
custom_stroke_depth = 1;
custom_stroke_speed = 1;
custom_pump_delay = 90;
custom_equine_pill = false;
custom_knotted_pill = false;
custom_extra_thick_pill = false;
custom_diphallia_pill = false;
custom_stamina_pill = false;
custom_leaky_pill = false;
custom_mega_sperm_pill = false;
custom_hyper_breeding_pill = false;
custom_blockage_pill = false;
custom_quickshot_pill = false;
custom_reverse_speed_pill = false;
custom_edge_addict_pill = false;
custom_pound_town_pill = false;
custom_greedy_womb_pill = false;
custom_premature_pill = false;
custom_edge_lover_pill = false;
custom_growth_cascade_pill = false;
custom_livestream_pill = false;
custom_three_pump_champ_pill = false;
custom_penis_type_index = 0;
custom_condom_color = -1;
custom_condom_color_set = false;
custom_condom_offset_mpress = 0;
custom_condom_offset_cowgirls = 0;
condom_offset_mpress = 0;
condom_offset_cowgirls = 0;
comment = "custom wife stuff";
custom_wife_sprite_loaded = false;
custom_wife_has_portrait = false;
custom_wife_portrait = -1;
custom_wife_portrait_scale = 1;
custom_wife_cowgirl = -1;
custom_wife_reverse_cowgirl = -1;
custom_wife_mating_press = -1;
custom_wife_xray = -1;
custom_wife_deepthroat = -1;
custom_wife_scale = 1;
legacy_custom_wife_toggle = false;
legacy_custom_wife_mating_press = -1;
legacy_custom_wife_reverse_cowgirl = -1;
legacy_custom_wife_deepthroat = -1;
legacy_custom_wife_portrait = -1;
legacy_custom_wife_xray = -1;
wife_xray_fixed_offset = false;
custom_bottom_boob_size = 1;
custom_bottom_ass_size = 1;
custom_partner_male = false;
custom_ovulation_pill = false;
custom_eggxcelent_pill = false;
custom_contraceptive_pill = false;
custom_wife_size_response = 1;
custom_wife_intensity_response = 1;
custom_wife_cum_response = 1;
custom_wife_reproductive_response = 1;
custom_wife_affection_response = 1;
custom_wife_pain_response = 1;
custom_wives_folder = ds_list_create();
custom_futas_folder = ds_list_create();
var _cs_bases = ["custom_sounds/futa", "custom_sounds", "custom_stuff/custom_sounds/futa", "custom_stuff/custom_sounds"];
for (var _bi = 0; _bi < array_length(_cs_bases); _bi++)
{
    var _base = _cs_bases[_bi];
    var _cs_file = tc_ff_first(_base + "/*", 16);
    while (_cs_file != "")
    {
        if (_cs_file != "." && _cs_file != ".." && _cs_file != "futa" && _cs_file != "wife (placeholder)" && _cs_file != "sfx (placeholder)")
        {
            var _cs_full = _base + "/" + _cs_file;
            if (file_exists(_cs_full + "/moan_slow/_manifest.txt") || file_exists(_cs_full + "/moan_fast/_manifest.txt") || file_exists(_cs_full + "/_manifest.txt") || tc_dir_exists(_cs_full))
            {
                if (ds_list_find_index(cs_futa_pack_names, _cs_file) == -1)
                {
                    ds_list_add(cs_futa_packs, _cs_full);
                    ds_list_add(cs_futa_pack_names, _cs_file);
                }
            }
        }
        _cs_file = tc_ff_next();
    }
    tc_ff_close();
}
cs_futa_packs_loaded = ds_list_size(cs_futa_packs) > 0;
var _wd = working_directory;
if (string_char_at(_wd, string_length(_wd)) == "/")
{
    _wd = string_copy(_wd, 1, string_length(_wd) - 1);
}
if (os_type == os_android || os_type == os_ios || _wd == "/")
{
    _wd = "";
}
var _is_mobile = os_type == os_android || os_type == os_ios;
var _futa_names = [];
var _mf_p = "custom_futas/_manifest.txt";
var _f_buf = buffer_load(_mf_p);
if (_f_buf == -1 && _wd != "") _f_buf = buffer_load(_wd + "/custom_futas/_manifest.txt");
if (_f_buf == -1) _f_buf = buffer_load("custom_stuff/custom_futas/_manifest.txt");
if (_f_buf != -1)
{
    var _f_str = string_replace_all(buffer_read(_f_buf, buffer_string), "\r", "");
    buffer_delete(_f_buf);
    var _cur_line = "";
    var _len = string_length(_f_str);
    for (var _ci = 1; _ci <= _len; _ci++)
    {
        var _ch = string_char_at(_f_str, _ci);
        if (_ch == "\n")
        {
            if (_cur_line != "" && _cur_line != "_manifest.txt")
            {
                array_push(_futa_names, _cur_line);
                _cur_line = "";
            }
        }
        else
        {
            _cur_line += _ch;
        }
    }
    if (_cur_line != "" && _cur_line != "_manifest.txt")
    {
        array_push(_futa_names, _cur_line);
    }
}
if (array_length(_futa_names) == 0)
{
    var _mf_futa = file_text_open_read(_mf_p);
    if (_mf_futa == -1 && _wd != "") _mf_futa = file_text_open_read(_wd + "/custom_futas/_manifest.txt");
    if (_mf_futa == -1) _mf_futa = file_text_open_read("custom_stuff/custom_futas/_manifest.txt");
    if (_mf_futa != -1)
    {
        while (!file_text_eof(_mf_futa))
        {
            var _mf_line = string_replace_all(string_replace_all(file_text_readln(_mf_futa), "\r", ""), "\n", "");
            if (_mf_line != "" && _mf_line != "_manifest.txt")
            {
                array_push(_futa_names, _mf_line);
            }
        }
        file_text_close(_mf_futa);
    }
}
var _futa_manifest = array_length(_futa_names) > 0;
var _f_root = file_exists("custom_stuff/custom_futas/_manifest.txt") ? "custom_stuff/custom_futas/" : "custom_futas/";
for (var _fi = 0; _fi < array_length(_futa_names); _fi++)
{
    var _file = _futa_names[_fi];
    var _full_path = _is_mobile ? (_f_root + _file) : (_wd + "/" + _f_root + _file);
    if (_is_mobile && _futa_manifest)
    {
        custom_sprite_loaded = true;
        tutorial = false;
        ds_list_add(custom_futas_folder, _full_path);
        pm_registry_add(_full_path);
        ds_list_add(futa_selector_names, _file);
        ds_list_add(futa_selector_has_deepthroat, true);
        ds_list_add(futa_selector_has_alts, false);
        ds_list_add(futa_selector_portraits, -1);
    }
    else if (_futa_manifest || tc_dir_exists(_full_path))
    {
        check_struct = check_custom_futa(_full_path);
        if (check_struct.custom_portrait != -1 && check_struct.custom_mating_press != -1 && check_struct.custom_cowgirls != -1 && check_struct.custom_xray != -1)
        {
            custom_sprite_loaded = true;
            tutorial = false;
            show_debug_message("SUCCESS: Loaded " + _file);
            ds_list_add(custom_futas_folder, _full_path);
            pm_registry_add(_full_path);
            ds_list_add(futa_selector_names, _file);
            var _has_deep = file_exists(_full_path + "/custom_deepthroat.png");
            var _has_alts = file_exists(_full_path + "/custom_futa_cowgirl_alt_1.png") || file_exists(_full_path + "/custom_futa_mating_press_alt_1.png");
            ds_list_add(futa_selector_has_deepthroat, _has_deep);
            ds_list_add(futa_selector_has_alts, _has_alts);
            var _preview_spr = -1;
            if (!_is_mobile)
            {
                _preview_spr = func_futa_selector_portrait(_full_path);
            }
            ds_list_add(futa_selector_portraits, _preview_spr);
        }
    }
}
_wd = working_directory;
if (string_char_at(_wd, string_length(_wd)) == "/")
{
    _wd = string_copy(_wd, 1, string_length(_wd) - 1);
}
var _wife_names = [];
var _mf_pw = "custom_wives/_manifest.txt";
var _w_buf = buffer_load(_mf_pw);
if (_w_buf == -1 && _wd != "") _w_buf = buffer_load(_wd + "/custom_wives/_manifest.txt");
if (_w_buf == -1) _w_buf = buffer_load("custom_stuff/custom_wives/_manifest.txt");
if (_w_buf != -1)
{
    var _w_str = string_replace_all(buffer_read(_w_buf, buffer_string), "\r", "");
    buffer_delete(_w_buf);
    var _cur_wline = "";
    var _wlen = string_length(_w_str);
    for (var _wi = 1; _wi <= _wlen; _wi++)
    {
        var _wch = string_char_at(_w_str, _wi);
        if (_wch == "\n")
        {
            if (_cur_wline != "" && _cur_wline != "_manifest.txt")
            {
                array_push(_wife_names, _cur_wline);
                _cur_wline = "";
            }
        }
        else
        {
            _cur_wline += _wch;
        }
    }
    if (_cur_wline != "" && _cur_wline != "_manifest.txt")
    {
        array_push(_wife_names, _cur_wline);
    }
}
if (array_length(_wife_names) == 0)
{
    var _mf_wife = file_text_open_read(_mf_pw);
    if (_mf_wife == -1 && _wd != "") _mf_wife = file_text_open_read(_wd + "/custom_wives/_manifest.txt");
    if (_mf_wife == -1) _mf_wife = file_text_open_read("custom_stuff/custom_wives/_manifest.txt");
    if (_mf_wife != -1)
    {
        while (!file_text_eof(_mf_wife))
        {
            var _mf_line2 = string_replace_all(string_replace_all(file_text_readln(_mf_wife), "\r", ""), "\n", "");
            if (_mf_line2 != "" && _mf_line2 != "_manifest.txt")
            {
                array_push(_wife_names, _mf_line2);
            }
        }
        file_text_close(_mf_wife);
    }
}
var _wife_manifest = array_length(_wife_names) > 0;
var _w_root = file_exists("custom_stuff/custom_wives/_manifest.txt") ? "custom_stuff/custom_wives/" : "custom_wives/";
for (var _wi = 0; _wi < array_length(_wife_names); _wi++)
{
    var _file = _wife_names[_wi];
    var _full_path = _is_mobile ? (_w_root + _file) : (_wd + "/" + _w_root + _file);
    if (_is_mobile && _wife_manifest)
    {
        custom_wife_sprite_loaded = true;
        ds_list_add(custom_wives_folder, _full_path);
        pm_registry_add(_full_path);
        ds_list_add(wife_selector_names, _file);
        ds_list_add(wife_selector_has_cowgirl, true);
        ds_list_add(wife_selector_portraits, -1);
    }
    else if (_wife_manifest || tc_dir_exists(_wd + "/custom_wives/" + _file))
    {
        _full_path = _is_mobile ? ("custom_wives/" + _file) : (_wd + "/custom_wives/" + _file);
        var _is_legacy_spouse = file_exists(_full_path + "/custom_data.spouse");
        if (_is_legacy_spouse)
        {
            if (file_exists(_full_path + "/custom_mating_press.png") || file_exists(_full_path + "/custom_reverse_cowgirl.png"))
            {
                custom_wife_sprite_loaded = true;
                show_debug_message("loaded 1.4 legacy spouse: " + _file);
                ds_list_add(custom_wives_folder, _full_path);
                pm_registry_add(_full_path);
                ds_list_add(wife_selector_names, _file);
                var _legacy_has_deep = file_exists(_full_path + "/custom_deepthroat.png");
                ds_list_add(wife_selector_has_cowgirl, _legacy_has_deep);
                var _w_spr = _is_mobile ? -1 : func_wife_selector_portrait(_full_path);
                ds_list_add(wife_selector_portraits, _w_spr);
            }
        }
        else
        {
            check_struct = check_custom_wife(_full_path);
            if (check_struct.custom_wife_cowgirl != -1 && check_struct.custom_wife_reverse_cowgirl != -1 && check_struct.custom_wife_mating_press != -1)
            {
                custom_wife_has_portrait = check_struct.custom_wife_portrait;
                custom_wife_sprite_loaded = true;
                show_debug_message("loaded custom wife");
                ds_list_add(custom_wives_folder, _full_path);
                pm_registry_add(_full_path);
                ds_list_add(wife_selector_names, _file);
                var _w_has_cowgirl = file_exists(_full_path + "/custom_wife_cowgirl_0.png");
                ds_list_add(wife_selector_has_cowgirl, _w_has_cowgirl);
                var _w_spr = _is_mobile ? -1 : func_wife_selector_portrait(_full_path);
                ds_list_add(wife_selector_portraits, _w_spr);
            }
        }
    }
}
// Ingestion of v1.5 custom/ directory packs into Lover and Wife selection
var _custom_names = [];
var _mf_pcust = "custom/_manifest.txt";
var _mf_cust = file_text_open_read(_mf_pcust);
if (_mf_cust == -1 && _wd != "")
{
    _mf_cust = file_text_open_read(_wd + "/custom/_manifest.txt");
}
if (_mf_cust != -1)
{
    while (!file_text_eof(_mf_cust))
    {
        var _c_line = string_replace_all(string_replace_all(file_text_readln(_mf_cust), "\r", ""), "\n", "");
        if (_c_line != "" && _c_line != "_manifest.txt")
        {
            array_push(_custom_names, _c_line);
        }
    }
    file_text_close(_mf_cust);
}
if (array_length(_custom_names) == 0 && tc_dir_exists(_wd + "/custom"))
{
    var _c_first = tc_ff_first(_wd + "/custom/*", 16);
    while (_c_first != "")
    {
        if (_c_first != "." && _c_first != ".." && _c_first != "_manifest.txt")
        {
            array_push(_custom_names, _c_first);
        }
        _c_first = tc_ff_next();
    }
    tc_ff_close();
}

for (var _c_i = 0; _c_i < array_length(_custom_names); _c_i++)
{
    var _c_name = _custom_names[_c_i];
    var _c_full = _is_mobile ? ("custom/" + _c_name) : (_wd + "/custom/" + _c_name);
    
    if (file_exists(_c_full + "/custom_data.futa"))
    {
        if (ds_list_find_index(custom_futas_folder, _c_full) == -1)
        {
            custom_sprite_loaded = true;
            tutorial = false;
            ds_list_add(custom_futas_folder, _c_full);
            ds_list_add(futa_selector_names, _c_name);
            ds_list_add(futa_selector_has_deepthroat, file_exists(_c_full + "/custom_deepthroat.png"));
            ds_list_add(futa_selector_has_alts, false);
            ds_list_add(futa_selector_portraits, -1);
        }
    }
    else if (file_exists(_c_full + "/custom_data.spouse"))
    {
        if (ds_list_find_index(custom_wives_folder, _c_full) == -1)
        {
            custom_wife_sprite_loaded = true;
            ds_list_add(custom_wives_folder, _c_full);
            ds_list_add(wife_selector_names, _c_name);
            ds_list_add(wife_selector_has_cowgirl, file_exists(_c_full + "/custom_deepthroat.png"));
            ds_list_add(wife_selector_portraits, -1);
        }
    }
}

pm_status = "";
pm_url = "";
pm_pick = 0;
pm_inbox_tick = 0;
pm_pick_list = [];
pm_pick_paths = [];
pm_pick_kinds = [];
pm_rm_path = "";
pm_rm_name = "";
pm_rm_kind = 0;
pm_seq = 0;
pm_bt_n = 0;
pm_bt_a = 0;
pm_bt_bg = 0;
pm_bt_dlg = 0;
pm_bt_tex = 0;
pm_bt_voice = 0;
pm_bt_dups = 0;
if (variable_global_exists("pm_note"))
{
    pm_status = string(global.pm_note);
    global.pm_note = "";
}
pm_pick_page = 0;
pm_voice_sel = "";
pm_voice_name = "";
pm_dialog = -1;
pm_http = -1;
// Phone-added characters come back after a restart: only the folders recorded in phone_mods_registry.txt are
// loaded (no folder scan, which hung startup in 1.1). REMOVE MOD drops a mod from the registry first.
if (os_type == os_android || os_type == os_ios)
{
    var _pm_save = game_save_id;
    if (string_char_at(_pm_save, string_length(_pm_save)) == "/")
    {
        _pm_save = string_copy(_pm_save, 1, string_length(_pm_save) - 1);
    }
    var _pm_root = _pm_save + "/phone_mods";
    if (!tc_dir_exists(_pm_root))
    {
        directory_create(_pm_root);
    }
    var _pm_wd = working_directory;
    if (string_char_at(_pm_wd, string_length(_pm_wd)) == "/")
    {
        _pm_wd = string_copy(_pm_wd, 1, string_length(_pm_wd) - 1);
    }
    if (false && file_exists(_pm_wd + "/phone_mods_seed.zip") && !file_exists(_pm_save + "/phone_mods_seed.done"))  // seed import stays off
    {
        var _pm_buf = buffer_load(_pm_wd + "/phone_mods_seed.zip");
        if (_pm_buf >= 0)
        {
            buffer_save(_pm_buf, _pm_save + "/phone_mods_seed_tmp.zip");
            buffer_delete(_pm_buf);
            zip_unzip(_pm_save + "/phone_mods_seed_tmp.zip", _pm_root + "/seed/");
            file_delete(_pm_save + "/phone_mods_seed_tmp.zip");
            var _pm_bg = 0;
            var _pm_dlg = 0;
            var _pm_tex = 0;
            var _pm_voice = 0;
            var _pm_rchars = 0;
            var _pm_tsrc = [];
            var _pm_tdst = [];
            var _pm_rq = [_pm_root + "/seed"];
            var _pm_rn = ["starter"];
            var _pm_rdep = [0];
            var _pm_ri = 0;
            while (_pm_ri < array_length(_pm_rq))
            {
                var _pm_rd = _pm_rq[_pm_ri];
                var _pm_rname = _pm_rn[_pm_ri];
                var _pm_rdepth = _pm_rdep[_pm_ri];
                _pm_ri++;
                if (file_exists(_pm_rd + "/custom_data.futa") || file_exists(_pm_rd + "/custom_data.wife") || file_exists(_pm_rd + "/custom_data.spouse"))
                {
                    _pm_rchars++;
                }
                else if (file_exists(_pm_rd + "/custom_data.bedroom"))
                {
                    var _pm_csrc = [_pm_rd];
                    var _pm_cdst = [_pm_save + "/custom_bedrooms/" + _pm_rname];
                    pm_registry_add(_pm_cdst[0]);
                    var _pm_ci = 0;
                    while (_pm_ci < array_length(_pm_csrc))
                    {
                        var _pm_cs = _pm_csrc[_pm_ci];
                        var _pm_cd = _pm_cdst[_pm_ci];
                        _pm_ci++;
                        if (!tc_dir_exists(_pm_cd))
                        {
                            directory_create(_pm_cd);
                        }
                        var _pm_cn = [];
                        var _pm_cf = tc_ff_first(_pm_cs + "/*", 16);
                        while (_pm_cf != "")
                        {
                            if (_pm_cf != "." && _pm_cf != "..")
                            {
                                array_push(_pm_cn, _pm_cf);
                            }
                            _pm_cf = tc_ff_next();
                        }
                        tc_ff_close();
                        for (var _pm_cx = 0; _pm_cx < array_length(_pm_cn); _pm_cx++)
                        {
                            if (tc_dir_exists(_pm_cs + "/" + _pm_cn[_pm_cx]))
                            {
                                array_push(_pm_csrc, _pm_cs + "/" + _pm_cn[_pm_cx]);
                                array_push(_pm_cdst, _pm_cd + "/" + _pm_cn[_pm_cx]);
                            }
                            else
                            {
                                file_copy(_pm_cs + "/" + _pm_cn[_pm_cx], _pm_cd + "/" + _pm_cn[_pm_cx]);
                            }
                        }
                    }
                    _pm_bg++;
                }
                else
                {
                    var _pm_re = [];
                    var _pm_rf = tc_ff_first(_pm_rd + "/*", 16);
                    while (_pm_rf != "")
                    {
                        if (_pm_rf != "." && _pm_rf != "..")
                        {
                            array_push(_pm_re, _pm_rf);
                        }
                        _pm_rf = tc_ff_next();
                    }
                    tc_ff_close();
                    var _pm_png = 0;
                    var _pm_subs = [];
                    for (var _pm_x = 0; _pm_x < array_length(_pm_re); _pm_x++)
                    {
                        var _pm_en = _pm_re[_pm_x];
                        var _pm_el = string_lower(_pm_en);
                        if (tc_dir_exists(_pm_rd + "/" + _pm_en))
                        {
                            array_push(_pm_subs, _pm_en);
                        }
                        else if (string_copy(_pm_el, string_length(_pm_el) - 4, 5) == ".json")
                        {
                            if (!tc_dir_exists(_pm_save + "/dialogue_packs"))
                            {
                                directory_create(_pm_save + "/dialogue_packs");
                            }
                            file_copy(_pm_rd + "/" + _pm_en, _pm_save + "/dialogue_packs/" + _pm_en);
                            pm_registry_add(_pm_save + "/dialogue_packs/" + _pm_en);
                            _pm_dlg++;
                        }
                        else if (string_copy(_pm_el, string_length(_pm_el) - 3, 4) == ".png")
                        {
                            _pm_png++;
                        }
                    }
                    var _pm_isvoice = false;
                    for (var _pm_z = 0; _pm_z < array_length(_pm_subs); _pm_z++)
                    {
                        if (string_lower(_pm_subs[_pm_z]) == "moan_fast" || string_lower(_pm_subs[_pm_z]) == "moan_slow")
                        {
                            _pm_isvoice = true;
                        }
                    }
                    if (_pm_isvoice)
                    {
                        if (!tc_dir_exists(_pm_save + "/phone_voices"))
                        {
                            directory_create(_pm_save + "/phone_voices");
                        }
                        var _pm_csrc = [_pm_rd];
                        var _pm_cdst = [_pm_save + "/phone_voices/" + _pm_rname];
                        pm_registry_add(_pm_cdst[0]);
                        var _pm_ci = 0;
                        while (_pm_ci < array_length(_pm_csrc))
                        {
                            var _pm_cs = _pm_csrc[_pm_ci];
                            var _pm_cd = _pm_cdst[_pm_ci];
                            _pm_ci++;
                            if (!tc_dir_exists(_pm_cd))
                            {
                                directory_create(_pm_cd);
                            }
                            var _pm_cn = [];
                            var _pm_cf = tc_ff_first(_pm_cs + "/*", 16);
                            while (_pm_cf != "")
                            {
                                if (_pm_cf != "." && _pm_cf != "..")
                                {
                                    array_push(_pm_cn, _pm_cf);
                                }
                                _pm_cf = tc_ff_next();
                            }
                            tc_ff_close();
                            for (var _pm_cx = 0; _pm_cx < array_length(_pm_cn); _pm_cx++)
                            {
                                if (tc_dir_exists(_pm_cs + "/" + _pm_cn[_pm_cx]))
                                {
                                    array_push(_pm_csrc, _pm_cs + "/" + _pm_cn[_pm_cx]);
                                    array_push(_pm_cdst, _pm_cd + "/" + _pm_cn[_pm_cx]);
                                }
                                else
                                {
                                    file_copy(_pm_cs + "/" + _pm_cn[_pm_cx], _pm_cd + "/" + _pm_cn[_pm_cx]);
                                }
                            }
                        }
                        _pm_voice++;
                    }
                    else if (_pm_png >= 3)
                    {
                        array_push(_pm_tsrc, _pm_rd);
                        array_push(_pm_tdst, _pm_save + "/texture_packs/" + _pm_rname);
                    }
                    else if (_pm_rdepth < 4)
                    {
                        for (var _pm_y = 0; _pm_y < array_length(_pm_subs); _pm_y++)
                        {
                            array_push(_pm_rq, _pm_rd + "/" + _pm_subs[_pm_y]);
                            array_push(_pm_rn, _pm_subs[_pm_y]);
                            array_push(_pm_rdep, _pm_rdepth + 1);
                        }
                    }
                }
            }
            if (_pm_rchars == 0)
            {
                for (var _pm_t = 0; _pm_t < array_length(_pm_tsrc); _pm_t++)
                {
                    var _pm_csrc = [_pm_tsrc[_pm_t]];
                    var _pm_cdst = [_pm_tdst[_pm_t]];
                    pm_registry_add(_pm_cdst[0]);
                    var _pm_ci = 0;
                    while (_pm_ci < array_length(_pm_csrc))
                    {
                        var _pm_cs = _pm_csrc[_pm_ci];
                        var _pm_cd = _pm_cdst[_pm_ci];
                        _pm_ci++;
                        if (!tc_dir_exists(_pm_cd))
                        {
                            directory_create(_pm_cd);
                        }
                        var _pm_cn = [];
                        var _pm_cf = tc_ff_first(_pm_cs + "/*", 16);
                        while (_pm_cf != "")
                        {
                            if (_pm_cf != "." && _pm_cf != "..")
                            {
                                array_push(_pm_cn, _pm_cf);
                            }
                            _pm_cf = tc_ff_next();
                        }
                        tc_ff_close();
                        for (var _pm_cx = 0; _pm_cx < array_length(_pm_cn); _pm_cx++)
                        {
                            if (tc_dir_exists(_pm_cs + "/" + _pm_cn[_pm_cx]))
                            {
                                array_push(_pm_csrc, _pm_cs + "/" + _pm_cn[_pm_cx]);
                                array_push(_pm_cdst, _pm_cd + "/" + _pm_cn[_pm_cx]);
                            }
                            else
                            {
                                file_copy(_pm_cs + "/" + _pm_cn[_pm_cx], _pm_cd + "/" + _pm_cn[_pm_cx]);
                            }
                        }
                    }
                    _pm_tex++;
                }
            }
        }
        var _pm_done = file_text_open_write(_pm_save + "/phone_mods_seed.done");
        file_text_write_string(_pm_done, "1");
        file_text_close(_pm_done);
    }
    var _pm_added = 0;
    var _pm_queue = [];
    var _pm_names = [];
    var _pm_depths = [];
    var _pm_reg = pm_registry_read();
    for (var _pm_rg = 0; _pm_rg < array_length(_pm_reg); _pm_rg++)
    {
        if (string_pos("/phone_mods/", _pm_reg[_pm_rg]) > 0)
        {
            array_push(_pm_queue, _pm_reg[_pm_rg]);
            array_push(_pm_names, pm_registry_base(_pm_reg[_pm_rg]));
            array_push(_pm_depths, 99);
        }
    }
    var _pm_qi = 0;
    while (_pm_qi < array_length(_pm_queue))
    {
        var _pm_dir = _pm_queue[_pm_qi];
        var _pm_name = _pm_names[_pm_qi];
        var _pm_depth = _pm_depths[_pm_qi];
        _pm_qi++;
        if (ds_list_find_index(custom_futas_folder, _pm_dir) >= 0 || ds_list_find_index(custom_wives_folder, _pm_dir) >= 0)
        {
            continue;
        }
        if (file_exists(_pm_dir + "/custom_data.futa") || file_exists(_pm_dir + "/custom_data.wife") || file_exists(_pm_dir + "/custom_data.spouse"))
        {
            var _file = _pm_name;
            var _pm_path = _pm_dir;
            if (file_exists(_pm_dir + "/custom_data.futa"))
            {
                var _pm_before = ds_list_size(custom_futas_folder);
                var _full_path = _pm_path;
                check_struct = check_custom_futa(_full_path);
                if (check_struct.custom_portrait != -1 && check_struct.custom_mating_press != -1 && check_struct.custom_cowgirls != -1 && check_struct.custom_xray != -1)
                {
                    custom_sprite_loaded = true;
                    tutorial = false;
                    show_debug_message("SUCCESS: Loaded " + _file);
                    ds_list_add(custom_futas_folder, _full_path);
                    pm_registry_add(_full_path);
                    ds_list_add(futa_selector_names, _file);
                    var _has_deep = file_exists(_full_path + "/custom_deepthroat.png");
                    var _has_alts = file_exists(_full_path + "/custom_futa_cowgirl_alt_1.png") || file_exists(_full_path + "/custom_futa_mating_press_alt_1.png");
                    ds_list_add(futa_selector_has_deepthroat, _has_deep);
                    ds_list_add(futa_selector_has_alts, _has_alts);
                    var _preview_spr = -1;  // loaded when shown, as for the APK packs
                    ds_list_add(futa_selector_portraits, _preview_spr);
                }
                if (ds_list_size(custom_futas_folder) > _pm_before)
                {
                    _pm_added++;
                }
            }
            else
            {
                var _pm_before_w = ds_list_size(custom_wives_folder);
                var _full_path = _pm_path;
                var _is_legacy_spouse = file_exists(_full_path + "/custom_data.spouse");
                if (_is_legacy_spouse)
                {
                    if (file_exists(_full_path + "/custom_mating_press.png") || file_exists(_full_path + "/custom_reverse_cowgirl.png"))
                    {
                        custom_wife_sprite_loaded = true;
                        show_debug_message("loaded 1.4 legacy spouse: " + _file);
                        ds_list_add(custom_wives_folder, _full_path);
                        pm_registry_add(_full_path);
                        ds_list_add(wife_selector_names, _file);
                        var _legacy_has_deep = file_exists(_full_path + "/custom_deepthroat.png");
                        ds_list_add(wife_selector_has_cowgirl, _legacy_has_deep);
                        var _w_spr = -1;  // loaded when shown, as for the APK packs
                        ds_list_add(wife_selector_portraits, _w_spr);
                    }
                }
                else
                {
                    check_struct = check_custom_wife(_full_path);
                    if (check_struct.custom_wife_cowgirl != -1 && check_struct.custom_wife_reverse_cowgirl != -1 && check_struct.custom_wife_mating_press != -1)
                    {
                        custom_wife_has_portrait = check_struct.custom_wife_portrait;
                        custom_wife_sprite_loaded = true;
                        show_debug_message("loaded custom wife");
                        ds_list_add(custom_wives_folder, _full_path);
                        pm_registry_add(_full_path);
                        ds_list_add(wife_selector_names, _file);
                        var _w_has_cowgirl = file_exists(_full_path + "/custom_wife_cowgirl_0.png");
                        ds_list_add(wife_selector_has_cowgirl, _w_has_cowgirl);
                        var _w_spr = -1;  // loaded when shown, as for the APK packs
                        ds_list_add(wife_selector_portraits, _w_spr);
                    }
                }
                if (ds_list_size(custom_wives_folder) > _pm_before_w)
                {
                    _pm_added++;
                }
            }
        }
        else if (_pm_depth < 4)
        {
            var _pm_find = tc_ff_first(_pm_dir + "/*", 16);
            while (_pm_find != "")
            {
                if (_pm_find != "." && _pm_find != "..")
                {
                    array_push(_pm_queue, _pm_dir + "/" + _pm_find);
                    array_push(_pm_names, _pm_find);
                    array_push(_pm_depths, _pm_depth + 1);
                }
                _pm_find = tc_ff_next();
            }
            tc_ff_close();
        }
    }
}

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

function func_load_custom_spouse(arg0)
{
    arg0 = tc_norm_path(arg0);
    var sprite_origin_x = 80;
    var sprite_origin_y = 84;
    var portrait_origin_x = 78;
    var portrait_origin_y = 80;
    legacy_custom_wife_toggle = false;
    custom_bottom_boob_size = 1;
    custom_bottom_ass_size = 1;
    custom_partner_male = false;
    custom_contraceptive_pill = false;
    custom_ovulation_pill = false;
    custom_wife_size_response = 1;
    custom_wife_intensity_response = 1;
    custom_wife_cum_response = 1;
    custom_wife_reproductive_response = 1;
    custom_wife_affection_response = 1;
    custom_wife_pain_response = 1;
    var mp_origin_x = sprite_origin_x;
    var mp_origin_y = sprite_origin_y;
    var rc_origin_x = sprite_origin_x;
    var rc_origin_y = sprite_origin_y;
    var dt_origin_x = sprite_origin_x;
    var dt_origin_y = sprite_origin_y;
    var xray_origin_x = 80;
    var xray_origin_y = 84;
    var _lcwx_fixed = false;
    if (file_exists(string(arg0) + "/custom_data.spouse"))
    {
        tc_ini_open_desc(string(arg0) + "/custom_data.spouse");  // native Deeproom: the spouse loader reads only .spouse
        sprite_origin_x = ini_read_real("sprite", "origin_x", 80);
        sprite_origin_y = ini_read_real("sprite", "origin_y", 84);
        portrait_origin_x = ini_read_real("portrait", "origin_x", 78);
        portrait_origin_y = ini_read_real("portrait", "origin_y", 80);
        var max_orgasms = ini_read_real("stats", "max_orgasms", 5);
        custom_max_loads = max_orgasms;
        mp_origin_x = ini_read_real("mating_press", "origin_x", sprite_origin_x);
        mp_origin_y = ini_read_real("mating_press", "origin_y", sprite_origin_y);
        rc_origin_x = ini_read_real("reverse_cowgirl", "origin_x", sprite_origin_x);
        rc_origin_y = ini_read_real("reverse_cowgirl", "origin_y", sprite_origin_y);
        dt_origin_x = ini_read_real("deepthroat", "origin_x", sprite_origin_x);
        dt_origin_y = ini_read_real("deepthroat", "origin_y", sprite_origin_y);
        var _def_xo = ini_read_real("xray", "origin_x", ini_read_real("sprite", "xray_x", 80));
        var _def_yo = ini_read_real("xray", "origin_y", ini_read_real("sprite", "xray_y", 84));
        if (_def_xo > 120 || _def_xo < 40)
        {
            _def_xo = 80;
        }
        if (_def_yo > 120 || _def_yo < 40)
        {
            _def_yo = 84;
        }
        xray_origin_x = _def_xo;
        xray_origin_y = _def_yo;
        // Origin measured from the strip by the patcher at build time (the canal on the penis line, in the
        // strip's own pixels): used exactly, no clamp and no rescale.
        _lcwx_fixed = ini_key_exists("xray", "mobile_origin_x");
        if (_lcwx_fixed)
        {
            xray_origin_x = ini_read_real("xray", "mobile_origin_x", 80);
            xray_origin_y = ini_read_real("xray", "mobile_origin_y", 84);
        }
        custom_contraceptive_pill = bool(ini_read_real("pills", "contraceptive_pill", 0));
        custom_ovulation_pill = bool(ini_read_real("pills", "ovulation_pill", 0));
        custom_eggxcelent_pill = bool(ini_read_real("pills", "eggxcelent_pill", 0));
        custom_greedy_womb_pill = bool(ini_read_real("pills", "greedy_womb_pill", 0));
        custom_dialogue_set_bottom = {};
        var _bottom_keys = ["intro", "intro_return", "sex_start", "sex_continue", "sex_halfway", "sex_exhausted", "sex_orgasm", "sex_after", "cleanup", "touch_boobs", "moan", "kiss", "headpat", "condom_on", "condom_off", "condom_remove", "condom_break"];
        for (var _i = 0; _i < array_length(_bottom_keys); _i += 1)
        {
            var _key = _bottom_keys[_i];
            var _result = func_check_custom_dialogue(_key, false);
            if (array_length(_result) > 0)
            {
                variable_struct_set(custom_dialogue_set_bottom, _key, _result);
            }
        }
        if (variable_struct_names_count(custom_dialogue_set_bottom) == 0)
        {
            custom_dialogue_set_bottom = -1;
        }
        wife_saved_kiss_y_offset = ini_read_real("portrait", "kiss_y_offset", 0);
        wife_saved_kiss_x_offset = ini_read_real("portrait", "kiss_x_offset", 0);
        wife_saved_boob_y_offset = ini_read_real("portrait", "boob_y_offset", 0);
        wife_saved_boob_x_offset = ini_read_real("portrait", "boob_x_offset", 0);
        wife_saved_headpat_y_offset = ini_read_real("portrait", "headpat_y_offset", 0);
        wife_saved_headpat_x_offset = ini_read_real("portrait", "headpat_x_offset", 0);
        if (portrait_number == 1)
        {
            custom_kiss_y_offset = wife_saved_kiss_y_offset;
            custom_kiss_x_offset = wife_saved_kiss_x_offset;
            custom_boob_y_offset = wife_saved_boob_y_offset;
            custom_boob_x_offset = wife_saved_boob_x_offset;
            custom_headpat_y_offset = wife_saved_headpat_y_offset;
            custom_headpat_x_offset = wife_saved_headpat_x_offset;
        }
        custom_wife_size_response = clamp(ini_read_real("personality", "size_response", 1), 0.4, 1.8);
        custom_wife_intensity_response = clamp(ini_read_real("personality", "intensity_response", 1), 0.4, 1.8);
        custom_wife_cum_response = clamp(ini_read_real("personality", "cum_response", 1), 0.4, 1.8);
        custom_wife_reproductive_response = clamp(ini_read_real("personality", "reproductive_response", 1), 0.4, 1.8);
        custom_wife_affection_response = clamp(ini_read_real("personality", "affection_response", 1), 0.4, 1.8);
        custom_wife_pain_response = clamp(ini_read_real("personality", "pain_response", 1), 0.4, 1.8);
        wife_climax_stamina = clamp(ini_read_real("personality", "climax", 100), 100, 2000);
        wife_pleasure_threshold = wife_climax_stamina;
        wife_pleasure_max = wife_climax_stamina;
        wife_womb_capacity = clamp(ini_read_real("personality", "womb_fill", 20), 1, 100);
        fill_max = wife_womb_capacity;
        ini_close();
    }
    ds_list_clear(custom_insert_list);
    ds_list_clear(custom_pullout_list);
    ds_list_clear(custom_condom_break_list);
    func_get_custom_audio(custom_insert_list, string(arg0) + "/sfx/insert");
    func_get_custom_audio(custom_insert_list, string(arg0) + "/insert");
    func_get_custom_audio(custom_pullout_list, string(arg0) + "/sfx/pullout");
    func_get_custom_audio(custom_pullout_list, string(arg0) + "/pullout");
    func_get_custom_audio(custom_condom_break_list, string(arg0) + "/sfx/condom_break");
    func_get_custom_audio(custom_condom_break_list, string(arg0) + "/condom_break");
    var f_port = string(arg0) + "/custom_portrait.png";
    if (!file_exists(f_port))
    {
        if (file_exists(string(arg0) + "/custom_wife_portrait_0.png")) f_port = string(arg0) + "/custom_wife_portrait_0.png";
        else if (file_exists(string(arg0) + "/custom_futa_portrait_0.png")) f_port = string(arg0) + "/custom_futa_portrait_0.png";
        else if (file_exists(string(arg0) + "/custom_portrait1.png")) f_port = string(arg0) + "/custom_portrait1.png";
        else if (file_exists(string(arg0) + "/custom_portraitt.png")) f_port = string(arg0) + "/custom_portraitt.png";
    }
    // One portrait per partner: drop BOTH portrait slots of the previous partner first.
    if (sprite_exists(custom_wife_portrait) && custom_wife_portrait > 189)
    {
        sprite_delete(custom_wife_portrait);
    }
    custom_wife_portrait = -1;
    if (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait > 189)
    {
        sprite_delete(legacy_custom_wife_portrait);
    }
    legacy_custom_wife_portrait = -1;
    custom_wife_portrait_scale = 1;
    if (file_exists(f_port))
    {
        legacy_custom_wife_portrait = sprite_add(f_port, func_portrait_frames(f_port, 10), false, false, portrait_origin_x, portrait_origin_y);
        custom_wife_has_portrait = true;
        if (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1)
        {
            var _wpw = sprite_get_width(legacy_custom_wife_portrait);
            if (_wpw > 0)
            {
                custom_wife_portrait_scale = 128 / _wpw;
            }
        }
    }
    else
    {
        custom_wife_has_portrait = false;
    }
    var f_mate = string(arg0) + "/custom_mating_press.png";
    if (file_exists(f_mate))
    {
        if (sprite_exists(legacy_custom_wife_mating_press))
        {
            sprite_delete(legacy_custom_wife_mating_press);
        }
        legacy_custom_wife_mating_press = sprite_add(f_mate, 4, false, false, mp_origin_x, mp_origin_y);
    }
    var f_cow = string(arg0) + "/custom_reverse_cowgirl.png";
    if (file_exists(f_cow))
    {
        if (sprite_exists(legacy_custom_wife_reverse_cowgirl))
        {
            sprite_delete(legacy_custom_wife_reverse_cowgirl);
        }
        legacy_custom_wife_reverse_cowgirl = sprite_add(f_cow, 5, false, false, rc_origin_x, rc_origin_y);
    }
    var f_deep = string(arg0) + "/custom_deepthroat.png";
    if (file_exists(f_deep))
    {
        if (sprite_exists(legacy_custom_wife_deepthroat))
        {
            sprite_delete(legacy_custom_wife_deepthroat);
        }
        legacy_custom_wife_deepthroat = sprite_add(f_deep, 5, false, false, dt_origin_x, dt_origin_y);
    }
    else
    {
        legacy_custom_wife_deepthroat = -1;
    }
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
    else
    {
        legacy_custom_wife_xray = -1;
    }
    legacy_custom_wife_toggle = true;
}

custom_dialogue_set_top = -1;
custom_dialogue_set_bottom = -1;

function func_hex_to_color(arg0, arg1)
{
    var _str = string_upper(string_trim(arg0));
    if (string_char_at(_str, 1) == "#")
    {
        _str = string_delete(_str, 1, 1);
    }
    if (string_length(_str) != 6)
    {
        return arg1;
    }
    var _hex = "0123456789ABCDEF";
    var _r = ((string_pos(string_char_at(_str, 1), _hex) - 1) * 16) + (string_pos(string_char_at(_str, 2), _hex) - 1);
    var _g = ((string_pos(string_char_at(_str, 3), _hex) - 1) * 16) + (string_pos(string_char_at(_str, 4), _hex) - 1);
    var _b = ((string_pos(string_char_at(_str, 5), _hex) - 1) * 16) + (string_pos(string_char_at(_str, 6), _hex) - 1);
    return make_color_rgb(_r, _g, _b);
}

function func_check_custom_dialogue(arg0, arg1)
{
    var return_array = [];
    if (ini_key_exists("dialogue", string(arg0) + "_0"))
    {
        for (var _i = 0; ini_key_exists("dialogue", string(arg0) + "_" + string(_i)); _i += 1)
        {
            return_array[_i] = ini_read_string("dialogue", string(arg0) + "_" + string(_i), "");
        }
    }
    if (arg1 == true && ini_key_exists("dialogue_alt", string(arg0) + "_0"))
    {
        return_array = [];
        for (var _i = 0; ini_key_exists("dialogue_alt", string(arg0) + "_" + string(_i)); _i += 1)
        {
            return_array[_i] = ini_read_string("dialogue_alt", string(arg0) + "_" + string(_i), "");
        }
    }
    return return_array;
}

function func_top_speak(arg0)
{
    if (char_dialogue_toggle == false)
    {
        exit;
    }
    if (custom_dialogue_set_top == -1)
    {
        exit;
    }
    var _arr = variable_struct_get(custom_dialogue_set_top, arg0);
    if (is_undefined(_arr) || !is_array(_arr) || array_length(_arr) == 0)
    {
        exit;
    }
    var _line = _arr[irandom(array_length(_arr) - 1)];
    var _priority = 1;
    if (arg0 == "sex_orgasm")
    {
        _priority = 2;
        oDialogueManager.top_dialogue_timer = 0;
        oDialogueManager.current_top_dialogue_priority = -1;
    }
    if (_line != "")
    {
        _line = func_replace_tags(_line);
        oDialogueManager.trigger_dialogue("?" + _line, "", 180, _priority);
    }
}

function func_replace_tags(arg0)
{
    if (string_pos("[LOADS]", arg0) != 0)
    {
        arg0 = string_replace_all(arg0, "[LOADS]", string(loads));
    }
    if (string_pos("[ROUND]", arg0) != 0)
    {
        arg0 = string_replace_all(arg0, "[ROUND]", string(loads + 1));
    }
    if (string_pos("[PARTNER]", arg0) != 0)
    {
        var _wife_is_custom = custom_wife_sprite_loaded == true || legacy_custom_wife_toggle == true;
        if (!_wife_is_custom || custom_sprite_loaded == true)
        {
            arg0 = string_replace_all(arg0, "[PARTNER]", "wife");
        }
        else
        {
            arg0 = string_replace_all(arg0, "[PARTNER]", "friend");
        }
    }
    return arg0;
}

function func_load_vanilla_dialogue(arg0)
{
    custom_dialogue_set_top = -1;
    var _path = (os_type == os_android || os_type == os_ios) ? ("custom_stuff/dialogue/" + arg0) : (working_directory + "/custom_stuff/dialogue/" + arg0);
    if (!file_exists(_path))
    {
        _path = (os_type == os_android || os_type == os_ios) ? ("dialogue/" + arg0) : (working_directory + "dialogue/" + arg0);
    }
    if (!file_exists(_path))
    {
        _path = "dialogue_packs/" + arg0;
        if (!file_exists(_path))
        {
            exit;
        }
    }
    var _buffer = buffer_load(_path);
    if (_buffer == -1)
    {
        exit;
    }
    var _json_string = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);
    var _data = json_parse(_json_string);
    if (is_undefined(_data))
    {
        exit;
    }
    custom_dialogue_set_top = _data;
}

function func_bottom_speak(arg0)
{
    if (char_dialogue_toggle == false)
    {
        exit;
    }
    if (custom_dialogue_set_bottom == -1)
    {
        exit;
    }
    var _arr = variable_struct_get(custom_dialogue_set_bottom, arg0);
    if (is_undefined(_arr) || !is_array(_arr) || array_length(_arr) == 0)
    {
        exit;
    }
    var _line = _arr[irandom(array_length(_arr) - 1)];
    var _priority = 1;
    if (arg0 == "sex_orgasm")
    {
        _priority = 2;
        oDialogueManager.wife_dialogue_timer = 0;
        oDialogueManager.current_wife_dialogue_priority = -1;
    }
    if (_line != "")
    {
        oDialogueManager.trigger_dialogue("", "?" + _line, 180, _priority);
    }
}

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
    custom_wife_reproductive_response = 1;
    custom_wife_affection_response = 1;
    custom_wife_pain_response = 1;
    if (file_exists(string(arg0) + "/custom_data.wife"))
    {
        tc_ini_open_desc(string(arg0) + "/custom_data.wife");
        sprite_origin_x = ini_read_real("sprite", "origin_x", 80);
        sprite_origin_y = ini_read_real("sprite", "origin_y", 84);
        // Native Deeproom: the .wife loader reads only the flat [sprite] keys. Packs are tuned against that, so the
        // spouse-style [mating_press]/[reverse_cowgirl]/[deepthroat] sections many packs also carry are NOT used here.
        cowgirl_origin_x = ini_read_real("sprite", "cowgirl_origin_x", sprite_origin_x);
        cowgirl_origin_y = ini_read_real("sprite", "cowgirl_origin_y", sprite_origin_y);
        mp_origin_x = ini_read_real("sprite", "mating_press_origin_x", sprite_origin_x);
        mp_origin_y = ini_read_real("sprite", "mating_press_origin_y", sprite_origin_y);
        dt_origin_x = ini_read_real("sprite", "deepthroat_origin_x", sprite_origin_x);
        dt_origin_y = ini_read_real("sprite", "deepthroat_origin_y", sprite_origin_y);
        portrait_origin_x = ini_read_real("portrait", "origin_x", 64);
        portrait_origin_y = ini_read_real("portrait", "origin_y", 64);
        custom_bottom_boob_size = ini_read_real("stats", "bottom_boob_size", 1);
        custom_bottom_ass_size = ini_read_real("stats", "bottom_ass_size", 1);
        custom_wife_size_response = clamp(ini_read_real("personality", "size_response", 1), 0.4, 1.8);
        custom_wife_intensity_response = clamp(ini_read_real("personality", "intensity_response", 1), 0.4, 1.8);
        custom_wife_cum_response = clamp(ini_read_real("personality", "cum_response", 1), 0.4, 1.8);
        custom_wife_reproductive_response = clamp(ini_read_real("personality", "reproductive_response", 1), 0.4, 1.8);
        custom_wife_affection_response = clamp(ini_read_real("personality", "affection_response", 1), 0.4, 1.8);
        custom_wife_pain_response = clamp(ini_read_real("personality", "pain_response", 1), 0.4, 1.8);
        wife_climax_stamina = clamp(ini_read_real("personality", "climax", 100), 100, 2000);
        wife_pleasure_threshold = wife_climax_stamina;
        wife_pleasure_max = wife_climax_stamina;
        wife_womb_capacity = clamp(ini_read_real("personality", "womb_fill", 20), 1, 100);
        fill_max = wife_womb_capacity;
        custom_contraceptive_pill = bool(ini_read_real("pills", "contraceptive_pill", 0));
        custom_ovulation_pill = bool(ini_read_real("pills", "ovulation_pill", 0));
        custom_eggxcelent_pill = bool(ini_read_real("pills", "eggxcelent_pill", 0));
        custom_greedy_womb_pill = bool(ini_read_real("pills", "greedy_womb_pill", 0));
        custom_partner_male = bool(ini_read_real("gender", "is_male", 0));
        wife_saved_kiss_y_offset = ini_read_real("portrait", "kiss_y_offset", 0);
        wife_saved_kiss_x_offset = ini_read_real("portrait", "kiss_x_offset", 0);
        wife_saved_boob_y_offset = ini_read_real("portrait", "boob_y_offset", 0);
        wife_saved_boob_x_offset = ini_read_real("portrait", "boob_x_offset", 0);
        wife_saved_headpat_y_offset = ini_read_real("portrait", "headpat_y_offset", 0);
        wife_saved_headpat_x_offset = ini_read_real("portrait", "headpat_x_offset", 0);
        if (portrait_number == 1)
        {
            custom_kiss_y_offset = wife_saved_kiss_y_offset;
            custom_kiss_x_offset = wife_saved_kiss_x_offset;
            custom_boob_y_offset = wife_saved_boob_y_offset;
            custom_boob_x_offset = wife_saved_boob_x_offset;
            custom_headpat_y_offset = wife_saved_headpat_y_offset;
            custom_headpat_x_offset = wife_saved_headpat_x_offset;
        }
        custom_dialogue_set_bottom = {};
        var _bottom_keys = ["intro", "intro_return", "sex_start", "sex_continue", "sex_halfway", "sex_exhausted", "sex_orgasm", "sex_after", "cleanup", "touch_boobs", "moan", "kiss", "headpat", "condom_on", "condom_off", "condom_remove", "condom_break"];
        for (var _i = 0; _i < array_length(_bottom_keys); _i += 1)
        {
            var _key = _bottom_keys[_i];
            var _result = func_check_custom_dialogue(_key, false);
            if (array_length(_result) > 0)
            {
                variable_struct_set(custom_dialogue_set_bottom, _key, _result);
            }
        }
        if (variable_struct_names_count(custom_dialogue_set_bottom) == 0)
        {
            custom_dialogue_set_bottom = -1;
        }
        ini_close();
    }
    custom_wife_alt_max = 1;
    while (file_exists(string(arg0) + "/custom_wife_mating_press_alt_" + string(custom_wife_alt_max) + ".png"))
    {
        custom_wife_alt_max++;
    }
    var _suffix = (arg1 == 0) ? "_0.png" : ("_alt_" + string(arg1) + ".png");
    var file_check = string(arg0) + "/custom_wife_portrait" + _suffix;
    if (!file_exists(file_check))
    {
        file_check = string(arg0) + "/custom_wife_portrait_0.png";  // alt variant without its own portrait
    }
    // One portrait per partner: drop BOTH portrait slots of the previous partner first.
    if (sprite_exists(custom_wife_portrait) && custom_wife_portrait > 189)
    {
        sprite_delete(custom_wife_portrait);
    }
    custom_wife_portrait = -1;
    if (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait > 189)
    {
        sprite_delete(legacy_custom_wife_portrait);
    }
    legacy_custom_wife_portrait = -1;
    custom_wife_portrait_scale = 1;
    if (file_exists(file_check))
    {
        custom_wife_portrait = sprite_add(file_check, func_portrait_frames(file_check, 17), false, false, portrait_origin_x, portrait_origin_y);
        custom_wife_has_portrait = true;
        if (sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1 && sprite_get_width(custom_wife_portrait) > 0)
        {
            custom_wife_portrait_scale = 128 / sprite_get_width(custom_wife_portrait);
        }
    }
    else
    {
        custom_wife_has_portrait = false;
    }
    file_check = string(arg0) + "/custom_wife_cowgirl" + _suffix;
    if (file_exists(file_check))
    {
        if (custom_wife_cowgirl != -1 && sprite_exists(custom_wife_cowgirl))
        {
            sprite_delete(custom_wife_cowgirl);
        }
        custom_wife_cowgirl = sprite_add(file_check, 11, false, false, cowgirl_origin_x, cowgirl_origin_y);
        var _scale = 160 / sprite_get_width(custom_wife_cowgirl);
        sprite_set_offset(custom_wife_cowgirl, cowgirl_origin_x / _scale, cowgirl_origin_y / _scale);
    }
    file_check = string(arg0) + "/custom_wife_reverse_cowgirl" + _suffix;
    if (file_exists(file_check))
    {
        if (custom_wife_reverse_cowgirl != -1 && sprite_exists(custom_wife_reverse_cowgirl))
        {
            sprite_delete(custom_wife_reverse_cowgirl);
        }
        custom_wife_reverse_cowgirl = sprite_add(file_check, 10, false, false, cowgirl_origin_x, cowgirl_origin_y);
        var _scale = 160 / sprite_get_width(custom_wife_reverse_cowgirl);
        sprite_set_offset(custom_wife_reverse_cowgirl, cowgirl_origin_x / _scale, cowgirl_origin_y / _scale);
    }
    file_check = string(arg0) + "/custom_wife_mating_press" + _suffix;
    if (file_exists(file_check))
    {
        if (custom_wife_mating_press != -1 && sprite_exists(custom_wife_mating_press))
        {
            sprite_delete(custom_wife_mating_press);
        }
        custom_wife_mating_press = sprite_add(file_check, 5, false, false, mp_origin_x, mp_origin_y);
    }
    file_check = string(arg0) + "/custom_wife_xray" + _suffix;
    if (file_exists(file_check))
    {
        if (custom_wife_xray != -1 && sprite_exists(custom_wife_xray))
        {
            sprite_delete(custom_wife_xray);
        }
        var _cwx_ox = 80;
        var _cwx_oy = 84;
        var _cwx_fixed = false;
        if (file_exists(string(arg0) + "/custom_data.wife"))
        {
            tc_ini_open_desc(string(arg0) + "/custom_data.wife");
            _cwx_ox = ini_read_real("xray", "origin_x", ini_read_real("sprite", "xray_x", 80));
            _cwx_oy = ini_read_real("xray", "origin_y", ini_read_real("sprite", "xray_y", 84));
            _cwx_fixed = ini_key_exists("xray", "mobile_origin_x");
            if (_cwx_fixed)
            {
                _cwx_ox = ini_read_real("xray", "mobile_origin_x", 80);
                _cwx_oy = ini_read_real("xray", "mobile_origin_y", 84);
            }
            ini_close();
        }
        if (!_cwx_fixed && (_cwx_ox > 120 || _cwx_ox < 40))
        {
            _cwx_ox = 80;
        }
        if (!_cwx_fixed && (_cwx_oy > 120 || _cwx_oy < 40))
        {
            _cwx_oy = 84;
        }
        var _cwx_frames = 3;
        var _cwx_probe = sprite_add(file_check, 1, false, false, 0, 0);
        if (_cwx_probe != -1)
        {
            var _cwx_pw = sprite_get_width(_cwx_probe);
            sprite_delete(_cwx_probe);
            if (_cwx_pw >= 160 && (_cwx_pw mod 160) == 0)
            {
                _cwx_frames = clamp(_cwx_pw div 160, 1, 8);
            }
        }
        custom_wife_xray = sprite_add(file_check, _cwx_frames, false, false, _cwx_ox, _cwx_oy);
        wife_xray_fixed_offset = _cwx_fixed;
        var _cwx_w = _cwx_fixed ? 160 : sprite_get_width(custom_wife_xray);
        if (_cwx_w > 0 && _cwx_w != 160)
        {
            var _cwx_sc = 160 / _cwx_w;
            sprite_set_offset(custom_wife_xray, _cwx_ox / _cwx_sc, _cwx_oy / _cwx_sc);
        }
    }
    file_check = string(arg0) + "/custom_wife_deepthroat" + _suffix;
    if (file_exists(file_check))
    {
        if (custom_wife_deepthroat != -1 && sprite_exists(custom_wife_deepthroat))
        {
            sprite_delete(custom_wife_deepthroat);
        }
        custom_wife_deepthroat = sprite_add(file_check, 5, false, false, dt_origin_x, dt_origin_y);
    }
    else
    {
        custom_wife_deepthroat = -1;
    }
}

function func_validate_sex_position()
{
    var _wife_has_deepthroat = legacy_custom_wife_toggle ? (legacy_custom_wife_deepthroat != -1 && sprite_exists(legacy_custom_wife_deepthroat)) : (!custom_wife_toggle || (custom_wife_deepthroat != -1 && sprite_exists(custom_wife_deepthroat)));
    var _wife_has_cowgirl = legacy_custom_wife_toggle ? false : (custom_wife_cowgirl != -1 && sprite_exists(custom_wife_cowgirl));
    if (sex_position == 3 && !_wife_has_deepthroat)
    {
        sex_position = 0;
    }
    if (sex_position == 2 && !_wife_has_cowgirl)
    {
        sex_position = 0;
    }
}

function func_wife_dt_file_cached()
{
    var _key = string(custom_wife_index) + ":" + string(custom_wife_mating_press);
    if (wife_dt_cache_key != _key)
    {
        wife_dt_cache_key = _key;
        wife_dt_cache_val = file_exists(string(ds_list_find_value(custom_wives_folder, custom_wife_index)) + "/custom_wife_deepthroat_0.png");
    }
    return wife_dt_cache_val;
}

function func_get_moan_audio(arg0)
{
    if (ds_map_find_value(custom_audio_storage, arg0) == undefined)
    {
        var audio_add = audio_create_stream(arg0);
        ds_map_add(custom_audio_storage, arg0, audio_add);
    }
    return ds_map_find_value(custom_audio_storage, arg0);
}

function func_get_custom_audio(arg0, arg1)
{
    arg1 = tc_norm_path(arg1);
    var _has_manifest = file_exists(arg1 + "/_manifest.txt");
    if (_has_manifest || tc_dir_exists(arg1))
    {
        ds_list_clear(arg0);
        show_debug_message("scanning folder: " + string(arg1));
        var _file = tc_ff_first(string(arg1) + "/*.ogg", 0);
        show_debug_message("first file found: " + string(_file));
        while (_file != "")
        {
            var moan_file = string(arg1) + "/" + string(_file);
            if (file_exists(moan_file))
            {
                ds_list_add(arg0, func_get_moan_audio(moan_file));
            }
            _file = tc_ff_next();
        }
        tc_ff_close();
    }
}

function func_cs_load_pack(arg0)
{
    ds_list_clear(cs_moan_slow_list);
    ds_list_clear(cs_moan_fast_list);
    ds_list_clear(cs_orgasm_list);
    ds_list_clear(cs_orgasm_alt_list);
    ds_list_clear(cs_futa_alt_names);
    cs_futa_alt_index = 0;
    if (arg0 < 0 || arg0 >= ds_list_size(cs_futa_packs))
    {
        exit;
    }
    var _pack_path = ds_list_find_value(cs_futa_packs, arg0);
    func_get_custom_audio(cs_moan_slow_list, _pack_path + "/moan_slow");
    func_get_custom_audio(cs_moan_fast_list, _pack_path + "/moan_fast");
    func_get_custom_audio(cs_orgasm_list, _pack_path + "/orgasm");
    var _orgasm_path = _pack_path + "/orgasm";
    if (tc_dir_exists(_orgasm_path))
    {
        var _alt_file = tc_ff_first(_orgasm_path + "/*", 16);
        while (_alt_file != "")
        {
            var _alt_full = _orgasm_path + "/" + _alt_file;
            if (tc_dir_exists(_alt_full))
            {
                ds_list_add(cs_futa_alt_names, _alt_file);
            }
            _alt_file = tc_ff_next();
        }
        tc_ff_close();
    }
}

function func_cs_apply_alt(arg0)
{
    ds_list_clear(cs_orgasm_alt_list);
    if (arg0 <= 0 || ds_list_size(cs_futa_alt_names) == 0)
    {
        exit;
    }
    var _real_idx = arg0 - 1;
    if (_real_idx >= ds_list_size(cs_futa_alt_names))
    {
        exit;
    }
    var _pack_path = ds_list_find_value(cs_futa_packs, cs_futa_pack_index);
    var _alt_name = ds_list_find_value(cs_futa_alt_names, _real_idx);
    var _alt_path = _pack_path + "/orgasm/" + _alt_name;
    func_get_custom_audio(cs_orgasm_alt_list, _alt_path);
}

function func_cs_wife_load_pack(arg0)
{
    ds_list_clear(cs_wife_moan_slow_list);
    ds_list_clear(cs_wife_moan_fast_list);
    ds_list_clear(cs_wife_orgasm_list);
    ds_list_clear(cs_wife_orgasm_alt_list);
    ds_list_clear(cs_wife_alt_names);
    cs_wife_alt_index = 0;
    if (arg0 < 0 || arg0 >= ds_list_size(cs_futa_packs))
    {
        exit;
    }
    var _pack_path = ds_list_find_value(cs_futa_packs, arg0);
    func_get_custom_audio(cs_wife_moan_slow_list, _pack_path + "/moan_slow");
    func_get_custom_audio(cs_wife_moan_fast_list, _pack_path + "/moan_fast");
    func_get_custom_audio(cs_wife_orgasm_list, _pack_path + "/orgasm");
    var _orgasm_path = _pack_path + "/orgasm";
    if (tc_dir_exists(_orgasm_path))
    {
        var _alt_file = tc_ff_first(_orgasm_path + "/*", 16);
        while (_alt_file != "")
        {
            var _alt_full = _orgasm_path + "/" + _alt_file;
            if (tc_dir_exists(_alt_full))
            {
                ds_list_add(cs_wife_alt_names, _alt_file);
            }
            _alt_file = tc_ff_next();
        }
        tc_ff_close();
    }
}

function func_cs_wife_apply_alt(arg0)
{
    ds_list_clear(cs_wife_orgasm_alt_list);
    if (arg0 <= 0 || ds_list_size(cs_wife_alt_names) == 0)
    {
        exit;
    }
    var _real_idx = arg0 - 1;
    if (_real_idx >= ds_list_size(cs_wife_alt_names))
    {
        exit;
    }
    var _pack_path = ds_list_find_value(cs_futa_packs, cs_wife_pack_index);
    var _alt_name = ds_list_find_value(cs_wife_alt_names, _real_idx);
    var _alt_path = _pack_path + "/orgasm/" + _alt_name;
    func_get_custom_audio(cs_wife_orgasm_alt_list, _alt_path);
}

function func_futa_pack_is_legacy(arg0)
{
    // Which lover loader a pack uses (same rule on PC and mobile): the standard-name (legacy) loader when
    // custom_mating_press.png exists, as in native Deeproom, or when there is no modern mating press
    // (packs with odd names rely on the legacy loader's fallbacks); otherwise the modern _0 loader.
    // Previously every pack with custom_data.futa, and every pack on Android/iOS, was sent to the legacy
    // loader, so modern-only packs loaded a 17-frame portrait as 10 frames and kept the previous
    // character's mating press, cowgirl and X-ray sprites.
    return file_exists(string(arg0) + "/custom_mating_press.png") || !file_exists(string(arg0) + "/custom_futa_mating_press_0.png");
}

function func_portrait_frames(arg0, arg1)
{
    // Portraits are 10 frames (standard) or 17 (modern) of ANY width (128 px usual, 256 px high-res packs
    // exist). Keep the loader's default arg1 when the width divides by it; switch to the other count only
    // when the width divides by that one and not by the default (e.g. a 10-frame strip saved under a
    // modern _0 name). Never derive the count from a pixel size.
    var _probe = sprite_add(arg0, 1, false, false, 0, 0);
    var _frames = arg1;
    if (sprite_exists(_probe) && _probe != -1)
    {
        var _w = sprite_get_width(_probe);
        sprite_delete(_probe);
        var _other = (arg1 == 17) ? 10 : 17;
        if (_w > 0 && (_w mod arg1) != 0 && (_w mod _other) == 0)
        {
            _frames = _other;
        }
    }
    return _frames;
}

function func_futa_selector_portrait(arg0)
{
    // Character-select preview: the portrait of the loader this pack will really use.
    var _a = string(arg0) + "/custom_futa_portrait_0.png";
    var _b = string(arg0) + "/custom_portrait.png";
    var _file = "";
    if (func_futa_pack_is_legacy(arg0))
    {
        _file = file_exists(_b) ? _b : (file_exists(_a) ? _a : "");
    }
    else
    {
        _file = file_exists(_a) ? _a : (file_exists(_b) ? _b : "");
    }
    if (_file == "")
    {
        return -1;
    }
    return sprite_add(_file, func_portrait_frames(_file, (_file == _a) ? 17 : 10), false, false, 54, 82);
}

function func_wife_selector_portrait(arg0)
{
    // Character-select preview for a partner: the portrait of the loader func_load_custom_wife will use
    // (spouse loader when custom_data.spouse or custom_mating_press.png exists or the modern mating press
    // is missing), with the frame count taken from the strip width.
    var _a = string(arg0) + "/custom_wife_portrait_0.png";
    var _b = string(arg0) + "/custom_portrait.png";
    var _spouse = file_exists(string(arg0) + "/custom_data.spouse") || file_exists(string(arg0) + "/custom_mating_press.png") || !file_exists(string(arg0) + "/custom_wife_mating_press_0.png");
    var _file = "";
    if (_spouse)
    {
        _file = file_exists(_b) ? _b : (file_exists(_a) ? _a : "");
    }
    else
    {
        _file = file_exists(_a) ? _a : (file_exists(_b) ? _b : "");
    }
    if (_file == "")
    {
        return -1;
    }
    return sprite_add(_file, func_portrait_frames(_file, (_file == _a) ? 17 : 10), false, false, 32, 48);
}

function check_custom_futa(arg0)
{
    arg0 = tc_norm_path(arg0);
    var is_legacy = file_exists(string(arg0) + "/custom_mating_press.png") && !file_exists(string(arg0) + "/custom_futa_mating_press_0.png");
    check_struct = {};
    if (is_legacy)
    {
        check_struct.custom_data = file_exists(string(arg0) + "/custom_data.futa");
        check_struct.custom_portrait = file_exists(string(arg0) + "/custom_portrait.png");
        check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_mating_press.png");
        check_struct.custom_cowgirls = file_exists(string(arg0) + "/custom_reverse_cowgirl.png");
        check_struct.custom_xray = file_exists(string(arg0) + "/custom_xray.png");
    }
    else
    {
        check_struct.custom_data = file_exists(string(arg0) + "/custom_data.futa");
        check_struct.custom_portrait = file_exists(string(arg0) + "/custom_futa_portrait_0.png");
        check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_futa_mating_press_0.png");
        check_struct.custom_cowgirls = file_exists(string(arg0) + "/custom_futa_cowgirls_0.png");
        check_struct.custom_xray = file_exists(string(arg0) + "/custom_futa_xray_0.png");
    }
    return check_struct;
}

function check_custom_image_size(arg0)
{
    // Native Deeproom 4.0.3: a 19-frame custom_mating_press.png (160 px frames) is not a legacy strip, so the
    // pack goes to the modern _0 loader. A pack with no modern mating press keeps the legacy loader (its fallbacks).
    if (!file_exists(string(arg0) + "/custom_futa_mating_press_0.png"))
    {
        return true;
    }
    var test_sprite = sprite_add(string(arg0) + "/custom_mating_press.png", 1, false, false, 0, 0);
    if (test_sprite == -1 || !sprite_exists(test_sprite))
    {
        return true;
    }
    var frames = sprite_get_width(test_sprite) / 160;
    sprite_delete(test_sprite);
    return frames != 19;
}

function func_load_custom_futa(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    is_legacy_custom = false;
    if (func_futa_pack_is_legacy(arg0))
    {
        is_legacy_custom = true;
        if (check_custom_image_size(arg0))
        {
            sprite_origin_x = 80;
            sprite_origin_y = 84;
            cowgirl_origin_x = 80;
            cowgirl_origin_y = 84;
            mp_origin_x = 80;
            mp_origin_y = 84;
            dt_origin_x = 80;
            dt_origin_y = 84;
            portrait_origin_x = 64;
            portrait_origin_y = 64;
            var custom_condom_offset = 78;
            custom_cum_y_offset = 0;
            custom_cum_y_offset_mp = 0;
            custom_cum_y_offset_cg = 0;
            custom_cum_y_offset_dt = 0;
            custom_condom_offset_deepthroat = 0;
            custom_bc_mp_off_y = 0;
            custom_bc_cg_off_y = 0;
            custom_bc_rc_off_y = 0;
            custom_bc_dt_off_y = 0;
            custom_xray_offset_y = 0;
            custom_condom_offset_mpress = 0;
            custom_condom_offset_cowgirls = 0;
            comment = "memory bleed guard";
            custom_max_loads = 5;
            custom_top_boob_size = 1;
            custom_top_ass_size = 1;
            custom_top_penis_length = 1;
            custom_top_penis_width = 1;
            custom_ball_size = 1;
            custom_virility_modifier = 1;
            custom_cum_volume_modifier = 1;
            custom_stroke_depth = 1;
            custom_stroke_speed = 1;
            custom_pump_delay = 90;
            custom_mega_sperm_pill = false;
            custom_equine_pill = false;
            custom_knotted_pill = false;
            custom_extra_thick_pill = false;
            custom_diphallia_pill = false;
            custom_stamina_pill = false;
            custom_leaky_pill = false;
            custom_hyper_breeding_pill = false;
            custom_blockage_pill = false;
            custom_quickshot_pill = false;
            custom_reverse_speed_pill = false;
            custom_edge_addict_pill = false;
            custom_premature_pill = false;
            custom_edge_lover_pill = false;
            custom_growth_cascade_pill = false;
            custom_livestream_pill = false;
            custom_three_pump_champ_pill = false;
            custom_penis_type_index = 0;
            if (file_exists(string(arg0) + "/custom_data.futa"))
            {
                tc_ini_open_desc(string(arg0) + "/custom_data.futa");
                sprite_origin_x = ini_read_real("sprite", "origin_x", 80);
                sprite_origin_y = ini_read_real("sprite", "origin_y", 84);
                cowgirl_origin_x = ini_read_real("sprite", "cowgirl_origin_x", sprite_origin_x);
                cowgirl_origin_y = ini_read_real("sprite", "cowgirl_origin_y", sprite_origin_y);
                mp_origin_x = ini_read_real("sprite", "mating_press_origin_x", sprite_origin_x);
                mp_origin_y = ini_read_real("sprite", "mating_press_origin_y", sprite_origin_y);
                dt_origin_x = ini_read_real("sprite", "deepthroat_origin_x", sprite_origin_x);
                dt_origin_y = ini_read_real("sprite", "deepthroat_origin_y", sprite_origin_y);
                custom_condom_offset = ini_read_real("sprite", "condom_y", 78);
                custom_xray_offset_y = ini_read_real("sprite", "xray_offset_y", 0);
                custom_cum_y_offset = ini_read_real("sprite", "cum_y_offset", 0);
                custom_cum_y_offset_mp = ini_read_real("CumPos", "mating_press_cum_offset", 0);
                custom_cum_y_offset_cg = ini_read_real("CumPos", "cg_and_rcg_cum_offset", 0);
                custom_cum_y_offset_dt = ini_read_real("CumPos", "deepthroat_cum_offset", 0);
                portrait_origin_x = ini_read_real("portrait", "origin_x", 64);
                portrait_origin_y = ini_read_real("portrait", "origin_y", 64);
                custom_condom_offset_mpress = ini_read_real("CondomPos", "condom_y_mpress", ini_read_real("condom", "condom_y_mpress", 0));
                custom_condom_offset_cowgirls = ini_read_real("CondomPos", "condom_y_cowgirls", ini_read_real("condom", "condom_y_cowgirls", 0));
                custom_condom_offset_deepthroat = ini_read_real("CondomPos", "deepthroat_condom_offset", 0);
                sex_progress_max = ini_read_real("stats", "stamina", 75, 700);
                user_pumps_max = ini_read_real("stats", "max_pumps", 12, 500);
                cum_shot_mult = ini_read_real("stats", "cumshot_mult", 1);
                rand_pump_delay_min = ini_read_real("stats", "pump_delay_min", 130, 60);
                rand_pump_delay_max = ini_read_real("stats", "pump_delay_max", 600, 700);
                custom_max_loads = ini_read_real("stats", "max_orgasms", 5);
                custom_top_boob_size = ini_read_real("stats", "top_boob_size", 1);
                custom_top_ass_size = ini_read_real("stats", "top_ass_size", 1);
                custom_top_penis_length = ini_read_real("stats", "top_penis_length", 1);
                custom_top_penis_width = ini_read_real("stats", "top_penis_width", 1);
                custom_ball_size = ini_read_real("stats", "ball_size", 1);
                custom_virility_modifier = ini_read_real("stats", "virility_modifier", 1);
                custom_cum_volume_modifier = ini_read_real("stats", "cum_volume_modifier", 1);
                custom_stroke_depth = ini_read_real("stats", "stroke_depth", 1);
                custom_stroke_speed = ini_read_real("stats", "stroke_speed", 1);
                custom_pump_delay = clamp(ini_read_real("stats", "pump_delay", 90), 30, 360);
                custom_bc_mp_off_y = ini_read_real("BallClench", "bc_mp_off_y", 0);
                custom_bc_cg_off_y = ini_read_real("BallClench", "bc_cg_off_y", 0);
                custom_bc_rc_off_y = ini_read_real("BallClench", "bc_rc_off_y", 0);
                custom_bc_dt_off_y = ini_read_real("BallClench", "bc_dt_off_y", 0);
                condom_color = func_hex_to_color(ini_read_string("colors", "condom", ""), 16777215);
                cum_color = func_hex_to_color(ini_read_string("colors", "cum", ""), 13497599);
                custom_mega_sperm_pill = bool(ini_read_real("pills", "mega_sperm_pill", 0));
                custom_extra_thick_pill = bool(ini_read_real("pills", "extra_thick_pill", 0));
                custom_diphallia_pill = bool(ini_read_real("pills", "diphallia_pill", 0));
                custom_stamina_pill = bool(ini_read_real("pills", "stamina_pill", 0));
                custom_leaky_pill = bool(ini_read_real("pills", "leaky_pill", 0));
                custom_hyper_breeding_pill = bool(ini_read_real("pills", "hyper_breeding_pill", 0));
                custom_blockage_pill = bool(ini_read_real("pills", "blockage_pill", 0));
                custom_quickshot_pill = bool(ini_read_real("pills", "quickshot_pill", 0));
                custom_reverse_speed_pill = bool(ini_read_real("pills", "reverse_speed_pill", 0));
                custom_edge_addict_pill = bool(ini_read_real("pills", "edge_addicted_pill", 0));
                custom_pound_town_pill = bool(ini_read_real("pills", "pound_town_pill", 0));
                custom_premature_pill = bool(ini_read_real("pills", "premature_pill", 0));
                custom_edge_lover_pill = bool(ini_read_real("pills", "edge_lover_pill", 0));
                custom_growth_cascade_pill = bool(ini_read_real("pills", "growth_cascade_pill", 0));
                custom_livestream_pill = bool(ini_read_real("pills", "livestream_pill", 0));
                custom_three_pump_champ_pill = bool(ini_read_real("pills", "three_pump_champ_pill", 0));
                custom_penis_type_index = ini_read_real("penis", "penis_type_index", 0);
                custom_dialogue_set_top = {};
                var _top_keys = ["intro", "intro_return", "sex_start", "sex_continue", "sex_halfway", "sex_exhausted", "sex_orgasm", "sex_after", "cleanup", "kiss", "condom_on", "condom_off", "condom_broken", "condom_remove", "condom_break", "pullout", "headpat", "spank", "touch_boobs", "moan", "mystery_effect", "sex_encorgasm"];
                for (var _i = 0; _i < array_length(_top_keys); _i += 1)
                {
                    var _key = _top_keys[_i];
                    var _result = func_check_custom_dialogue(_key, false);
                    if (array_length(_result) > 0)
                    {
                        variable_struct_set(custom_dialogue_set_top, _key, _result);
                    }
                }
                if (variable_struct_names_count(custom_dialogue_set_top) == 0)
                {
                    custom_dialogue_set_top = -1;
                }
                futa_saved_kiss_y_offset = ini_read_real("portrait", "kiss_y_offset", 0);
                futa_saved_kiss_x_offset = ini_read_real("portrait", "kiss_x_offset", 0);
                futa_saved_boob_y_offset = ini_read_real("portrait", "boob_y_offset", 0);
                futa_saved_boob_x_offset = ini_read_real("portrait", "boob_x_offset", 0);
                futa_saved_headpat_y_offset = ini_read_real("portrait", "headpat_y_offset", 0);
                futa_saved_headpat_x_offset = ini_read_real("portrait", "headpat_x_offset", 0);
                if (portrait_number == 0)
                {
                    custom_kiss_y_offset = futa_saved_kiss_y_offset;
                    custom_kiss_x_offset = futa_saved_kiss_x_offset;
                    custom_boob_y_offset = futa_saved_boob_y_offset;
                    custom_boob_x_offset = futa_saved_boob_x_offset;
                    custom_headpat_y_offset = futa_saved_headpat_y_offset;
                    custom_headpat_x_offset = futa_saved_headpat_x_offset;
                }
                ini_close();
            }
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
            // One portrait per lover: drop BOTH portrait slots of the previous lover first. Before this, switching
            // from a standard-name lover to a modern one kept the old legacy portrait, which the draw code preferred.
            if (sprite_exists(custom_portrait) && custom_portrait > 189)
            {
                sprite_delete(custom_portrait);
            }
            custom_portrait = -1;
            if (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait > 189)
            {
                sprite_delete(legacy_custom_portrait);
            }
            legacy_custom_portrait = -1;
            custom_portrait_scale = 1;
            if (file_exists(f_port))
            {
                legacy_custom_portrait = sprite_add(f_port, func_portrait_frames(f_port, 10), false, false, portrait_origin_x, portrait_origin_y);
                if (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1)
                {
                    var _pw = sprite_get_width(legacy_custom_portrait);
                    if (_pw > 0)
                    {
                        custom_portrait_scale = 128 / _pw;
                    }
                }
            }
            if (variable_instance_exists(id, "custom_sperm_sprite") && sprite_exists(custom_sperm_sprite) && custom_sperm_sprite > 189)
            {
                sprite_delete(custom_sperm_sprite);
            }
            custom_sperm_sprite = -1;
            if (variable_instance_exists(id, "custom_sperm_big_sprite") && sprite_exists(custom_sperm_big_sprite) && custom_sperm_big_sprite > 189)
            {
                sprite_delete(custom_sperm_big_sprite);
            }
            custom_sperm_big_sprite = -1;
            var _f_sperm = string(arg0) + "/custom_futa_sperm.png";
            if (!file_exists(_f_sperm)) _f_sperm = string(arg0) + "/custom_sperm.png";
            if (file_exists(_f_sperm))
            {
                custom_sperm_sprite = sprite_add(_f_sperm, 4, false, false, 24, 24);
            }
            var _f_sperm_big = string(arg0) + "/custom_futa_sperm_big.png";
            if (!file_exists(_f_sperm_big)) _f_sperm_big = string(arg0) + "/custom_sperm_big.png";
            if (file_exists(_f_sperm_big))
            {
                custom_sperm_big_sprite = sprite_add(_f_sperm_big, 4, false, false, 24, 24);
            }

            f_mate = string(arg0) + "/custom_mating_press.png";
            // Native Deeproom 4.0.3: 9 frames at the [sprite] mating_press_origin, drawn unscaled.
            var _temp_mate = sprite_add(f_mate, 9, false, false, mp_origin_x, mp_origin_y);
            if (sprite_exists(_temp_mate) && _temp_mate != -1)
            {
                is_legacy_custom = true;
                if (sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press > 189)
                {
                    sprite_delete(legacy_custom_mating_press);
                }
                legacy_custom_mating_press = _temp_mate;
                custom_mating_press_scale = 1;
            }
            f_cow = string(arg0) + "/custom_reverse_cowgirl.png";
            if (file_exists(f_cow))
            {
                if (sprite_exists(legacy_custom_cowgirl))
                {
                    sprite_delete(legacy_custom_cowgirl);
                }
                var frames = 5;
                var temp_sprite = sprite_add(f_cow, 1, false, false, cowgirl_origin_x, cowgirl_origin_y);
                if (sprite_exists(temp_sprite) && temp_sprite != -1)
                {
                    if (sprite_get_width(temp_sprite) > (sprite_origin_x * 10))
                    {
                        frames = 7;
                    }
                    sprite_delete(temp_sprite);
                }
                legacy_custom_cowgirl = sprite_add(f_cow, frames, false, false, cowgirl_origin_x, cowgirl_origin_y);
            }
            f_xray = string(arg0) + "/custom_xray.png";
            if (file_exists(f_xray))
            {
                if (sprite_exists(legacy_custom_xray))
                {
                    sprite_delete(legacy_custom_xray);
                }
                var _lfm_fixed = false;
                var _lfm_ox = 80;
                var _lfm_oy = 84;
                if (file_exists(string(arg0) + "/custom_data.futa"))
                {
                    tc_ini_open_desc(string(arg0) + "/custom_data.futa");
                    // Origin measured from the strip by the patcher at build time (shaft on the penis line); used exactly.
                    _lfm_fixed = ini_key_exists("xray", "mobile_origin_x");
                    if (_lfm_fixed)
                    {
                        _lfm_ox = ini_read_real("xray", "mobile_origin_x", 80);
                        _lfm_oy = ini_read_real("xray", "mobile_origin_y", 84);
                    }
                    ini_close();
                }
                legacy_custom_xray = sprite_add(f_xray, 3, false, false, _lfm_ox, _lfm_oy);
                var _lfx_w = _lfm_fixed ? 160 : sprite_get_width(legacy_custom_xray);
                if (_lfx_w > 0 && _lfx_w != 160)
                {
                    var _lfx_sc = 160 / _lfx_w;
                    sprite_set_offset(legacy_custom_xray, 80 / _lfx_sc, 84 / _lfx_sc);
                }
                _lfx_w = _lfm_fixed ? 160 : sprite_get_width(legacy_custom_xray);
                if (_lfx_w > 0 && _lfx_w != 160)
                {
                    var _lfx_sc = 160 / _lfx_w;
                    sprite_set_offset(legacy_custom_xray, 80 / _lfx_sc, 84 / _lfx_sc);
                }
            }
            var f_xray_broken = string(arg0) + "/custom_xray_broken.png";
            if (file_exists(f_xray_broken))
            {
                if (sprite_exists(legacy_custom_xray_broken))
                {
                    sprite_delete(legacy_custom_xray_broken);
                }
                legacy_custom_xray_broken = sprite_add(f_xray_broken, 1, false, false, 80, 84);
            }
            var f_condom = string(arg0) + "/custom_condom.png";
            if (file_exists(f_condom))
            {
                if (sprite_exists(legacy_custom_condom))
                {
                    sprite_delete(legacy_custom_condom);
                }
                legacy_custom_condom = sprite_add(f_condom, 2, false, false, sprite_origin_x, sprite_origin_y);
            }
            var f_condom_broken = string(arg0) + "/custom_condom_broken.png";
            if (file_exists(f_condom_broken))
            {
                if (sprite_exists(custom_condom_broken))
                {
                    sprite_delete(custom_condom_broken);
                }
                custom_condom_broken = sprite_add(f_condom_broken, 2, false, false, sprite_origin_x, sprite_origin_y);
            }
            else
            {
                custom_condom_broken = -1;
            }
            f_deep = string(arg0) + "/custom_deepthroat.png";
            if (file_exists(f_deep))
            {
                if (sprite_exists(custom_deepthroat))
                {
                    sprite_delete(custom_deepthroat);
                }
                custom_deepthroat = sprite_add(f_deep, 9, false, false, dt_origin_x, dt_origin_y);
            }
            else
            {
                custom_deepthroat = -1;
            }
            if (custom_deepthroat == -1 && sex_position == 3)
            {
                sex_position = 0;
            }
            custom_default_moans = false;
            ds_list_clear(custom_moan_slow_list);
            ds_list_clear(custom_moan_fast_list);
            ds_list_clear(custom_orgasm_list);
            func_get_custom_audio(custom_moan_slow_list, string(arg0) + "/moan_slow");
            func_get_custom_audio(custom_moan_fast_list, string(arg0) + "/moan_fast");
            func_get_custom_audio(custom_orgasm_list, string(arg0) + "/orgasm");
            ds_list_clear(custom_insert_list);
            ds_list_clear(custom_pullout_list);
            ds_list_clear(custom_condom_break_list);
            func_get_custom_audio(custom_insert_list, string(arg0) + "/sfx/insert");
            func_get_custom_audio(custom_insert_list, string(arg0) + "/insert");
            func_get_custom_audio(custom_pullout_list, string(arg0) + "/sfx/pullout");
            func_get_custom_audio(custom_pullout_list, string(arg0) + "/pullout");
            func_get_custom_audio(custom_condom_break_list, string(arg0) + "/sfx/condom_break");
            func_get_custom_audio(custom_condom_break_list, string(arg0) + "/condom_break");
            custom_default_moans = true;
            moan_pitch = random_range(0.9, 1.1);
            ds_list_clear(moan_slow_list);
            ds_list_clear(moan_fast_list);
            ds_list_clear(orgasm_list);
            if (ds_list_size(custom_moan_slow_list) > 0)
            {
                ds_list_copy(moan_slow_list, custom_moan_slow_list);
            }
            if (ds_list_size(custom_moan_fast_list) > 0)
            {
                ds_list_copy(moan_fast_list, custom_moan_fast_list);
            }
            if (ds_list_size(custom_orgasm_list) > 0)
            {
                ds_list_copy(orgasm_list, custom_orgasm_list);
            }
            if (sprite_exists(legacy_bc_mating_press))
            {
                sprite_delete(legacy_bc_mating_press);
            }
            if (sprite_exists(legacy_bc_cowgirl))
            {
                sprite_delete(legacy_bc_cowgirl);
            }
            if (sprite_exists(legacy_bc_deepthroat))
            {
                sprite_delete(legacy_bc_deepthroat);
            }
            if (sprite_exists(legacy_bc_crest))
            {
                sprite_delete(legacy_bc_crest);
            }
            legacy_bc_mating_press = -1;
            legacy_bc_cowgirl = -1;
            legacy_bc_deepthroat = -1;
            legacy_bc_crest = -1;
            legacy_bc_loaded = false;
            var _lbc_path = string(arg0) + "/custom_BallClench.png";
            if (file_exists(_lbc_path))
            {
                legacy_bc_mating_press = sprite_add(_lbc_path, 5, false, false, 22, 0);
                if (sprite_get_width(legacy_bc_mating_press) > 100)
                {
                    sprite_delete(legacy_bc_mating_press);
                    legacy_bc_mating_press = sprite_add(_lbc_path, 6, false, false, 79, 112);
                }
                legacy_bc_cowgirl = sprite_add(_lbc_path, 5, false, false, 22, 0);
                if (sprite_get_width(legacy_bc_cowgirl) > 100)
                {
                    sprite_delete(legacy_bc_cowgirl);
                    legacy_bc_cowgirl = sprite_add(_lbc_path, 6, false, false, 79, 112);
                }
                legacy_bc_deepthroat = sprite_add(_lbc_path, 5, false, false, 22, 0);
                if (sprite_get_width(legacy_bc_deepthroat) > 100)
                {
                    sprite_delete(legacy_bc_deepthroat);
                    legacy_bc_deepthroat = sprite_add(_lbc_path, 6, false, false, 79, 112);
                }
                legacy_bc_loaded = true;
                var _lbc_crest_path = string(arg0) + "/custom_BallClenchCREST.png";
                if (file_exists(_lbc_crest_path))
                {
                    legacy_bc_crest = sprite_add(_lbc_crest_path, 5, false, false, 22, 0);
                    if (sprite_get_width(legacy_bc_crest) > 100)
                    {
                        sprite_delete(legacy_bc_crest);
                        legacy_bc_crest = sprite_add(_lbc_crest_path, 6, false, false, 79, 112);
                    }
                }
            }
            custom_futa_alt_max = 0;
            exit;
        }
        is_legacy_custom = false;  // 19-frame strip: loaded by the modern loader below, drawn as a modern lover
    }
    var sprite_origin_x = 80;
    var sprite_origin_y = 84;
    var cowgirl_origin_x = 80;
    var cowgirl_origin_y = 84;
    var portrait_origin_x = 64;
    var portrait_origin_y = 64;
    custom_cum_y_offset = 0;
    custom_cum_y_offset_mp = 0;
    custom_cum_y_offset_cg = 0;
    custom_cum_y_offset_dt = 0;
    custom_condom_offset_deepthroat = 0;
    custom_bc_mp_off_y = 0;
    custom_bc_cg_off_y = 0;
    custom_bc_rc_off_y = 0;
    custom_bc_dt_off_y = 0;
    custom_xray_offset_y = 0;
    custom_condom_offset_mpress = 0;
    custom_condom_offset_cowgirls = 0;
    comment = "memory bleed guard";
    custom_max_loads = 5;
    custom_top_boob_size = 1;
    custom_top_ass_size = 1;
    custom_top_penis_length = 1;
    custom_top_penis_width = 1;
    custom_ball_size = 1;
    custom_virility_modifier = 1;
    custom_cum_volume_modifier = 1;
    custom_stroke_depth = 1;
    custom_stroke_speed = 1;
    custom_pump_delay = 90;
    custom_mega_sperm_pill = false;
    custom_equine_pill = false;
    custom_knotted_pill = false;
    custom_extra_thick_pill = false;
    custom_diphallia_pill = false;
    custom_stamina_pill = false;
    custom_leaky_pill = false;
    custom_hyper_breeding_pill = false;
    custom_blockage_pill = false;
    custom_quickshot_pill = false;
    custom_reverse_speed_pill = false;
    custom_edge_addict_pill = false;
    custom_premature_pill = false;
    custom_edge_lover_pill = false;
    custom_growth_cascade_pill = false;
    custom_livestream_pill = false;
    custom_three_pump_champ_pill = false;
    custom_penis_type_index = 0;
    custom_condom_color = -1;
    custom_condom_color_set = false;
    custom_dialogue_set_top = -1;
    if (file_exists(string(arg0) + "/custom_data.futa"))
    {
        tc_ini_open_desc(string(arg0) + "/custom_data.futa");
        sprite_origin_x = ini_read_real("sprite", "origin_x", 80);
        sprite_origin_y = ini_read_real("sprite", "origin_y", 84);
        cowgirl_origin_x = ini_read_real("sprite", "cowgirl_origin_x", sprite_origin_x);
        cowgirl_origin_y = ini_read_real("sprite", "cowgirl_origin_y", sprite_origin_y);
        mp_origin_x = ini_read_real("sprite", "mating_press_origin_x", sprite_origin_x);
        mp_origin_y = ini_read_real("sprite", "mating_press_origin_y", sprite_origin_y);
        custom_futa_dt_y_offset = ini_read_real("sprite", "deepthroat_y_offset", 22);
        dt_origin_x = ini_read_real("sprite", "deepthroat_origin_x", sprite_origin_x);
        dt_origin_y = ini_read_real("sprite", "deepthroat_origin_y", sprite_origin_y);
        custom_xray_offset_y = ini_read_real("sprite", "xray_offset_y", 0);
        custom_cum_y_offset = ini_read_real("sprite", "cum_y_offset", 0);
        custom_cum_y_offset_mp = ini_read_real("CumPos", "mating_press_cum_offset", 0);
        custom_cum_y_offset_cg = ini_read_real("CumPos", "cg_and_rcg_cum_offset", 0);
        custom_cum_y_offset_dt = ini_read_real("CumPos", "deepthroat_cum_offset", 0);
        portrait_origin_x = ini_read_real("portrait", "origin_x", 64);
        portrait_origin_y = ini_read_real("portrait", "origin_y", 64);
        custom_condom_offset_mpress = ini_read_real("CondomPos", "condom_y_mpress", ini_read_real("condom", "condom_y_mpress", 0));
        custom_condom_offset_cowgirls = ini_read_real("CondomPos", "condom_y_cowgirls", ini_read_real("condom", "condom_y_cowgirls", 0));
        custom_condom_offset_deepthroat = ini_read_real("CondomPos", "deepthroat_condom_offset", 0);
        custom_max_loads = ini_read_real("stats", "max_orgasms", 5);
        custom_top_boob_size = ini_read_real("stats", "top_boob_size", 1);
        custom_top_ass_size = ini_read_real("stats", "top_ass_size", 1);
        custom_top_penis_length = ini_read_real("stats", "top_penis_length", 1);
        custom_top_penis_width = ini_read_real("stats", "top_penis_width", 1);
        custom_ball_size = ini_read_real("stats", "ball_size", 1);
        custom_virility_modifier = ini_read_real("stats", "virility_modifier", 1);
        custom_cum_volume_modifier = ini_read_real("stats", "cum_volume_modifier", 1);
        custom_stroke_depth = ini_read_real("stats", "stroke_depth", 1);
        custom_stroke_speed = ini_read_real("stats", "stroke_speed", 1);
        custom_pump_delay = clamp(ini_read_real("stats", "pump_delay", 90), 30, 360);
        custom_bc_mp_off_y = ini_read_real("BallClench", "bc_mp_off_y", 0);
        custom_bc_cg_off_y = ini_read_real("BallClench", "bc_cg_off_y", 0);
        custom_bc_rc_off_y = ini_read_real("BallClench", "bc_rc_off_y", 0);
        custom_bc_dt_off_y = ini_read_real("BallClench", "bc_dt_off_y", 0);
        var _cc_hex = ini_read_string("condom", "condom_color", "");
        if (_cc_hex != "")
        {
            if (string_char_at(_cc_hex, 1) == "#")
            {
                _cc_hex = string_copy(_cc_hex, 2, string_length(_cc_hex) - 1);
            }
            _cc_hex = string_upper(_cc_hex);
            var _hc = "0123456789ABCDEF";
            var _r = ((string_pos(string_char_at(_cc_hex, 1), _hc) - 1) * 16) + (string_pos(string_char_at(_cc_hex, 2), _hc) - 1);
            var _g = ((string_pos(string_char_at(_cc_hex, 3), _hc) - 1) * 16) + (string_pos(string_char_at(_cc_hex, 4), _hc) - 1);
            var _b = ((string_pos(string_char_at(_cc_hex, 5), _hc) - 1) * 16) + (string_pos(string_char_at(_cc_hex, 6), _hc) - 1);
            custom_condom_color = make_color_rgb(_r, _g, _b);
            custom_condom_color_set = true;
        }
        else
        {
            custom_condom_color = -1;
            custom_condom_color_set = false;
        }
        custom_mega_sperm_pill = bool(ini_read_real("pills", "mega_sperm_pill", 0));
        custom_equine_pill = bool(ini_read_real("pills", "equine_pill", 0));
        custom_knotted_pill = bool(ini_read_real("pills", "knotted_pill", 0));
        custom_extra_thick_pill = bool(ini_read_real("pills", "extra_thick_pill", 0));
        custom_diphallia_pill = bool(ini_read_real("pills", "diphallia_pill", 0));
        custom_stamina_pill = bool(ini_read_real("pills", "stamina_pill", 0));
        custom_leaky_pill = bool(ini_read_real("pills", "leaky_pill", 0));
        custom_hyper_breeding_pill = bool(ini_read_real("pills", "hyper_breeding_pill", 0));
        custom_blockage_pill = bool(ini_read_real("pills", "blockage_pill", 0));
        custom_quickshot_pill = bool(ini_read_real("pills", "quickshot_pill", 0));
        custom_reverse_speed_pill = bool(ini_read_real("pills", "reverse_speed_pill", 0));
        custom_edge_addict_pill = bool(ini_read_real("pills", "edge_addicted_pill", 0));
        custom_pound_town_pill = bool(ini_read_real("pills", "pound_town_pill", 0));
        custom_premature_pill = bool(ini_read_real("pills", "premature_pill", 0));
        custom_edge_lover_pill = bool(ini_read_real("pills", "edge_lover_pill", 0));
        custom_growth_cascade_pill = bool(ini_read_real("pills", "growth_cascade_pill", 0));
        custom_livestream_pill = bool(ini_read_real("pills", "livestream_pill", 0));
        custom_three_pump_champ_pill = bool(ini_read_real("pills", "three_pump_champ_pill", 0));
        custom_penis_type_index = ini_read_real("penis", "penis_type_index", 0);
        sex_progress_max = ini_read_real("stats", "stamina", sex_progress_max);
        user_pumps_max = ini_read_real("stats", "max_pumps", user_pumps_max);
        cum_shot_mult = ini_read_real("stats", "cumshot_mult", cum_shot_mult);
        rand_pump_delay_min = ini_read_real("stats", "pump_delay_min", rand_pump_delay_min);
        rand_pump_delay_max = ini_read_real("stats", "pump_delay_max", rand_pump_delay_max);
        condom_color = func_hex_to_color(ini_read_string("colors", "condom", ""), condom_color);
        cum_color = func_hex_to_color(ini_read_string("colors", "cum", ""), cum_color);
        if (arg1 > 0)
        {
            var _alt_sec = "stats_alt_" + string(arg1);
            sex_progress_max = ini_read_real(_alt_sec, "stamina", sex_progress_max);
            user_pumps_max = ini_read_real(_alt_sec, "max_pumps", user_pumps_max);
            cum_shot_mult = ini_read_real(_alt_sec, "cumshot_mult", cum_shot_mult);
            rand_pump_delay_min = ini_read_real(_alt_sec, "pump_delay_min", rand_pump_delay_min);
            rand_pump_delay_max = ini_read_real(_alt_sec, "pump_delay_max", rand_pump_delay_max);
            condom_color = func_hex_to_color(ini_read_string(_alt_sec, "condom", ""), condom_color);
            cum_color = func_hex_to_color(ini_read_string(_alt_sec, "cum", ""), cum_color);
            custom_max_loads = ini_read_real(_alt_sec, "max_orgasms", custom_max_loads);
            custom_top_boob_size = ini_read_real(_alt_sec, "top_boob_size", custom_top_boob_size);
            custom_top_ass_size = ini_read_real(_alt_sec, "top_ass_size", custom_top_ass_size);
            custom_top_penis_length = ini_read_real(_alt_sec, "top_penis_length", custom_top_penis_length);
            custom_top_penis_width = ini_read_real(_alt_sec, "top_penis_width", custom_top_penis_width);
            custom_ball_size = ini_read_real(_alt_sec, "ball_size", custom_ball_size);
            custom_virility_modifier = ini_read_real(_alt_sec, "virility_modifier", custom_virility_modifier);
            custom_cum_volume_modifier = ini_read_real(_alt_sec, "cum_volume_modifier", custom_cum_volume_modifier);
            custom_stroke_depth = ini_read_real(_alt_sec, "stroke_depth", custom_stroke_depth);
            custom_stroke_speed = ini_read_real(_alt_sec, "stroke_speed", custom_stroke_speed);
            custom_pump_delay = clamp(ini_read_real(_alt_sec, "pump_delay", custom_pump_delay), 30, 360);
            custom_bc_mp_off_y = ini_read_real("BallClench", "bc_mp_off_y", 0);
            custom_bc_cg_off_y = ini_read_real("BallClench", "bc_cg_off_y", 0);
            custom_bc_rc_off_y = ini_read_real("BallClench", "bc_rc_off_y", 0);
            custom_bc_dt_off_y = ini_read_real("BallClench", "bc_dt_off_y", 0);
        }
        custom_dialogue_set_top = {};
        var _top_keys = ["intro", "intro_return", "sex_start", "sex_continue", "sex_halfway", "sex_exhausted", "sex_orgasm", "sex_after", "cleanup", "kiss", "condom_on", "condom_off", "condom_broken", "condom_remove", "condom_break", "pullout", "headpat", "spank", "touch_boobs", "moan", "mystery_effect", "sex_encorgasm"];
        for (var _i = 0; _i < array_length(_top_keys); _i += 1)
        {
            var _key = _top_keys[_i];
            var _result = func_check_custom_dialogue(_key, false);
            if (array_length(_result) > 0)
            {
                variable_struct_set(custom_dialogue_set_top, _key, _result);
            }
        }
        if (variable_struct_names_count(custom_dialogue_set_top) == 0)
        {
            custom_dialogue_set_top = -1;
        }
        futa_saved_kiss_y_offset = ini_read_real("portrait", "kiss_y_offset", 0);
        futa_saved_kiss_x_offset = ini_read_real("portrait", "kiss_x_offset", 0);
        futa_saved_boob_y_offset = ini_read_real("portrait", "boob_y_offset", 0);
        futa_saved_boob_x_offset = ini_read_real("portrait", "boob_x_offset", 0);
        futa_saved_headpat_y_offset = ini_read_real("portrait", "headpat_y_offset", 0);
        futa_saved_headpat_x_offset = ini_read_real("portrait", "headpat_x_offset", 0);
        if (portrait_number == 0)
        {
            custom_kiss_y_offset = futa_saved_kiss_y_offset;
            custom_kiss_x_offset = futa_saved_kiss_x_offset;
            custom_boob_y_offset = futa_saved_boob_y_offset;
            custom_boob_x_offset = futa_saved_boob_x_offset;
            custom_headpat_y_offset = futa_saved_headpat_y_offset;
            custom_headpat_x_offset = futa_saved_headpat_x_offset;
        }
        ini_close();
    }
    var _suffix = (arg1 == 0) ? "_0.png" : ("_alt_" + string(arg1) + ".png");
    var f_port = string(arg0) + "/custom_futa_portrait" + _suffix;
    if (!file_exists(f_port))
    {
        f_port = string(arg0) + "/custom_futa_portrait_0.png";  // alt variant without its own portrait
    }
    // One portrait per lover: drop BOTH portrait slots of the previous lover first. Before this, switching
    // from a standard-name lover to a modern one kept the old legacy portrait, which the draw code preferred.
    if (sprite_exists(custom_portrait) && custom_portrait > 189)
    {
        sprite_delete(custom_portrait);
    }
    custom_portrait = -1;
    if (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait > 189)
    {
        sprite_delete(legacy_custom_portrait);
    }
    legacy_custom_portrait = -1;
    custom_portrait_scale = 1;
    if (file_exists(f_port))
    {
        custom_portrait = sprite_add(f_port, func_portrait_frames(f_port, 17), false, false, portrait_origin_x, portrait_origin_y);
        if (sprite_exists(custom_portrait) && custom_portrait != -1 && sprite_get_width(custom_portrait) > 0)
        {
            custom_portrait_scale = 128 / sprite_get_width(custom_portrait);
        }
    }
    var f_mate = string(arg0) + "/custom_futa_mating_press" + _suffix;
    if (file_exists(f_mate))
    {
        if (sprite_exists(custom_mating_press))
        {
            sprite_delete(custom_mating_press);
        }
        custom_mating_press = sprite_add(f_mate, 24, false, false, mp_origin_x, mp_origin_y);
    }
    var f_cow = string(arg0) + "/custom_futa_cowgirls" + _suffix;
    if (file_exists(f_cow))
    {
        if (sprite_exists(custom_cowgirl))
        {
            sprite_delete(custom_cowgirl);
        }
        custom_cowgirl = sprite_add(f_cow, 19, false, false, cowgirl_origin_x, cowgirl_origin_y);
    }
    var f_xray = string(arg0) + "/custom_futa_xray" + _suffix;
    if (file_exists(f_xray))
    {
        if (sprite_exists(custom_xray))
        {
            sprite_delete(custom_xray);
        }
        var _cfm_fixed = false;
        var _cfm_ox = 80;
        var _cfm_oy = (custom_xray_offset_y > 0) ? (84 - custom_xray_offset_y) : (84 + custom_xray_offset_y);
        if (file_exists(string(arg0) + "/custom_data.futa"))
        {
            tc_ini_open_desc(string(arg0) + "/custom_data.futa");
            // Origin measured from the strip by the patcher at build time (shaft on the penis line); used exactly.
            _cfm_fixed = ini_key_exists("xray", "mobile_origin_x");
            if (_cfm_fixed)
            {
                _cfm_ox = ini_read_real("xray", "mobile_origin_x", 80);
                _cfm_oy = ini_read_real("xray", "mobile_origin_y", 84);
            }
            ini_close();
        }
        custom_xray = sprite_add(f_xray, 18, false, false, _cfm_ox, _cfm_oy);
        var _px_w = _cfm_fixed ? 160 : sprite_get_width(custom_xray);
        if (_px_w > 0 && _px_w != 160)
        {
            var _px_sc = 160 / _px_w;
            var _px_yoff = (custom_xray_offset_y > 0) ? (84 - custom_xray_offset_y) : (84 + custom_xray_offset_y);
            sprite_set_offset(custom_xray, 80 / _px_sc, _px_yoff / _px_sc);
        }
        _px_w = _cfm_fixed ? 160 : sprite_get_width(custom_xray);
        if (_px_w > 0 && _px_w != 160)
        {
            var _px_sc = 160 / _px_w;
            var _px_yoff = (custom_xray_offset_y > 0) ? (84 - custom_xray_offset_y) : (84 + custom_xray_offset_y);
            sprite_set_offset(custom_xray, 80 / _px_sc, _px_yoff / _px_sc);
        }
    }
    var f_condom_14 = string(arg0) + "/custom_condom.png";
    if (file_exists(f_condom_14))
    {
        if (sprite_exists(custom_condom))
        {
            sprite_delete(custom_condom);
        }
        custom_condom = sprite_add(f_condom_14, 2, false, false, sprite_origin_x, sprite_origin_y);
    }
    else
    {
        custom_condom = -1;
    }
    var f_condom_broken_14 = string(arg0) + "/custom_condom_broken.png";
    if (file_exists(f_condom_broken_14))
    {
        if (sprite_exists(custom_condom_broken))
        {
            sprite_delete(custom_condom_broken);
        }
        custom_condom_broken = sprite_add(f_condom_broken_14, 2, false, false, sprite_origin_x, sprite_origin_y);
    }
    else
    {
        custom_condom_broken = -1;
    }
    var f_futa_dt = string(arg0) + "/custom_futa_deepthroat" + _suffix;
    if (file_exists(f_futa_dt))
    {
        if (sprite_exists(custom_futa_deepthroat))
        {
            sprite_delete(custom_futa_deepthroat);
        }
        custom_futa_deepthroat = sprite_add(f_futa_dt, 24, false, false, mp_origin_x, mp_origin_y);
    }
    else
    {
        if (sprite_exists(custom_futa_deepthroat))
        {
            sprite_delete(custom_futa_deepthroat);
        }
        custom_futa_deepthroat = -1;
    }
    if (custom_futa_deepthroat == -1 && sex_position == 3)
    {
        sex_position = 0;
    }
    comment = "Count how many alts exist so the menu knows where to stop";
    custom_futa_alt_max = 0;
    while (file_exists(string(arg0) + "/custom_futa_mating_press_alt_" + string(custom_futa_alt_max + 1) + ".png"))
    {
        custom_futa_alt_max++;
    }
    var f_deep = string(arg0) + "/custom_deepthroat.png";
    if (file_exists(f_deep))
    {
        if (sprite_exists(custom_deepthroat))
        {
            sprite_delete(custom_deepthroat);
        }
        custom_deepthroat = sprite_add(f_deep, 9, false, false, dt_origin_x, dt_origin_y);
    }
    else
    {
        if (sprite_exists(custom_deepthroat))
        {
            sprite_delete(custom_deepthroat);
        }
        custom_deepthroat = -1;
    }
    if (custom_deepthroat == -1 && sex_position == 3)
    {
        sex_position = 0;
    }
    custom_default_moans = false;
    ds_list_clear(custom_moan_slow_list);
    ds_list_clear(custom_moan_fast_list);
    ds_list_clear(custom_orgasm_list);
    func_get_custom_audio(custom_moan_slow_list, string(arg0) + "/moan_slow");
    func_get_custom_audio(custom_moan_fast_list, string(arg0) + "/moan_fast");
    func_get_custom_audio(custom_orgasm_list, string(arg0) + "/orgasm");
    moan_pitch = random_range(0.9, 1.1);
    ds_list_clear(moan_slow_list);
    ds_list_clear(moan_fast_list);
    ds_list_clear(orgasm_list);
    if (ds_list_size(custom_moan_slow_list) > 0)
    {
        ds_list_copy(moan_slow_list, custom_moan_slow_list);
    }
    if (ds_list_size(custom_moan_fast_list) > 0)
    {
        ds_list_copy(moan_fast_list, custom_moan_fast_list);
    }
    if (ds_list_size(custom_orgasm_list) > 0)
    {
        ds_list_copy(orgasm_list, custom_orgasm_list);
    }
    comment = "clean up any previously loaded bc sprites";
    if (sprite_exists(custom_bc_mating_press))
    {
        sprite_delete(custom_bc_mating_press);
    }
    if (sprite_exists(custom_bc_cowgirl))
    {
        sprite_delete(custom_bc_cowgirl);
    }
    custom_bc_mating_press = -1;
    custom_bc_cowgirl = -1;
    custom_bc_loaded = false;
    var _bc_alt_suffix = (arg1 == 0) ? "_0" : ("_alt_" + string(arg1));
    var _bc_alt_shared = (arg1 == 0) ? "" : ("_ALT_" + string(arg1));
    var _bc_mp_specific = string(arg0) + "/custom_futa_mating_press" + _bc_alt_suffix + "_BC.png";
    var _bc_cg_specific = string(arg0) + "/custom_futa_cowgirls" + _bc_alt_suffix + "_BC.png";
    var _bc_shared = string(arg0) + "/custom_futa_BC" + _bc_alt_shared + ".png";
    if (file_exists(_bc_mp_specific))
    {
        custom_bc_mating_press = sprite_add(_bc_mp_specific, 5, false, false, 22, 0);
        if (sprite_get_width(custom_bc_mating_press) > 100)
        {
            sprite_delete(custom_bc_mating_press);
            custom_bc_mating_press = sprite_add(_bc_mp_specific, 6, false, false, 79, 112);
        }
    }
    else if (file_exists(_bc_shared))
    {
        custom_bc_mating_press = sprite_add(_bc_shared, 5, false, false, 22, 0);
        if (sprite_get_width(custom_bc_mating_press) > 100)
        {
            sprite_delete(custom_bc_mating_press);
            custom_bc_mating_press = sprite_add(_bc_shared, 6, false, false, 79, 112);
        }
    }
    if (file_exists(_bc_cg_specific))
    {
        custom_bc_cowgirl = sprite_add(_bc_cg_specific, 5, false, false, 22, 0);
        if (sprite_get_width(custom_bc_cowgirl) > 100)
        {
            sprite_delete(custom_bc_cowgirl);
            custom_bc_cowgirl = sprite_add(_bc_cg_specific, 6, false, false, 79, 112);
        }
    }
    else if (file_exists(_bc_shared))
    {
        custom_bc_cowgirl = sprite_add(_bc_shared, 5, false, false, 22, 0);
        if (sprite_get_width(custom_bc_cowgirl) > 100)
        {
            sprite_delete(custom_bc_cowgirl);
            custom_bc_cowgirl = sprite_add(_bc_shared, 6, false, false, 79, 112);
        }
    }
    if (sprite_exists(custom_bc_crest))
    {
        sprite_delete(custom_bc_crest);
    }
    custom_bc_crest = -1;
    var _bc_crest_path = string(arg0) + "/custom_futa_BCCREST" + _bc_alt_shared + ".png";
    if (file_exists(_bc_crest_path))
    {
        custom_bc_crest = sprite_add(_bc_crest_path, 6, false, false, 79, 112);
    }
    if (sprite_exists(custom_bc_crest_mp))
    {
        sprite_delete(custom_bc_crest_mp);
    }
    custom_bc_crest_mp = -1;
    var _bc_crest_mp_path = string(arg0) + "/custom_futa_mating_press" + _bc_alt_suffix + "_BCCREST.png";
    if (file_exists(_bc_crest_mp_path))
    {
        custom_bc_crest_mp = sprite_add(_bc_crest_mp_path, 6, false, false, 79, 112);
    }
    if (sprite_exists(custom_bc_crest_cg))
    {
        sprite_delete(custom_bc_crest_cg);
    }
    custom_bc_crest_cg = -1;
    var _bc_crest_cg_path = string(arg0) + "/custom_futa_cowgirls" + _bc_alt_suffix + "_BCCREST.png";
    if (file_exists(_bc_crest_cg_path))
    {
        custom_bc_crest_cg = sprite_add(_bc_crest_cg_path, 6, false, false, 79, 112);
    }
    if (sprite_exists(custom_bc_crest_dt))
    {
        sprite_delete(custom_bc_crest_dt);
    }
    custom_bc_crest_dt = -1;
    var _bc_crest_dt_path = string(arg0) + "/custom_futa_deepthroat" + _bc_alt_suffix + "_BCCREST.png";
    if (file_exists(_bc_crest_dt_path))
    {
        custom_bc_crest_dt = sprite_add(_bc_crest_dt_path, 6, false, false, 79, 112);
    }
    if (sprite_exists(custom_bc_mating_press) || sprite_exists(custom_bc_cowgirl))
    {
        custom_bc_loaded = true;
    }
    if (sprite_exists(custom_sperm_sprite))
    {
        sprite_delete(custom_sperm_sprite);
    }
    custom_sperm_sprite = -1;
    if (sprite_exists(custom_sperm_big_sprite))
    {
        sprite_delete(custom_sperm_big_sprite);
    }
    custom_sperm_big_sprite = -1;
    var _f_sperm = string(arg0) + "/custom_futa_sperm.png";
    var _f_sperm_big = string(arg0) + "/custom_futa_sperm_big.png";
    if (file_exists(_f_sperm))
    {
        custom_sperm_sprite = sprite_add(_f_sperm, 4, false, false, 24, 24);
    }
    if (file_exists(_f_sperm_big))
    {
        custom_sperm_big_sprite = sprite_add(_f_sperm_big, 4, false, false, 24, 24);
    }
    custom_sprite_loaded = true;
}

randomize();
comment = "probably need to adjust this to suit the larger sizes the modded version tends to have";

function func_get_rating(arg0)
{
    var rating_numb = 1;
    if (arg0 >= 0.9)
    {
        rating_numb = 2;
    }
    if (arg0 >= 1)
    {
        rating_numb = 3;
    }
    if (arg0 >= 1.1)
    {
        rating_numb = 4;
    }
    if (arg0 >= 1.2)
    {
        rating_numb = 5;
    }
    if (arg0 >= 1.3)
    {
        rating_numb = 6;
    }
    return rating_numb;
}

function func_get_futa_frame(arg0, arg1)
{
    var _part = arg0;
    var _pos = arg1;
    if (top_sprite == legacy_custom_mating_press)
    {
        if (_pos == 0)
        {
            switch (_part)
            {
                case "boobs":
                    comment = "boobs";
                    return 0;
                case "head":
                    comment = "head";
                    return 1;
                case "back":
                    comment = "back";
                    return 2;
                case "hair":
                    comment = "hair";
                    return 3;
                case "thighs":
                    comment = "thighs";
                    return 4;
                case "feet":
                    comment = "feet";
                    return 5;
                case "butt":
                    comment = "butt";
                    return 6;
                case "balls":
                    comment = "balls";
                    return 8;
                case "crest":
                    comment = "balls crest";
                    return -1;
                case "tail":
                    comment = "tail";
                    return -1;
                case "wings":
                    comment = "wings";
                    return -1;
                case "pussy":
                    comment = "pussy";
                    return -1;
                case "shaft":
                    comment = "layer 1 (base/sheath)";
                    if (penis_type_index == 0)
                    {
                        comment = "human shaft";
                        return 7;
                    }
                    if (penis_type_index == 1)
                    {
                        comment = "horse sheath";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis full";
                        return -1;
                    }
                    if (penis_type_index == 3)
                    {
                        comment = "knotted horse full";
                        return -1;
                    }
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
                    comment = "condom";
                    if (penis_type_index == 0)
                    {
                        comment = "human condom";
                        return 0;
                    }
                    if (penis_type_index == 1 || penis_type_index == 3)
                    {
                        comment = "horse/knotted horse condom";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis condom";
                        return -1;
                    }
                    return 0;
                case "broken":
                    comment = "broken condom";
                    if (penis_type_index == 0)
                    {
                        comment = "human broken condom";
                        return -1;
                    }
                    if (penis_type_index == 1 || penis_type_index == 3)
                    {
                        comment = "horse/knotted horse broken condom";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis broken condom";
                        return -1;
                    }
                    return -1;
            }
        }
        if (_pos == 1)
        {
            switch (_part)
            {
                case "boobs":
                    comment = "boobs/torso";
                    return 0;
                case "butt":
                    comment = "ass and legs";
                    return 1;
                case "balls":
                    comment = "balls";
                    return 3;
                case "crest":
                    comment = "balls crest";
                    return -1;
                case "hands":
                    comment = "hands";
                    var temp_hands_id = 4;
                    if (sprite_get_number(legacy_custom_cowgirl) > 6)
                    {
                        temp_hands_id = 6;
                    }
                    return temp_hands_id;
                case "shaft":
                    comment = "layer 1 (base/sheath)";
                    if (penis_type_index == 0)
                    {
                        comment = "human shaft";
                        return 2;
                    }
                    if (penis_type_index == 1)
                    {
                        comment = "horse sheath";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis";
                        return -1;
                    }
                    if (penis_type_index == 3)
                    {
                        comment = "knotted horse shaft";
                        return -1;
                    }
                    return 2;
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
                        comment = "no 2nd layer";
                        return -1;
                    }
                    if (penis_type_index == 3)
                    {
                        comment = "knotted horse has no 2nd layer";
                        return -1;
                    }
                    return -1;
                case "condom":
                    comment = "condom";
                    if (penis_type_index == 0)
                    {
                        comment = "human condom";
                        return 1;
                    }
                    if (penis_type_index == 1 || penis_type_index == 3)
                    {
                        comment = "horse/knotted horse condom";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis condom";
                        return -1;
                    }
                    return 1;
                case "broken":
                    comment = "broken condom";
                    if (penis_type_index == 0)
                    {
                        comment = "human broken condom";
                        return -1;
                    }
                    if (penis_type_index == 1 || penis_type_index == 3)
                    {
                        comment = "horse/knotted horse broken condom";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis broken condom";
                        return -1;
                    }
                    return -1;
            }
        }
        if (_pos == 2)
        {
            switch (_part)
            {
                case "boobs":
                    comment = "boobs/torso";
                    return 0;
                case "butt":
                    comment = "ass and legs";
                    return 1;
                case "balls":
                    comment = "balls";
                    return 3;
                case "crest":
                    comment = "balls crest";
                    return -1;
                case "hands":
                    comment = "hands";
                    var temp_hands_id = 4;
                    if (sprite_get_number(legacy_custom_cowgirl) > 6)
                    {
                        temp_hands_id = 6;
                    }
                    return temp_hands_id;
                case "shaft":
                    comment = "layer 1 (base/sheath)";
                    if (penis_type_index == 0)
                    {
                        comment = "human shaft";
                        return 2;
                    }
                    if (penis_type_index == 1)
                    {
                        comment = "horse sheath";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis";
                        return -1;
                    }
                    if (penis_type_index == 3)
                    {
                        comment = "knotted horse shaft";
                        return -1;
                    }
                    return 2;
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
                        comment = "no 2nd layer";
                        return -1;
                    }
                    if (penis_type_index == 3)
                    {
                        comment = "knotted horse has no 2nd layer";
                        return -1;
                    }
                    return -1;
                case "condom":
                    comment = "condom";
                    if (penis_type_index == 0)
                    {
                        comment = "human condom";
                        return 1;
                    }
                    if (penis_type_index == 1 || penis_type_index == 3)
                    {
                        comment = "horse/knotted horse condom";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis condom";
                        return -1;
                    }
                    return 1;
                case "broken":
                    comment = "broken condom";
                    if (penis_type_index == 0)
                    {
                        comment = "human broken condom";
                        return -1;
                    }
                    if (penis_type_index == 1 || penis_type_index == 3)
                    {
                        comment = "horse/knotted horse broken condom";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis broken condom";
                        return -1;
                    }
                    return -1;
            }
        }
        return 0;
    }
    if (top_sprite != custom_mating_press)
    {
        switch (_part)
        {
            case "shaft":
                comment = "vanilla shaft";
                return 7;
            case "glans":
                comment = "vanilla glans";
                return 12;
            case "balls":
                comment = "vanilla balls";
                return 8;
            case "pussy":
                comment = "vanilla pussy";
                return 13;
            case "crest":
                comment = "vanilla crest";
                return 9;
            default:
                comment = "default fallback";
                return 0;
        }
    }
    if (_pos == 0)
    {
        switch (_part)
        {
            case "boobs":
                comment = "boobs";
                return 0;
            case "head":
                comment = "head";
                return 1;
            case "back":
                comment = "back";
                return 2;
            case "hair":
                comment = "hair";
                return 3;
            case "thighs":
                comment = "thighs";
                return 4;
            case "feet":
                comment = "feet";
                return 5;
            case "butt":
                comment = "butt";
                return 6;
            case "balls":
                comment = "balls";
                return 19;
            case "crest":
                comment = "balls crest";
                return 20;
            case "tail":
                comment = "tail";
                return 21;
            case "wings":
                comment = "wings";
                return 22;
            case "pussy":
                comment = "pussy";
                return 23;
            case "shaft":
                comment = "layer 1 (base/sheath)";
                if (penis_type_index == 0)
                {
                    comment = "human shaft";
                    return 7;
                }
                if (penis_type_index == 1)
                {
                    comment = "horse sheath";
                    return 11;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis full";
                    return 15;
                }
                if (penis_type_index == 3)
                {
                    comment = "knotted horse full";
                    return 18;
                }
                return 7;
            case "glans":
                comment = "layer 2 (tip/extension)";
                if (penis_type_index == 0)
                {
                    comment = "human glans";
                    return 8;
                }
                if (penis_type_index == 1)
                {
                    comment = "horse shaft";
                    return 12;
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
                comment = "condom";
                if (penis_type_index == 0)
                {
                    comment = "human condom";
                    return 9;
                }
                if (penis_type_index == 1 || penis_type_index == 3)
                {
                    comment = "horse/knotted horse condom";
                    return 13;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis condom";
                    return 16;
                }
                return 9;
            case "broken":
                comment = "broken condom";
                if (penis_type_index == 0)
                {
                    comment = "human broken condom";
                    return 10;
                }
                if (penis_type_index == 1 || penis_type_index == 3)
                {
                    comment = "horse/knotted horse broken condom";
                    return 14;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis broken condom";
                    return 17;
                }
                return 10;
        }
    }
    if (_pos == 1)
    {
        switch (_part)
        {
            case "boobs":
                comment = "boobs/torso";
                return 0;
            case "butt":
                comment = "ass and legs";
                return 1;
            case "balls":
                comment = "balls";
                return 14;
            case "crest":
                comment = "balls crest";
                return 18;
            case "hands":
                comment = "hands";
                return 17;
            case "shaft":
                comment = "layer 1 (base/sheath)";
                if (penis_type_index == 0)
                {
                    comment = "human shaft";
                    return 2;
                }
                if (penis_type_index == 1)
                {
                    comment = "horse sheath";
                    return 6;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis";
                    return 10;
                }
                if (penis_type_index == 3)
                {
                    comment = "knotted horse shaft";
                    return 13;
                }
                return 2;
            case "glans":
                comment = "layer 2 (tip/extension)";
                if (penis_type_index == 0)
                {
                    comment = "human glans";
                    return 3;
                }
                if (penis_type_index == 1)
                {
                    comment = "horse shaft";
                    return 7;
                }
                if (penis_type_index == 2)
                {
                    comment = "no 2nd layer";
                    return -1;
                }
                if (penis_type_index == 3)
                {
                    comment = "knotted horse has no 2nd layer";
                    return -1;
                }
                return -1;
            case "condom":
                comment = "condom";
                if (penis_type_index == 0)
                {
                    comment = "human condom";
                    return 4;
                }
                if (penis_type_index == 1 || penis_type_index == 3)
                {
                    comment = "horse/knotted horse condom";
                    return 8;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis condom";
                    return 11;
                }
                return 4;
            case "broken":
                comment = "broken condom";
                if (penis_type_index == 0)
                {
                    comment = "human broken condom";
                    return 5;
                }
                if (penis_type_index == 1 || penis_type_index == 3)
                {
                    comment = "horse/knotted horse broken condom";
                    return 9;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis broken condom";
                    return 12;
                }
                return 5;
        }
    }
    if (_pos == 2)
    {
        switch (_part)
        {
            case "shaft":
                comment = "layer 1 (base/sheath)";
                if (penis_type_index == 0)
                {
                    comment = "human shaft";
                    return 0;
                }
                if (penis_type_index == 1)
                {
                    comment = "horse sheath";
                    return 7;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted shaft";
                    return 10;
                }
                if (penis_type_index == 3)
                {
                    comment = "knotted horse shaft";
                    return 15;
                }
                return 0;
            case "urethra":
                comment = "urethra";
                if (penis_type_index == 0)
                {
                    comment = "human urethra";
                    return 1;
                }
                if (penis_type_index == 1)
                {
                    comment = "horse urethra";
                    return 6;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted urethra";
                    return 12;
                }
                if (penis_type_index == 3)
                {
                    comment = "knotted horse urethra";
                    return 17;
                }
                return 1;
            case "glans":
                comment = "layer 2 (tip/extension)";
                if (penis_type_index == 0)
                {
                    comment = "human glans";
                    return 2;
                }
                if (penis_type_index == 1)
                {
                    comment = "horse shaft";
                    return 5;
                }
                if (penis_type_index == 2)
                {
                    comment = "no 2nd layer";
                    return -1;
                }
                if (penis_type_index == 3)
                {
                    comment = "no 2nd layer";
                    return -1;
                }
                return -1;
            case "knot":
                comment = "x-ray specific knot drawing";
                if (penis_type_index == 2)
                {
                    comment = "knotted penis knot";
                    return 11;
                }
                if (penis_type_index == 3)
                {
                    comment = "knotted horse knot";
                    return 16;
                }
                return -1;
            case "condom":
                comment = "condom";
                if (penis_type_index == 0)
                {
                    comment = "human condom";
                    return 3;
                }
                if (penis_type_index == 1 || penis_type_index == 3)
                {
                    comment = "horse/knotted horse condom";
                    return 8;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis condom";
                    return 13;
                }
                return 3;
            case "broken":
                comment = "broken condom";
                if (penis_type_index == 0)
                {
                    comment = "human broken condom";
                    return 4;
                }
                if (penis_type_index == 1 || penis_type_index == 3)
                {
                    comment = "horse/knotted horse broken condom";
                    return 9;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis broken condom";
                    return 14;
                }
                return 4;
        }
    }
    return 0;
}

function func_randomize_top(arg0 = -1, arg1 = -1)
{
    var temp_color = -1;
    for (var i = 0; i < 5; i++)
    {
        temp_color[i] = make_color_hsv(30, 0, min(255, 100 + (50 * i) + random_range(-25, 25)));
    }
    breeding_words = ["FERTILIZED", "BRED", "IMPREGNATED", "LOVE MADE", "BUN IN THE OVEN", "KNOCKED UP", "SEEDED", "SOWN", "SPECIAL DELIVERY"];
    breeding_words_2 = ["DOUBLE FERTILIZED", "DOUBLE BRED", "DOUBLE IMPREGNATED", "TWINS", "TWO BUNS IN THE OVEN", "TWO'S COMPANY", "KNOCK-KNOCKED UP", "DOUBLE SEEDED", "DOUBLE SOWN", "DOUBLE BOOKED"];
    breeding_words_3 = ["TRIPLE FERTILIZED", "TRIPLE BRED", "TRIPLE IMPREGNATED", "TRIPLETS", "THREE BUNS IN THE OVEN", "THREE'S A CROWD", "TRIPLE SEEDED", "TRIPLE SOWN", "TRIPLE BOOKED"];
    breeding_words_8 = ["OCTOMOM"];
    breeding_words_11 = ["IT'S RIDICULOUS, IT'S NOT EVEN FUNNY"];
    breeding_words_13 = ["BAKER'S DOZEN"];
    breeding_milestone_text = ["GROWING FAMILY", "BROODMOTHER", "ALL-STAR BREEDER", "BABY FACTORY", "OVERSTUFFED WOMB", "PUTS RABBITS TO SHAME", "POPULATION BOOM", "MATERNITY WARD", "STORK'S WORST NIGHTMARE", "IT MAKES A VILLAGE", "EMPRESS OF MOTHERHOOD", "DAYCARE INDUSTRIAL COMPLEX", "DEMOGRAPHIC SHIFTER", "SPECIES SAVIOUR", "REPOPULATION SINGULARITY", "UNIVERSAL ANCESTOR", "PLANETARY COLONIZER", "SAIYAN SOVERIGN: THE LEGENDARY SUPER SLUT"];
    plapping_climax_words = ["WELL-FUCKED", "AHEGAO", "EYES ROLLED BACK", "CLIMAXED", "PLEASURED", "GIVEN IN", "FUCKED SILLY", "SURRENDERED", "SQUIRTED", "CROSS-EYED", "HEART PUPILS", "LET GO", "REDUCED TO JELLY", "WRECKED", "UTTERLY SATISFIED", "BLISS-BROKEN"];
    rare_plapping_climax_words = ["SAW GOD", "VISITED HEAVEN", "TOUCHED PERFECTION", "ASCENDED", "MET ETERNITY", "LA PETIT MORT"];
    breeding_climax_words = ["WELL-FILLED", "BREEDING SLUT", "BREEDER'S BLISS", "BROODMOTHER ECSTASY", "IMPREGNATION ADDICT", "EGGS SCRAMBLED", "INSATIABLE BREEDER", "BABYMAKING EUPHORIA", "CONCEPTION CLIMAX", "JIZZ ADDLED", "LOVE-STUFFED", "WHITED OUT", "CERTIFIED CUMSLUT", "IMPREGNATION INSANITY", "FERTILITY FREAK", "CUM LANDFILL"];
    rare_breeding_climax_words = ["CHURNING NUT-BUTTER", "OVARIAN OVATION", "EGGSTATIC", "OVER EASY", "NUT-BUTTER NIRVANA", "EGGS BENEDICTION"];
    kissing_climax_words = ["MELTED", "SWEETENED", "KISS-DRUNK", "IN BLISS", "LOVE-DAZED", "SWOONED", "LIP SERVICED", "FRENCHED", "WEAK IN THE LIPS", "SMOOCHED STUPID", "TONGUE TIED", "LIP LOCKED", "RAVISHED"];
    rare_kissing_climax_words = ["FIRST BASE RUNNER", "TONGUEWRESTLING CHAMP", "KISS OF LIFE"];
    temp_color = array_shuffle(temp_color);
    comment = "next two lines have different logic in vanilla; I think they only generate grayscale. reverted to modded values";
    top_skin = (arg1 == -1) ? make_color_hsv(random_range(0, 15), random_range(32, 128), choose(random_range(200, 250), random_range(150, 200), random_range(50, 150))) : make_color_hsv(random_range(0, 15), random_range(32, 128), arg1);
    top_hair = make_color_hsv(random_range(0, 15), random_range(32, 255), random_range(32, 255));
    top_stockings = temp_color[2];
    eye_color = make_color_hsv(choose(random_range(140, 235), random_range(90, 120), random_range(60, 85), random_range(35, 55), random_range(0, 30)), random_range(70, 250), random_range(80, 250));
    cum_color = 13497599;
    pill_effect = 0;
    contraceptive_pill = false;
    mega_sperm_pill = false;
    equine_pill = false;
    knotted_pill = false;
    extra_thick_pill = false;
    diphallia_pill = false;
    ovulation_pill = false;
    stamina_pill = false;
    leaky_pill = false;
    hyper_breeding_pill = false;
    blockage_pill = false;
    quickshot_pill = false;
    reverse_speed_pill = false;
    edge_addict_pill = false;
    eggxcelent_pill = false;
    premature_pill = false;
    edge_lover_pill = false;
    pound_town_pill = false;
    livestream_pill = false;
    growth_cascade_pill = false;
    if (three_pump_champ_pill)
    {
        user_pumps_max = three_pump_champ_saved_pumps;
        cum_volume_modifier /= 3;
    }
    three_pump_champ_pill = false;
    comment = "sync prev vars so change-detection does not fire removal logic against new character's base stats";
    contraceptive_pill_prev = false;
    mega_sperm_pill_prev = false;
    equine_pill_prev = false;
    knotted_pill_prev = false;
    extra_thick_pill_prev = false;
    diphallia_pill_prev = false;
    ovulation_pill_prev = false;
    eggxcelent_pill_prev = false;
    stamina_pill_prev = false;
    leaky_pill_prev = false;
    hyper_breeding_pill_prev = false;
    blockage_pill_prev = false;
    quickshot_pill_prev = false;
    reverse_speed_pill_prev = false;
    edge_addict_pill_prev = false;
    pound_town_pill_prev = false;
    eggxcelent_pill_prev = false;
    comment = "have adjusted these values back to the (approximately) vanilla standard, to allow for the pill effect stacking";
    ball_size = random_range(0.8, 1.2);
    virility_modifier = random_range(0.8, 1.4);
    cum_volume_modifier = random_range(0.7, 1.5);
    top_ass_size = random_range(0.75, 1.25);
    top_penis_width = random_range(0.8, 1.2);
    top_penis_length = random_range(0.8, 1.2);
    top_boob_size = random_range(0.8, 1.2);
    cum_color = choose(13497599, 12776191, 14612735, 14609151, 14609663, 12902389);
    custom_portrait_scale = 1;
    custom_mating_press_scale = 1;
    custom_cowgirl_scale = 1;
    custom_condom_scale = 1;
    custom_xray_scale = 1;
    condom_offset_mpress = 0;
    condom_offset_cowgirls = 0;
    custom_xray_offset_y = 0;
    max_loads = choose(2, 5, 7, 10);
    custom_dialogue_set_top = -1;
    rare_guarantee += 1;
    penis_type_index = 0;
    ds_list_clear(custom_moan_slow_list);
    ds_list_clear(custom_moan_fast_list);
    ds_list_clear(custom_orgasm_list);
    ds_list_clear(moan_slow_list);
    ds_list_clear(moan_fast_list);
    ds_list_clear(orgasm_list);
    moan_previous = -1;
    if (custom_sprite_loaded == true)
    {
        rare_guarantee += 2;
    }
    if (sprite_exists(custom_bc_crest))
    {
        sprite_delete(custom_bc_crest);
    }
    custom_bc_crest = -1;
    if (sprite_exists(custom_bc_crest_mp))
    {
        sprite_delete(custom_bc_crest_mp);
    }
    custom_bc_crest_mp = -1;
    if (sprite_exists(custom_bc_crest_cg))
    {
        sprite_delete(custom_bc_crest_cg);
    }
    custom_bc_crest_cg = -1;
    if (sprite_exists(custom_bc_crest_dt))
    {
        sprite_delete(custom_bc_crest_dt);
    }
    custom_bc_crest_dt = -1;
    custom_bc_loaded = false;
    if (sprite_exists(legacy_bc_crest))
    {
        sprite_delete(legacy_bc_crest);
    }
    legacy_bc_crest = -1;
    if (sprite_exists(custom_sperm_sprite))
    {
        sprite_delete(custom_sperm_sprite);
    }
    custom_sperm_sprite = -1;
    if (sprite_exists(custom_sperm_big_sprite))
    {
        sprite_delete(custom_sperm_big_sprite);
    }
    custom_sperm_big_sprite = -1;
    top_sprite = sFutaMatingPress;
    hair_sprite = choose(sFutaMatingPress, sFutaMatingPress2, sFutaMatingPress3, sFutaMatingPress4, sFutaMatingPressAndroid, sFutaMatingPressDevil, sFutaMatingPressClown);
    face_sprite = choose(sFutaPortrait1, sFutaPortrait2, sFutaPortrait3, sFutaPortrait4);
    eye_sprite = choose(sFutaPortrait1Eyes, sFutaPortrait2Eyes, sFutaPortrait3Eyes, sFutaPortrait4Eyes);
    mouth_id = choose(0, 2, 4, 6);
    bangs_sprite = choose(sFutaPortrait1, sFutaPortrait2, sFutaPortrait3, sFutaPortrait4, sFutaPortraitAndroid, sFutaPortraitDevil, sFutaPortraitClown);
    outfit_sprite = choose(sOutfitMatingPress1, sOutfitMatingPress2, sOutfitMatingPress3);
    outfit_toggle = choose(true, false);
    futa_boob_index = irandom(3);
    var rare_chance = irandom(4);
    if (arg0 != -1)
    {
        top_sprite = arg0;
    }
    else if ((rare_chance == 0 || rare_guarantee > 10) && title == false)
    {
        oAudioManager.play_sfx(sndRare, 0, 1, 0.8);
        rare_guarantee = 0;
        var rare_list = ds_list_create();
        ds_list_add(rare_list, sFutaMatingPressDevil, sFutaMatingPressSlime, sFutaMatingPressAndroid, sFutaMatingFurry, sFutaMatingPressAlien, sFutaMatingPressClown, mystery_pilled_futa, sFutaMatingBunny);
        if (custom_sprite_loaded == true)
        {
            var _rand_futa_folder = ds_list_find_value(custom_futas_folder, irandom(ds_list_size(custom_futas_folder) - 1));
            var randomizer_alt_max = 1;
            while (file_exists(string(_rand_futa_folder) + "/custom_futa_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
            {
                randomizer_alt_max++;
            }
            custom_futa_alt_index = irandom(randomizer_alt_max - 1);
            func_load_custom_futa(_rand_futa_folder, custom_futa_alt_index);
            ds_list_add(rare_list, custom_mating_press, custom_mating_press, custom_mating_press);
        }
        top_sprite = ds_list_find_value(rare_list, irandom(ds_list_size(rare_list) - 1));
        ds_list_destroy(rare_list);
    }
    switch (top_sprite)
    {
        case mystery_pilled_futa:
            top_sprite = sFutaMatingPress;
            var pill_items = ["mega_sperm", "equine", "knotted", "extra_thick", "stamina", "leaky", "diphallia", "hyper_breeding", "quickshot", "blockage", "edge_addicted", "reverse_speed", "premature", "edge_lover"];
            var pill_weights = [3, 4, 4, 4, 2, 2, 1, 0.5, 1, 0.5, 2, 1, 2, 2];
            var pill_count = irandom_range(2, 4);
            repeat (pill_count)
            {
                var pill = func_weighted_pick(pill_items, pill_weights);
                switch (pill)
                {
                    case "mega_sperm":
                        mega_sperm_pill = true;
                        break;
                    case "equine":
                        equine_pill = true;
                        break;
                    case "knotted":
                        knotted_pill = true;
                        break;
                    case "extra_thick":
                        extra_thick_pill = true;
                        break;
                    case "stamina":
                        stamina_pill = true;
                        break;
                    case "leaky":
                        leaky_pill = true;
                        break;
                    case "diphallia":
                        diphallia_pill = true;
                        break;
                    case "hyper_breeding":
                        hyper_breeding_pill = true;
                        break;
                    case "premature":
                        premature_pill = true;
                        break;
                    case "edge_lover":
                        edge_lover_pill = true;
                        break;
                    case "quickshot":
                        quickshot_pill = true;
                        break;
                    case "blockage":
                        blockage_pill = true;
                        break;
                    case "edge_addicted":
                        edge_addicted_pill = true;
                        break;
                    case "reverse_speed":
                        reverse_speed_pill = true;
                        break;
                }
                var index = -1;
                for (var i = 0; i < array_length(pill_items); i++)
                {
                    if (pill_items[i] == pill)
                    {
                        index = i;
                        break;
                    }
                }
                if (index != -1)
                {
                    array_delete(pill_items, index, 1);
                    array_delete(pill_weights, index, 1);
                }
            }
            break;
        case sFutaMatingPressSlime:
            penis_type_index = 0;
            hair_sprite = sFutaMatingPressSlime;
            top_skin = make_color_hsv(irandom(255), 100, (arg1 != -1) ? arg1 : 255);
            top_hair = top_skin;
            eye_color = top_skin;
            cum_color = top_skin;
            face_sprite = sFutaPortraitSlime;
            mouth_id = 14;
            eye_sprite = sFutaPortraitSlimeEyes;
            bangs_sprite = sFutaPortraitSlime;
            outfit_toggle = false;
            top_penis_length = random_range(1.2, 1.35);
            top_penis_width = random_range(1, 1.35);
            ball_size = random_range(1.2, 1.35);
            virility_modifier = random_range(0.1, 0.2);
            cum_volume_modifier = random_range(2.25, 2.75);
            max_loads = 10;
            futa_boob_index = irandom(3);
            breeding_milestone_text = ["GROWING FAMILY", "BROODMOTHER", "ALL-STAR BREEDER", "SLIME SEEDBED", "OVERSTUFFED WOMB", "PUTS RABBITS TO SHAME", "POPULATION BOOM", "MATERNITY WARD", "STORK'S WORST NIGHTMARE", "IT MAKES A VILLAGE", "SLIME QUEEN SOVEREIGN", "DAYCARE INDUSTRIAL COMPLEX", "DEMOGRAPHIC SHIFTER", "SPECIES SAVIOUR", "REPOPULATION SINGULARITY", "UNIVERSAL ANCESTOR", "PLANETARY COLONIZER", "SAIYAN SOVERIGN: THE LEGENDARY SUPER SLUT"];
            break;
        case sFutaMatingPressAndroid:
            penis_type_index = 0;
            top_skin = 16777215;
            top_hair = make_color_hsv(irandom(255), 100, 255);
            eye_color = top_hair;
            cum_color = merge_color(top_hair, top_skin, 0.5);
            top_penis_length = random_range(1.2, 1.35);
            top_penis_width = random_range(1, 1.35);
            ball_size = random_range(1.2, 1.35);
            virility_modifier = random_range(0.01, 0.1);
            cum_volume_modifier = random_range(1.1, 1.3);
            max_loads = 10;
            futa_boob_index = irandom(3);
            breeding_milestone_text = ["GROWING FAMILY", "BROODMOTHER", "ALL-STAR BREEDER", "DROID FOUNDRY", "OVERSTUFFED WOMB", "PUTS RABBITS TO SHAME", "ASSEMBLY LINE OVERDRIVE", "MATERNITY WARD", "STORK'S WORST NIGHTMARE", "IT MAKES A VILLAGE", "MOTHER OF ALL BOARDS", "DAYCARE INDUSTRIAL COMPLEX", "DEMOGRAPHIC SHIFTER", "SPECIES SAVIOUR", "REPOPULATION SINGULARITY", "UNIVERSAL ANCESTOR", "PLANETARY COLONIZER", "SAIYAN SOVERIGN: THE LEGENDARY SUPER SLUT"];
            break;
        case sFutaMatingFurry:
            penis_type_index = 2;
            top_skin = make_color_hsv(choose(random_range(0, 25), random_range(150, 170)), random_range(0, 150), (arg1 != -1) ? arg1 : random_range(200, 255));
            top_hair = merge_color(c_white, top_skin, 0.5);
            face_sprite = sFutaPortraitFurry;
            mouth_id = 12;
            eye_sprite = sFutaPortraitFurryEyes;
            top_penis_length = random_range(1.2, 1.35);
            top_penis_width = random_range(1, 1.35);
            ball_size = random_range(1.2, 1.35);
            virility_modifier = random_range(2, 3.5);
            cum_volume_modifier = random_range(1.2, 1.35);
            max_loads = 10;
            futa_boob_index = irandom(3);
            breeding_milestone_text = ["GROWING FAMILY", "BROODMOTHER", "ALL-STAR BREEDER", "PUPPY MILL", "OVERSTUFFED WOMB", "PUTS RABBITS TO SHAME", "LITTER(-AL) EXPLOSION", "MATERNITY WARD", "STORK'S WORST NIGHTMARE", "IT MAKES A VILLAGE", "QUEEN BITCH", "DAYCARE INDUSTRIAL COMPLEX", "DEMOGRAPHIC SHIFTER", "SPECIES SAVIOUR", "REPOPULATION SINGULARITY", "UNIVERSAL ANCESTOR", "PLANETARY COLONIZER", "SAIYAN SOVERIGN: THE LEGENDARY SUPER SLUT"];
            break;
        case sFutaMatingPressDevil:
            penis_type_index = 1;
            var devil_color = make_color_hsv(random_range(200, 255), 225, (arg1 != -1) ? arg1 : 255);
            top_skin = merge_color(top_skin, devil_color, 0.5);
            top_hair = 16777215;
            eye_color = make_color_hsv(choose(random_range(0, 10), random_range(10, 25), random_range(35, 55), random_range(260, 290), random_range(300, 330), random_range(170, 200)), random_range(180, 255), random_range(220, 255));
            face_sprite = sFutaPortraitDevil;
            mouth_id = 6;
            eye_sprite = sFutaPortraitDevilEyes;
            top_penis_length = random_range(1.35, 1.35);
            top_penis_width = random_range(1.2, 1.35);
            ball_size = random_range(1.35, 1.5);
            virility_modifier = random_range(2, 3);
            cum_volume_modifier = random_range(1.3, 1.5);
            cum_color = choose(13497599, 12776191, 14612735, 14609151, 14609663, 12902389);
            max_loads = 12;
            futa_boob_index = irandom(3);
            breeding_milestone_text = ["GROWING FAMILY", "BROODMOTHER", "ALL-STAR BREEDER", "IMP INCUBATOR", "OVERSTUFFED WOMB", "PUTS RABBITS TO SHAME", "DEMONIC INVASION", "MATERNITY WARD", "STORK'S WORST NIGHTMARE", "IT MAKES A VILLAGE", "UNHOLY EMPRESS", "DAYCARE INDUSTRIAL COMPLEX", "DEMOGRAPHIC SHIFTER", "SPECIES SAVIOUR", "REPOPULATION SINGULARITY", "UNIVERSAL ANCESTOR", "PLANETARY COLONIZER", "SAIYAN SOVERIGN: THE LEGENDARY SUPER SLUT"];
            break;
        case sFutaMatingPressAlien:
            penis_type_index = 0;
            var alien_color = make_color_hsv(random_range(50, 165), 225, (arg1 != -1) ? arg1 : 255);
            top_skin = merge_color(top_skin, alien_color, 0.5);
            top_hair = 16777215;
            cum_color = merge_color(top_skin, c_white, 0.5);
            face_sprite = sFutaPortraitAlien;
            eye_sprite = sFutaPortraitAlienEyes;
            outfit_toggle = false;
            top_penis_length = random_range(1, 1.35);
            top_penis_width = random_range(1, 1.35);
            ball_size = random_range(1, 1.35);
            virility_modifier = random_range(0.5, 1.5);
            cum_volume_modifier = random_range(1.1, 1.5);
            max_loads = choose(6, 7, 8);
            futa_boob_index = irandom(3);
            breeding_milestone_text = ["GROWING FAMILY", "BROODMOTHER", "ALL-STAR BREEDER", "ALIEN SEEDBED", "OVERSTUFFED WOMB", "PUTS RABBITS TO SHAME", "EXTRATERRESTRIAL INVASION", "MATERNITY WARD", "STORK'S WORST NIGHTMARE", "IT MAKES A VILLAGE", "GALACTIC EMPRESS", "DAYCARE INDUSTRIAL COMPLEX", "DEMOGRAPHIC SHIFTER", "SPECIES SAVIOUR", "REPOPULATION SINGULARITY", "UNIVERSAL ANCESTOR", "PLANETARY COLONIZER", "SAIYAN SOVERIGN: THE LEGENDARY SUPER SLUT"];
            break;
        case sFutaMatingPressClown:
            penis_type_index = 0;
            top_hair = make_color_hsv(irandom(255), 100, 255);
            top_skin = 16777215;
            face_sprite = sFutaPortraitClown;
            eye_sprite = sFutaPortraitClownEyes;
            outfit_sprite = sFutaMatingPressClownClothes;
            top_penis_length = random_range(1.2, 1.35);
            top_penis_width = random_range(1, 1.35);
            ball_size = random_range(1.2, 1.35);
            virility_modifier = random_range(0.5, 1.5);
            cum_volume_modifier = random_range(1.1, 1.5);
            max_loads = choose(6, 7, 8);
            top_skin = (arg1 == -1) ? make_color_hsv(random_range(5, 15), random_range(25, 90), choose(random_range(220, 255), random_range(160, 219), random_range(80, 159))) : make_color_hsv(random_range(5, 15), random_range(25, 90), arg1);
            var clown_outfit = choose(0, 1, 2);
            if (clown_outfit == 0)
            {
                var _h = random_range(0, 255);
                var _s = random_range(50, 200);
                var _v = random_range(200, 255);
                outfit_body_color = make_color_hsv(_h, _s, _v);
                outfit_hips_color = outfit_body_color;
                outfit_legs_color = make_color_hsv(_h, _s, random_range(40, 190));
            }
            if (clown_outfit == 1)
            {
                var _h = random_range(0, 255);
                var _s = random_range(50, 200);
                var _v = random_range(200, 255);
                outfit_body_color = make_color_hsv(_h, _s, _v);
                outfit_hips_color = outfit_body_color;
                outfit_legs_color = make_color_hsv(_h, _s, random_range(180, 255));
            }
            if (clown_outfit == 2)
            {
                var _h = random_range(0, 255);
                var _s = random_range(50, 200);
                var _v = random_range(200, 255);
                outfit_body_color = make_color_hsv(_h, _s, _v);
                outfit_hips_color = outfit_body_color;
                outfit_legs_color = make_color_hsv(_h, _s, random_range(200, 255));
            }
            oAudioManager.play_sfx(choose(sndHonk1, sndHonk2, sndHonk3, sndHonk4), 0, 1, 0.5);
            break;
        case sFutaMatingBunny:
            penis_type_index = 0;
            face_sprite = sFutaPortraitBunny;
            eye_sprite = sFutaPortraitBunnyEyes;
            outfit_sprite = sFutaMatingBunnyClothes;
            outfit_toggle = true;
            top_penis_length = random_range(1.2, 1.35);
            top_penis_width = random_range(1, 1.35);
            ball_size = random_range(1.2, 1.35);
            virility_modifier = random_range(1, 2);
            cum_volume_modifier = random_range(1.1, 1.5);
            max_loads = choose(6, 7, 8);
            bunny_money = 0;
            bunny_money_lerp = 0;
            top_skin = (arg1 == -1) ? make_color_hsv(random_range(5, 15), random_range(25, 90), choose(random_range(220, 255), random_range(160, 219), random_range(80, 159))) : make_color_hsv(random_range(5, 15), random_range(25, 90), arg1);
            var bunny_outfit = choose(0, 1, 2);
            if (bunny_outfit == 0)
            {
                var _h = random_range(0, 50);
                var _s = random_range(100, 200);
                var _v = random_range(180, 255);
                outfit_body_color = make_color_hsv(_h, _s, _v);
                outfit_hips_color = outfit_body_color;
                outfit_legs_color = make_color_hsv(_h, _s, random_range(80, 160));
            }
            if (bunny_outfit == 1)
            {
                var _h = random_range(60, 150);
                var _s = random_range(100, 200);
                var _v = random_range(80, 160);
                outfit_body_color = make_color_hsv(_h, _s, _v);
                outfit_hips_color = outfit_body_color;
                outfit_legs_color = make_color_hsv(_h, _s, random_range(180, 255));
            }
            if (bunny_outfit == 2)
            {
                var _h = random_range(140, 255);
                var _s = random_range(150, 255);
                var _v = random_range(150, 220);
                outfit_body_color = make_color_hsv(_h, _s, _v);
                outfit_hips_color = outfit_body_color;
                outfit_legs_color = make_color_hsv(_h, _s, random_range(200, 255));
            }
            break;
        case custom_mating_press:
            custom_portrait_scale = (sprite_exists(custom_portrait) && sprite_get_width(custom_portrait) > 0) ? (128 / sprite_get_width(custom_portrait)) : 1;
            custom_mating_press_scale = 160 / sprite_get_width(custom_mating_press);
            custom_cowgirl_scale = 160 / sprite_get_width(custom_cowgirl);
            custom_condom_scale = 160 / sprite_get_width(custom_condom);
            custom_xray_scale = 160 / sprite_get_width(custom_xray);
            func_apply_custom_futa_stats();
            break;
    }
    base_penis_type_index = penis_type_index;
    if (equine_pill)
    {
        penis_type_index |= 1;
    }
    if (knotted_pill)
    {
        penis_type_index |= 2;
    }
    comment = "graphics mod decouples penis type from top type";
    if (top_sprite == custom_mating_press)
    {
        penis_sprite = custom_mating_press;
    }
    else if (top_sprite == legacy_custom_mating_press || top_sprite != custom_mating_press)
    {
        switch (penis_type_index)
        {
            case 1:
                penis_sprite = sFutaMatingPressDevil;
                break;
            case 2:
                penis_sprite = sFutaMatingFurry;
                break;
            case 3:
                penis_sprite = sFutaMatingPressKnottedHorse;
                break;
            default:
                penis_sprite = top_sprite;
                break;
        }
    }
    if (pound_town_pill == true)
    {
        max_loads *= 5;
        sex_progress_max = 60;
    }
    func_set_top_orgasm_pumps_max();
    orgasm_pumps = orgasm_pumps_max;
    orgasm_pumps_display_snapshot = orgasm_pumps_max;
    penis_color = top_skin;
    penis_head_color = top_skin;
    if (prev_cum_color == -1)
    {
        prev_cum_color = cum_color;
        cum_fill_color = cum_color;
    }
}

function func_apply_custom_futa_stats()
{
    if (is_legacy_custom)
    {
        top_sprite = (sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press != -1) ? legacy_custom_mating_press : sFutaMatingPress;
        penis_sprite = top_sprite;
        hair_sprite = top_sprite;
        face_sprite = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
        bangs_sprite = face_sprite;
        condom_offset_mpress = custom_condom_offset_mpress;
        condom_offset_cowgirls = custom_condom_offset_cowgirls;
        condom_offset_deepthroat = custom_condom_offset_deepthroat;
    }
    else
    {
        top_sprite = (sprite_exists(custom_mating_press) && custom_mating_press != -1) ? custom_mating_press : sFutaMatingPress;
        penis_sprite = top_sprite;
        hair_sprite = top_sprite;
        face_sprite = (sprite_exists(custom_portrait) && custom_portrait != -1) ? custom_portrait : sFutaPortrait1;
        bangs_sprite = face_sprite;
        condom_offset_mpress = custom_condom_offset_mpress;
        condom_offset_cowgirls = custom_condom_offset_cowgirls;
        condom_offset_deepthroat = custom_condom_offset_deepthroat;
    }
    top_hair = 16777215;
    top_skin = 16777215;
    penis_color = 16777215;
    penis_head_color = 16777215;
    eye_color = 16777215;
    top_boob_size = custom_top_boob_size;
    top_ass_size = custom_top_ass_size;
    top_penis_length = custom_top_penis_length;
    top_penis_width = custom_top_penis_width;
    ball_size = custom_ball_size;
    virility_modifier = custom_virility_modifier;
    cum_volume_modifier = custom_cum_volume_modifier;
    stroke_depth = custom_stroke_depth;
    stroke_speed = custom_stroke_speed;
    pump_delay = custom_pump_delay;
    max_loads = custom_max_loads;
    if (custom_condom_color_set)
    {
        condom_color = custom_condom_color;
    }
    outfit_toggle = false;
    mega_sperm_pill = custom_mega_sperm_pill;
    equine_pill = custom_equine_pill;
    knotted_pill = custom_knotted_pill;
    extra_thick_pill = custom_extra_thick_pill;
    diphallia_pill = custom_diphallia_pill;
    stamina_pill = custom_stamina_pill;
    leaky_pill = custom_leaky_pill;
    hyper_breeding_pill = custom_hyper_breeding_pill;
    blockage_pill = custom_blockage_pill;
    quickshot_pill = custom_quickshot_pill;
    reverse_speed_pill = custom_reverse_speed_pill;
    edge_addict_pill = custom_edge_addict_pill;
    pound_town_pill = custom_pound_town_pill;
    premature_pill = custom_premature_pill;
    edge_lover_pill = custom_edge_lover_pill;
    growth_cascade_pill = custom_growth_cascade_pill;
    livestream_pill = custom_livestream_pill;
    three_pump_champ_pill = custom_three_pump_champ_pill;
    mega_sperm_pill_prev = custom_mega_sperm_pill;
    equine_pill_prev = custom_equine_pill;
    knotted_pill_prev = custom_knotted_pill;
    extra_thick_pill_prev = custom_extra_thick_pill;
    diphallia_pill_prev = custom_diphallia_pill;
    stamina_pill_prev = custom_stamina_pill;
    leaky_pill_prev = custom_leaky_pill;
    hyper_breeding_pill_prev = custom_hyper_breeding_pill;
    blockage_pill_prev = custom_blockage_pill;
    quickshot_pill_prev = custom_quickshot_pill;
    reverse_speed_pill_prev = custom_reverse_speed_pill;
    edge_addict_pill_prev = custom_edge_addict_pill;
    pound_town_pill_prev = custom_pound_town_pill;
    premature_pill = custom_premature_pill;
    edge_lover_pill = custom_edge_lover_pill;
    growth_cascade_pill = custom_growth_cascade_pill;
    livestream_pill = custom_livestream_pill;
    three_pump_champ_pill = custom_three_pump_champ_pill;
    base_penis_type_index = custom_penis_type_index;
    penis_type_index = base_penis_type_index;
    if (equine_pill)
    {
        penis_type_index |= 1;
    }
    if (knotted_pill)
    {
        penis_type_index |= 2;
    }
}

fill_amount = 0;
fill_lerp = 0;
condom_lerp = 0;
fill_max = 20;
wife_womb_capacity = 20;
xray = true;
tutorial = false;
global.ps = part_system_create();
part_system_automatic_draw(global.ps, false);
global.ps_back = part_system_create();
part_system_automatic_draw(global.ps_back, false);
stat_sperm_cell = 0;
stat_pump_rand = 0;
stat_pump_volume = 0;
stat_orgasm_volume = 0;
stat_volume_remaining = 0;
stat_liters = 0;
stat_duration = 0;
comment = "stat_pumps is new in 1.1";
stat_pumps = 0;
stat_liters_lerp = 0;
stat_sperm_cell_lerp = 0;
sex_progress = 0;
pill_effect = 0;
partner_set = 0;
partner_male = false;
part_love = part_type_create();
part_type_sprite(part_love, sHearts, true, true, false);
part_type_direction(part_love, 90, 90, 0, 0);
part_type_speed(part_love, 0.1, 0.1, 0, 0);
part_type_life(part_love, 120, 360);
part_timer = 0;
title = true;
title_scale = 1;
title_timer = 240;
title_prev_sound = true;
disclaimer = false;
disclaimer_scale = 0;
logo_scale = 0;
title_alpha = 0;
start_timer = 0;
title_from_hotkey = false;
title_background_id = 0;
muffle_pending = false;
muffle_delay_timer = 0;
effect_muffled = audio_effect_create(4, 
{
    cutoff: 750,
    q: 1
});
effect_gain = audio_effect_create(2, 
{
    gain: 0.25
});
audio_bus_main.effects[0] = effect_muffled;
audio_bus_main.effects[1] = effect_gain;
ambience_pending = true;
bottom_skin = make_color_hsv(random_range(0, 18), random_range(32, 128), random_range(32, 500));
hair_sprite_array = [sFutaMatingPress, sFutaMatingPress2, sFutaMatingPress3, sFutaMatingPress4, sFutaMatingPressAndroid, sFutaMatingPressDevil, sFutaMatingPressClown];
wife_hair_sprite_array = [sWifeNormalCowgirl1, sWifeNormalCowgirl2, sWifeNormalCowgirl3, sWifeNormalCowgirl4, sWifeNormalCowgirlAndroid, sWifeNormalCowgirlDevil];
womb_color = make_color_hsv(random_range(230, 256), random_range(128, 256), random_range(64, 256));
func_randomize_top();
func_randomize_bottom();

function func_randomize_bottom(arg0 = -1, arg1 = -1)
{
    var temp_color = -1;
    for (var i = 0; i < 5; i++)
    {
        temp_color[i] = make_color_hsv(30, 0, min(255, 100 + (50 * i) + random_range(-25, 25)));
    }
    bottom_ass_size = random_range(0.8, 1.3);
    bottom_boob_size = random_range(0.9, 1.1);
    temp_color = array_shuffle(temp_color);
    bottom_skin = (arg1 == -1) ? make_color_hsv(random_range(0, 15), random_range(32, 128), choose(random_range(200, 250), random_range(150, 200), random_range(50, 150))) : make_color_hsv(random_range(0, 15), random_range(32, 128), arg1);
    bottom_hair = make_color_hsv(random_range(0, 15), random_range(32, 255), random_range(32, 255));
    wife_hair_sprite = choose(sWifeNormalCowgirl1, sWifeNormalCowgirl2, sWifeNormalCowgirl3, sWifeNormalCowgirl4, sWifeNormalCowgirlAndroid, sWifeNormalCowgirlDevil);
    wife_face_sprite = choose(sFutaPortrait1, sFutaPortrait2, sFutaPortrait3, sFutaPortrait4);
    wife_eye_sprite = choose(sFutaPortrait1Eyes, sFutaPortrait2Eyes, sFutaPortrait3Eyes, sFutaPortrait4Eyes);
    wife_eye_color = make_color_hsv(choose(random_range(90, 120), random_range(60, 85), random_range(35, 55), random_range(20, 30)), random_range(80, 180), random_range(80, 255));
    wife_mouth_id = choose(0, 2, 4, 6);
    wife_bangs_sprite = choose(sFutaPortrait1, sFutaPortrait2, sFutaPortrait3, sFutaPortrait4, sFutaPortraitAndroid, sFutaPortraitDevil);
    bottom_sprite = sWifeMatingPress;
    bottom_stockings = 8421504;
    wife_outfit_sprite = choose(sWifeNormalCowgirlOutfit1, sWifeNormalCowgirlOutfit2, sWifeNormalCowgirlOutfit3);
    wife_outfit_toggle = choose(true, false);
    partner_male = false;
    contraceptive_pill = false;
    contraceptive_pill_prev = contraceptive_pill;
    ovulation_pill = false;
    ovulation_pill_prev = ovulation_pill;
    custom_wife_portrait_scale = 1;
    custom_dialogue_set_bottom = -1;
    wife_size_response = random_range(0.4, 1.4);
    wife_intensity_response = random_range(0.4, 1.4);
    wife_cum_response = random_range(0.4, 1.4);
    wife_reproductive_response = random_range(0.4, 1.4);
    wife_affection_response = random_range(0.4, 1.4);
    wife_pain_response = random_range(0.4, 1.4);
    if (title == false)
    {
        if (arg0 != -1)
        {
            bottom_sprite = arg0;
        }
        else if (random(1) <= bottom_male_chance)
        {
            bottom_sprite = sHusbandMatingPress;
        }
        else if (custom_wife_sprite_loaded == true && irandom(4) == 0 && title == false)
        {
            oAudioManager.play_sfx(sndRare, 0, 1, 0.8);
            var custom_count = ds_list_size(custom_wives_folder);
            if (custom_count > 0)
            {
                custom_wife_index = irandom(custom_count - 1);
                var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                var randomizer_alt_max = 1;
                while (file_exists(string(selected_folder) + "/custom_wife_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                {
                    randomizer_alt_max++;
                }
                custom_wife_alt_index = irandom(randomizer_alt_max - 1);
                func_load_custom_wife(selected_folder, custom_wife_alt_index);
                func_validate_sex_position();
                bottom_sprite = custom_wife_mating_press;
            }
        }
        else
        {
            bottom_sprite = choose(sWifeMatingPressDevil, sWifeMatingPressSlime, sWifeMatingPress, sWifeMatingPressFurry, sWifeMatingPressAndroid);
        }
        if (bottom_sprite != custom_wife_mating_press)
        {
            custom_default_moans = false;
            ds_list_clear(custom_moan_slow_list);
            ds_list_clear(custom_moan_fast_list);
            ds_list_clear(custom_orgasm_list);
            ds_list_clear(moan_slow_list);
            ds_list_clear(moan_fast_list);
            ds_list_clear(orgasm_list);
            moan_previous = -1;
        }
        switch (bottom_sprite)
        {
            case sWifeMatingPress:
                bottom_hair = make_color_hsv(random_range(0, 15), random_range(32, 255), random_range(32, 255));
                func_womb_r();
                break;
            case sWifeMatingPressSlime:
                wife_outfit_toggle = false;
                bottom_skin = make_color_hsv(irandom(255), 100, (arg1 != -1) ? arg1 : 255);
                wife_face_sprite = sFutaPortraitSlime;
                wife_mouth_id = 14;
                wife_eye_sprite = sFutaPortraitSlimeEyes;
                wife_eye_color = bottom_skin;
                wife_bangs_sprite = sFutaPortraitSlime;
                wife_hair_sprite = sFutaMatingPressSlime;
                bottom_hair = bottom_skin;
                bottom_stockings = bottom_skin;
                womb_color = bottom_skin;
                break;
            case sWifeMatingPressAndroid:
                wife_outfit_toggle = false;
                bottom_skin = 16777215;
                bottom_hair = make_color_hsv(irandom(255), 100, 255);
                wife_eye_color = top_hair;
                bottom_stockings = bottom_skin;
                womb_color = bottom_hair;
                break;
            case sWifeMatingPressFurry:
                bottom_skin = make_color_hsv(choose(random_range(0, 25), random_range(150, 170)), random_range(0, 150), (arg1 != -1) ? arg1 : random_range(200, 255));
                wife_face_sprite = sFutaPortraitFurry;
                wife_mouth_id = 12;
                wife_eye_sprite = sFutaPortraitFurryEyes;
                bottom_hair = merge_color(c_white, bottom_skin, 0.5);
                bottom_stockings = bottom_skin;
                func_womb_r();
                break;
            case sWifeMatingPressDevil:
                var devil_color = make_color_hsv(random_range(200, 255), 225, (arg1 != -1) ? arg1 : 255);
                bottom_skin = merge_color(bottom_skin, devil_color, 0.5);
                wife_face_sprite = sFutaPortraitDevil;
                wife_mouth_id = 6;
                wife_eye_sprite = sFutaPortraitDevilEyes;
                wife_eye_color = make_color_hsv(choose(random_range(0, 10), random_range(10, 25), random_range(35, 55), random_range(260, 290), random_range(300, 330), random_range(170, 200)), random_range(180, 255), random_range(220, 255));
                bottom_hair = 16777215;
                bottom_stockings = bottom_skin;
                womb_color = bottom_skin;
                break;
            case sHusbandMatingPress:
                bottom_stockings = bottom_skin;
                partner_male = true;
                wife_outfit_toggle = false;
                break;
            case custom_wife_mating_press:
                func_apply_custom_wife_stats();
                break;
        }
    }
}

function func_apply_custom_wife_stats()
{
    if (legacy_custom_wife_toggle)
    {
        bottom_sprite = legacy_custom_wife_mating_press;
    }
    else
    {
        bottom_sprite = custom_wife_mating_press;
    }
    bottom_boob_size = custom_bottom_boob_size;
    bottom_ass_size = custom_bottom_ass_size;
    wife_size_response = custom_wife_size_response;
    wife_intensity_response = custom_wife_intensity_response;
    wife_cum_response = custom_wife_cum_response;
    wife_reproductive_response = custom_wife_reproductive_response;
    wife_affection_response = custom_wife_affection_response;
    wife_pain_response = custom_wife_pain_response;
    contraceptive_pill = custom_contraceptive_pill;
    eggxcelent_pill = custom_eggxcelent_pill;
    ovulation_pill = custom_ovulation_pill;
    contraceptive_pill_prev = false;
    ovulation_pill_prev = false;
    bottom_skin = 16777215;
    bottom_hair = 16777215;
    bottom_stockings = 16777215;
    womb_color = 16777215;
    var _valid_wife_port = -1;
    if (sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1)
    {
        _valid_wife_port = custom_wife_portrait;
    }
    else if (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1)
    {
        _valid_wife_port = legacy_custom_wife_portrait;
    }
    else
    {
        _valid_wife_port = sFutaPortrait1;
    }
    wife_bangs_sprite = _valid_wife_port;
    var _valid_wife_body = -1;
    if (sprite_exists(custom_wife_mating_press) && custom_wife_mating_press != -1)
    {
        _valid_wife_body = custom_wife_mating_press;
    }
    else if (sprite_exists(legacy_custom_wife_mating_press) && legacy_custom_wife_mating_press != -1)
    {
        _valid_wife_body = legacy_custom_wife_mating_press;
    }
    else
    {
        _valid_wife_body = sWifeMatingPress;
    }
    wife_hair_sprite = _valid_wife_body;
    custom_wife_scale = 1;
    wife_outfit_toggle = false;
    partner_male = custom_partner_male;
    if (partner_male)
    {
        bottom_stockings = bottom_skin;
    }
}

function func_randomize_top_skin()
{
    var temp_color = -1;
    for (var i = 0; i < 5; i++)
    {
        temp_color[i] = make_color_hsv(30, 0, min(255, 100 + (50 * i) + random_range(-25, 25)));
    }
    temp_color = array_shuffle(temp_color);
    top_skin = make_color_hsv(random_range(0, 15), random_range(32, 128), random_range(250, 500));
}

function func_randomize_top_haircolor()
{
    var temp_color = -1;
    for (var i = 0; i < 5; i++)
    {
        temp_color[i] = make_color_hsv(30, 0, min(255, 100 + (50 * i) + random_range(-25, 25)));
    }
    temp_color = array_shuffle(temp_color);
    top_hair = make_color_hsv(random_range(0, 15), random_range(32, 255), random_range(32, 255));
}

function func_randomize_top_hair()
{
    hair_sprite = choose(sFutaMatingPress, sFutaMatingPress2, sFutaMatingPress3, sFutaMatingPress4, sFutaMatingPressAndroid, sFutaMatingPressDevil, sFutaMatingPressClown);
}

function func_randomize_bottom_hair()
{
    wife_hair_sprite = choose(sWifeNormalCowgirl1, sWifeNormalCowgirl2, sWifeNormalCowgirl3, sWifeNormalCowgirl4, sWifeNormalCowgirlAndroid, sWifeNormalCowgirlDevil);
}

function func_condom_random()
{
    condom_color = make_color_rgb(random_range(64, 255), random_range(64, 255), random_range(64, 255));
}

function func_womb_r()
{
    womb_color = make_color_hsv(random_range(230, 256), random_range(128, 256), random_range(64, 256));
}

function round_fixed(arg0, arg1)
{
    comment = "this function doesn't exist in 1.1 - I don't know what it does. It doesn't seem to be used anywhere, either";
    return round(arg0 * power(10, arg1)) / power(10, arg1);
}

function func_get_money(arg0)
{
    var money = string(round(arg0));
    var i = string_length(money) - 2;
    while (i > 1)
    {
        money = string_insert(",", money, i);
        i -= 3;
    }
    return money;
}

function func_get_portrait(arg0, arg1)
{
    var return_port = sFutaPortrait1;
    switch (arg1)
    {
        case 0:
            switch (arg0)
            {
                case sFutaMatingPress:
                    return_port = sFutaPortrait1;
                    break;
                case sFutaMatingPress2:
                    return_port = sFutaPortrait2;
                    break;
                case sFutaMatingPress3:
                    return_port = sFutaPortrait3;
                    break;
                case sFutaMatingPress4:
                    return_port = sFutaPortrait4;
                    break;
                case sFutaMatingPressDevil:
                    return_port = sFutaPortraitDevil;
                    break;
                case sFutaMatingPressSlime:
                    return_port = sFutaPortraitSlime;
                    break;
                case sFutaMatingPressAndroid:
                    return_port = sFutaPortraitAndroid;
                    break;
                case sFutaMatingPressAlien:
                    return_port = sFutaPortraitAlien;
                    break;
                case sFutaMatingPressClown:
                    return_port = sFutaPortraitClown;
                    break;
                case sFutaMatingBunny:
                    return_port = sFutaPortraitBunny;
                    break;
                case sFutaMatingFurry:
                    return_port = sFutaPortraitFurry;
                    break;
                case custom_mating_press:
                    return_port = custom_portrait;
                    break;
                case legacy_custom_mating_press:
                    return_port = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
                    break;
            }
            break;
        case 1:
            switch (arg0)
            {
                case sWifeNormalCowgirl1:
                    return_port = sFutaPortrait1;
                    break;
                case sWifeNormalCowgirl2:
                    return_port = sFutaPortrait2;
                    break;
                case sWifeNormalCowgirl3:
                    return_port = sFutaPortrait3;
                    break;
                case sWifeNormalCowgirl4:
                    return_port = sFutaPortrait4;
                    break;
                case sWifeNormalCowgirlDevil:
                    return_port = sFutaPortraitDevil;
                    break;
                case sFutaMatingPressSlime:
                    return_port = sFutaPortraitSlime;
                    break;
                case sWifeNormalCowgirlAndroid:
                    return_port = sFutaPortraitAndroid;
                    break;
                case sFutaMatingFurry:
                    return_port = sFutaPortraitFurry;
                    break;
                case custom_wife_mating_press:
                    return_port = custom_wife_portrait;
                    break;
            }
            break;
    }
    if (return_port <= 0 || !sprite_exists(return_port))
    {
        return_port = sFutaPortrait1;
    }
    return return_port;
}

function func_wife_portrait_body(arg0)
{
    var return_port = sFutaPortrait1;
    switch (arg0)
    {
        case sWifeMatingPress:
            return_port = sFutaPortrait1;
            break;
        case sWifeMatingPressDevil:
            return_port = sFutaPortraitDevil;
            break;
        case sWifeMatingPressSlime:
            return_port = sFutaPortraitSlime;
            break;
        case sWifeMatingPressAndroid:
            return_port = sFutaPortraitAndroid;
            break;
        case sWifeMatingPressFurry:
            return_port = sFutaPortraitFurry;
            break;
        case custom_wife_mating_press:
            return_port = (sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1) ? custom_wife_portrait : sFutaPortrait1;
            break;
        case legacy_custom_wife_mating_press:
            return_port = (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1) ? legacy_custom_wife_portrait : sFutaPortrait1;
            break;
    }
    return (sprite_exists(return_port) && return_port != -1) ? return_port : sFutaPortrait1;
}

function func_get_portrait_boobs(arg0, arg1)
{
    var return_port = sFutaPortrait1;
    switch (arg1)
    {
        case 0:
            if (outfit_toggle == false)
            {
                switch (arg0)
                {
                    case sFutaMatingPress:
                        return_port = sFutaPortrait1;
                        break;
                    case sFutaMatingPressDevil:
                        return_port = sFutaPortraitDevil;
                        break;
                    case sFutaMatingPressSlime:
                        return_port = sFutaPortraitSlime;
                        break;
                    case sFutaMatingPressAndroid:
                        return_port = sFutaPortraitAndroid;
                        break;
                    case sFutaMatingPressAlien:
                        return_port = sFutaPortraitAlien;
                        break;
                    case sFutaMatingPressClown:
                        return_port = sFutaPortraitClown;
                        break;
                    case sFutaMatingBunny:
                        return_port = sFutaPortraitBunny;
                        break;
                    case sFutaMatingFurry:
                        return_port = sFutaPortraitFurry;
                        break;
                    case custom_mating_press:
                        return_port = (sprite_exists(custom_portrait) && custom_portrait != -1) ? custom_portrait : sFutaPortrait1;
                        break;
                    case legacy_custom_mating_press:
                        return_port = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
                        break;
                }
            }
            else if (outfit_sprite == sOutfitMatingPress1)
            {
                return_port = sFutaPortrait2;
            }
            else if (outfit_sprite == sOutfitMatingPress2)
            {
                return_port = sFutaPortrait4;
            }
            else if (outfit_sprite == sOutfitMatingPress3)
            {
                return_port = sFutaPortrait3;
            }
            break;
        case 1:
            if (wife_outfit_toggle == false)
            {
                switch (arg0)
                {
                    case sWifeMatingPress:
                        return_port = sFutaPortrait1;
                        break;
                    case sWifeMatingPressDevil:
                        return_port = sFutaPortraitDevil;
                        break;
                    case sWifeMatingPressSlime:
                        return_port = sFutaPortraitSlime;
                        break;
                    case sWifeMatingPressAndroid:
                        return_port = sFutaPortraitAndroid;
                        break;
                    case sWifeMatingPressFurry:
                        return_port = sFutaPortraitFurry;
                        break;
                    case custom_wife_mating_press:
                        return_port = (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1) ? legacy_custom_wife_portrait : ((sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1) ? custom_wife_portrait : sFutaPortrait1);
                        break;
                }
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit1)
            {
                return_port = sFutaPortrait2;
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit2)
            {
                return_port = sFutaPortrait4;
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit3)
            {
                return_port = sFutaPortrait3;
            }
            break;
    }
    if (return_port <= 0 || !sprite_exists(return_port))
    {
        return_port = sFutaPortrait1;
    }
    return (sprite_exists(return_port) && return_port != -1) ? return_port : sFutaPortrait1;
}

function func_get_alt_boob_sprite(arg0)
{
    var _frame = futa_boob_index - 1;
    if (_frame < 0)
    {
        _frame = 0;
    }
    if (arg0 == sFutaMatingPressAlien)
    {
        return [sFutaPortraitAltBoobsAlien, _frame];
    }
    if (arg0 == sFutaMatingPressAndroid)
    {
        return [sFutaPortraitAltBoobsAndroid, _frame];
    }
    if (arg0 == sFutaMatingPressDevil)
    {
        return [sFutaPortraitAltBoobsDevil, _frame];
    }
    if (arg0 == sFutaMatingPressSlime)
    {
        return [sFutaPortraitAltBoobsSlime, _frame];
    }
    return [sFutaPortraitAltBoobs1, _frame];
}

function func_get_portrait_outfit(arg0, arg1)
{
    var return_port = sFutaPortraitOutfit1;
    switch (arg1)
    {
        case 0:
            switch (arg0)
            {
                case sOutfitMatingPress1:
                    return_port = sFutaPortraitOutfit1;
                    break;
                case sOutfitMatingPress2:
                    return_port = sFutaPortraitOutfit3;
                    break;
                case sOutfitMatingPress3:
                    return_port = sFutaPortraitOutfit2;
                    break;
                case sFutaMatingPressClownClothes:
                    return_port = sFutaPortraitClownClothes;
                    break;
                case sFutaMatingBunnyClothes:
                    return_port = sFutaPortraitBunnyClothes;
                    break;
            }
            break;
        case 1:
            switch (arg0)
            {
                case sWifeNormalCowgirlOutfit1:
                    return_port = sFutaPortraitOutfit1;
                    break;
                case sWifeNormalCowgirlOutfit2:
                    return_port = sFutaPortraitOutfit3;
                    break;
                case sWifeNormalCowgirlOutfit3:
                    return_port = sFutaPortraitOutfit2;
                    break;
            }
            break;
    }
    return return_port;
}

function func_get_portrait_iris(arg0)
{
    var return_port = sFutaPortrait1Iris;
    switch (arg0)
    {
        case sFutaPortrait1Eyes:
            return_port = sFutaPortrait1Iris;
            break;
        case sFutaPortrait2Eyes:
            return_port = sFutaPortrait2Iris;
            break;
        case sFutaPortrait3Eyes:
            return_port = sFutaPortrait3Iris;
            break;
        case sFutaPortrait4Eyes:
            return_port = sFutaPortrait4Iris;
            break;
        case sFutaPortraitDevilEyes:
            return_port = sFutaPortraitDevilIris;
            break;
        case sFutaPortraitAndroidEyes:
            return_port = sFutaPortraitAndroidIris;
            break;
        case sFutaPortraitSlimeEyes:
            return_port = sFutaPortraitSlimeIris;
            break;
        case sFutaPortraitFurryEyes:
            return_port = sFutaPortraitFurryIris;
            break;
        case sFutaPortraitAlienEyes:
            return_port = -1;
            break;
        case sFutaPortraitBunnyEyes:
            return_port = sFutaPortraitBunnyIris;
            break;
    }
    return return_port;
}

comment = "functions for switching between mating press and cowgirl(s)";

function func_get_reverse_cowgirl(arg0)
{
    var return_sprite = sFutaCowgirl;
    switch (arg0)
    {
        case sFutaMatingPress:
            return_sprite = sFutaCowgirl;
            break;
        case sFutaMatingPress2:
            return_sprite = sFutaCowgirl2;
            break;
        case sFutaMatingPress3:
            return_sprite = sFutaCowgirl3;
            break;
        case sFutaMatingPress4:
            return_sprite = sFutaCowgirl4;
            break;
        case sFutaMatingPressDevil:
            return_sprite = sFutaCowgirlDevil;
            break;
        case sFutaMatingPressSlime:
            return_sprite = sFutaCowgirlSlime;
            break;
        case sFutaMatingPressAndroid:
            return_sprite = sFutaCowgirlAndroid;
            break;
        case sFutaMatingFurry:
            return_sprite = sFutaCowgirlFurry;
            break;
        case sFutaMatingPressAlien:
            return_sprite = sFutaCowgirlAlien;
            break;
        case sFutaMatingPressClown:
            return_sprite = sFutaCowgirlClown;
            break;
        case sFutaMatingBunny:
            return_sprite = sFutaCowgirlBunny;
            break;
        case sFutaMatingPressKnottedHorse:
            return_sprite = sFutaCowgirlKnottedHorse;
            break;
        case custom_mating_press:
            return_sprite = custom_cowgirl;
            break;
        case legacy_custom_mating_press:
            return_sprite = legacy_custom_cowgirl;
            break;
    }
    return return_sprite;
}

function func_get_deepthroat(arg0)
{
    var return_sprite = sFutaDeepthroat;
    switch (arg0)
    {
        case sFutaMatingPress:
            return_sprite = sFutaDeepthroat;
            break;
        case sFutaMatingPress2:
            return_sprite = sFutaDeepthroat2;
            break;
        case sFutaMatingPress3:
            return_sprite = sFutaDeepthroat3;
            break;
        case sFutaMatingPress4:
            return_sprite = sFutaDeepthroat4;
            break;
        case sFutaMatingPressDevil:
            return_sprite = sFutaDeepthroatDevil;
            break;
        case sFutaMatingPressSlime:
            return_sprite = sFutaDeepthroatSlime;
            break;
        case sFutaMatingPressAndroid:
            return_sprite = sFutaDeepthroatAndroid;
            break;
        case sFutaMatingPressAlien:
            return_sprite = sFutaDeepthroatAlien;
            break;
        case sFutaMatingPressClown:
            return_sprite = sFutaDeepthroatClown;
            break;
        case sFutaMatingFurry:
            return_sprite = sFutaDeepthroatFurry;
            break;
        case sFutaMatingBunny:
            return_sprite = sFutaDeepthroatBunny;
            break;
        default:
            if (arg0 == custom_mating_press)
            {
                return_sprite = custom_futa_deepthroat;
            }
            else if (arg0 == legacy_custom_mating_press)
            {
                return_sprite = (custom_deepthroat != -1) ? custom_deepthroat : sFutaDeepthroat;
            }
            break;
    }
    return return_sprite;
}

function func_get_deepthroat_outfit(arg0)
{
    var return_sprite = sFutaDeepthroatClothes1;
    switch (arg0)
    {
        case sOutfitMatingPress1:
            return_sprite = sFutaDeepthroatClothes1;
            break;
        case sOutfitMatingPress2:
            return_sprite = sFutaDeepthroatClothes2;
            break;
        case sOutfitMatingPress3:
            return_sprite = sFutaDeepthroatClothes3;
            break;
        case sFutaMatingPressClownClothes:
            return_sprite = sFutaDeepthroatClownClothes;
            break;
        case sFutaMatingBunnyClothes:
            return_sprite = sFutaDeepthroatBunnyClothes;
            break;
    }
    return return_sprite;
}

function func_get_reverse_cowgirl_outfit(arg0)
{
    var return_sprite = sOutfitCowgirl1;
    switch (arg0)
    {
        case sOutfitMatingPress1:
            return_sprite = sOutfitCowgirl1;
            break;
        case sOutfitMatingPress2:
            return_sprite = sOutfitCowgirl2;
            break;
        case sOutfitMatingPress3:
            return_sprite = sOutfitCowgirl3;
            break;
        case sFutaMatingPressClownClothes:
            return_sprite = sFutaCowgirlClownClothes;
            break;
        case sFutaMatingBunnyClothes:
            return_sprite = sFutaCowgirlBunnyClothes;
            break;
    }
    return return_sprite;
}

function func_get_reverse_cowgirl_bottom(arg0)
{
    var return_sprite = sWifeCowgirl;
    partner_male = false;
    switch (arg0)
    {
        case sWifeMatingPress:
            return_sprite = sWifeCowgirl;
            break;
        case sHusbandMatingPress:
            partner_male = true;
            return_sprite = sHusbandCowgirl;
            break;
        case sWifeMatingPressDevil:
            return_sprite = sWifeCowgirlDevil;
            break;
        case sWifeMatingPressSlime:
            return_sprite = sWifeCowgirlSlime;
            break;
        case sWifeMatingPressAndroid:
            return_sprite = sWifeCowgirlAndroid;
            break;
        case sWifeMatingPressFurry:
            return_sprite = sWifeCowgirlFurry;
            break;
        case custom_wife_mating_press:
            return_sprite = custom_wife_reverse_cowgirl;
            bottom_skin = 16777215;
            break;
    }
    return return_sprite;
}

function func_get_normal_cowgirl_bottom(arg0)
{
    var return_sprite = sWifeNormalCowgirl1;
    partner_male = false;
    switch (arg0)
    {
        case sWifeMatingPress:
            return_sprite = sWifeNormalCowgirl1;
            break;
        case sHusbandMatingPress:
            partner_male = true;
            return_sprite = sWifeNormalCowgirl1;
            break;
        case sWifeMatingPressDevil:
            return_sprite = sWifeNormalCowgirlDevil;
            break;
        case sWifeMatingPressSlime:
            return_sprite = sWifeNormalCowgirlSlime;
            break;
        case sWifeMatingPressAndroid:
            return_sprite = sWifeNormalCowgirlAndroid;
            break;
        case sWifeMatingPressFurry:
            return_sprite = sWifeNormalCowgirlFurry;
            break;
        case custom_wife_mating_press:
            return_sprite = custom_wife_cowgirl;
            bottom_skin = 16777215;
            wife_outfit_toggle = false;
            wife_hair_sprite = custom_wife_cowgirl;
            bottom_hair = 16777215;
            break;
    }
    return return_sprite;
}

function func_get_wife_xray(arg0)
{
    var return_sprite = -1;
    switch (arg0)
    {
        case custom_wife_mating_press:
            if (custom_wife_xray != -1 && sprite_exists(custom_wife_xray))
            {
                return_sprite = custom_wife_xray;
            }
            break;
        case legacy_custom_wife_mating_press:
            if (legacy_custom_wife_xray != -1 && sprite_exists(legacy_custom_wife_xray))
            {
                return_sprite = legacy_custom_wife_xray;
            }
            break;
    }
    return return_sprite;
}

function func_set_top_orgasm_pumps_max()
{
    var base_volume;
    if (giga_pump == false)
    {
        base_volume = ball_size * ball_size * ball_size * cum_volume_modifier;
    }
    else
    {
        base_volume = 6.858999999999999 * cum_volume_modifier;
    }
    var stamina_boost = 1 + (stamina_pill * 0.5);
    var calculated_pumps = 0;
    var width_divisor = clamp(top_penis_width, 1, 1.5);
    switch (top_sprite)
    {
        case sFutaMatingPressAndroid:
            calculated_pumps = ((10 * base_volume) + 15) * stamina_boost;
            break;
        case sFutaMatingPressDevil:
            calculated_pumps = ((10 * base_volume) + (15 * ball_size) + 5) * stamina_boost;
            break;
        case sFutaMatingPressSlime:
            calculated_pumps = ((8 * base_volume) + (5 * cum_volume_modifier) + 5) * stamina_boost;
            break;
        case sFutaMatingFurry:
            calculated_pumps = ((8 * base_volume) + (5 * virility_modifier) + 5) * stamina_boost;
            break;
        default:
            calculated_pumps = ((15 * base_volume) + 10) * stamina_boost;
            break;
    }
    orgasm_pumps_max = user_pumps_max;
    if (pound_town_pill == true)
    {
        orgasm_pumps_max = max(1, round(orgasm_pumps_max * 0.75));
    }
    if (orgasm == false)
    {
        orgasm_pumps = orgasm_pumps_max;
    }
}

function func_wife_pleasure_add(arg0)
{
    wife_pleasure += arg0;
    while (wife_pleasure >= wife_pleasure_threshold)
    {
        wife_pleasure -= wife_pleasure_threshold;
        wife_pleasure_threshold *= 1.25;
        func_wife_climax();
    }
}

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
            body_jiggle = 0.015;
            break;
        case 3:
            bottom_ass_jiggle = 0.4;
            body_jiggle = 0.02;
            break;
        case 4:
            bottom_ass_jiggle = 0.45;
            body_jiggle = 0.03;
            break;
        case 5:
            bottom_ass_jiggle = 0.5;
            body_jiggle = 0.04;
            break;
    }
    var _use_cs_wife_org = cs_wife_pack_index > 0 && ds_list_size(cs_wife_orgasm_list) > 0;
    if (_use_cs_wife_org)
    {
        if (cs_wife_moan_sound != -1 && audio_is_playing(cs_wife_moan_sound))
        {
            audio_stop_sound(cs_wife_moan_sound);
        }
        var _wife_org_list = ds_list_create();
        if (cs_wife_alt_index > 0 && ds_list_size(cs_wife_orgasm_alt_list) > 0)
        {
            ds_list_copy(_wife_org_list, cs_wife_orgasm_alt_list);
        }
        else
        {
            ds_list_copy(_wife_org_list, cs_wife_orgasm_list);
        }
        var _wife_org_pick = ds_list_find_value(_wife_org_list, irandom(ds_list_size(_wife_org_list) - 1));
        cs_wife_moan_sound = oAudioManager.play_voice(_wife_org_pick, 0, random_range(0.9, 1.1), 0.5);
        cs_wife_moan_previous = -1;
        ds_list_destroy(_wife_org_list);
    }
    else
    {
        var _any_climax_playing = audio_is_playing(sndClimax1) || audio_is_playing(sndClimax2) || audio_is_playing(sndClimax3) || audio_is_playing(sndClimax4) || audio_is_playing(sndKissClimax1) || audio_is_playing(sndKissClimax2);
        if (!_any_climax_playing)
        {
            if (partner_male == false)
            {
                if ((kiss_flag || kiss_timer > 0) && cs_wife_kiss_enabled)
                {
                    oAudioManager.play_voice(choose(sndKissClimax1, sndKissClimax2), 99, 1, 1);
                }
                else
                {
                    oAudioManager.play_voice(choose(sndClimax1, sndClimax2, sndClimax3, sndClimax4), 99, 1, 1);
                }
            }
        }
    }
    wife_climax_counter += 1;
    climax_combo += 1;
    var _points = 1000 + (wife_climax_counter * 50);
    var rare_words_chance = irandom(9);
    switch (wife_climax_type)
    {
        case "plapping":
            if (rare_words_chance == 0)
            {
                ds_list_insert(score_combo_mods, 0, rare_plapping_climax_words[irandom(array_length(rare_plapping_climax_words) - 1)]);
            }
            else
            {
                ds_list_insert(score_combo_mods, 0, plapping_climax_words[irandom(array_length(plapping_climax_words) - 1)]);
            }
            if (oDialogueManager.top_dialogue_timer < 1 && oDialogueManager.wife_dialogue_timer < 1)
            {
                oDialogueManager.trigger_dialogue("top_react_wife_plapping_climax", "wife_plapping_climax", 120, 1);
            }
            break;
        case "kissing":
            _points = 500 + (wife_climax_counter * 25);
            if (rare_words_chance == 0)
            {
                ds_list_insert(score_combo_mods, 0, kissing_climax_words[irandom(array_length(kissing_climax_words) - 1)]);
            }
            else
            {
                ds_list_insert(score_combo_mods, 0, rare_kissing_climax_words[irandom(array_length(rare_kissing_climax_words) - 1)]);
            }
            if (oDialogueManager.top_dialogue_timer < 1 && oDialogueManager.wife_dialogue_timer < 1)
            {
                oDialogueManager.trigger_dialogue("top_react_wife_kissing_climax", "wife_kissing_climax", 120, 1);
            }
            break;
        case "breeding":
            if (rare_words_chance == 0)
            {
                ds_list_insert(score_combo_mods, 0, rare_breeding_climax_words[irandom(array_length(rare_breeding_climax_words) - 1)]);
            }
            else
            {
                ds_list_insert(score_combo_mods, 0, breeding_climax_words[irandom(array_length(breeding_climax_words) - 1)]);
            }
            if (oDialogueManager.top_dialogue_timer < 1 && oDialogueManager.wife_dialogue_timer < 1)
            {
                oDialogueManager.trigger_dialogue("top_react_wife_breeding_climax", "wife_breeding_climax", 120, 1);
            }
            break;
    }
    var count_normal = clamp(wife_climax_counter / 20, 0, 1);
    var normalized_stat = (wife_reproductive_response - 0.8) / 0.6;
    var stat_bonus = normalized_stat * 0.5;
    if (machinegun_toggle == true && shot_queue > 0)
    {
        mg_score_pool += _points;
    }
    else
    {
        futa_score += _points;
        score_combo += _points;
        score_combo_scale = 1.5;
        score_combo_timer = 300;
    }
    while (ds_list_size(score_combo_mods) > max_combo_display)
    {
        ds_list_delete(score_combo_mods, ds_list_size(score_combo_mods) - 1);
    }
}

mp_cum_tip_index = 0;

function func_mp_next_tip()
{
    if (diphallia_pill == false)
    {
        return 0;
    }
    mp_cum_tip_index = 1 - mp_cum_tip_index;
    return mp_cum_tip_index;
}

function func_mp_cum_tip_offset(arg0 = 0)
{
    var _tip_twin = diphallia_pill == true && arg0 == 1;
    var _tip_rot = 5 - (5 * thrust);
    if (sex_position == 3)
    {
        var _dt_scale_y = (image_yscale - top_breath) * top_penis_length;
        var _dt_y = (38 + (20 * (5 * top_breath))) - (thrust * 16);
        var _dt_twin_off = _tip_twin ? -8 : 0;
        return _dt_y + (79 * _dt_scale_y) + _dt_twin_off + custom_cum_y_offset + custom_cum_y_offset_dt;
    }
    if (sex_position > 0)
    {
        var _cg_adj_ass = (top_ass_size > 1) ? (1 + ((top_ass_size - 1) * 0.5)) : top_ass_size;
        var _cg_clamped = min(_cg_adj_ass, 0.85);
        var _cg_drift = (((_cg_clamped - 1) > 0) ? ((_cg_clamped - 1) * 13) : ((_cg_clamped - 1) * 5)) * 0.5;
        var _cg_up = max(0, _cg_adj_ass - 0.85) * 50;
        var _cg_gen = _cg_drift - _cg_up;
        var _cg_scale_y = (image_yscale - top_breath) * (1 + (0.1 * insert_thrust)) * top_penis_length * custom_cowgirl_scale;
        var _cg_py = (y + (20 - (4 * thrust)) + 10 + _cg_gen) - (_tip_twin ? 8 : 0);
        var _cg_rot = 0;
        if (diphallia_pill == true)
        {
            _cg_rot = _tip_twin ? _tip_rot : -_tip_rot;
        }
        return (_cg_py - (dcos(_cg_rot) * 57 * _cg_scale_y) - y) + custom_cum_y_offset + custom_cum_y_offset_cg;
    }
    var _mp_scale_y = (image_yscale - top_breath) * top_penis_length * custom_mating_press_scale;
    return ((79 * _mp_scale_y) - (thrust * 32) - (_tip_twin ? 8 : 0)) + custom_cum_y_offset + custom_cum_y_offset_mp;
}

function func_mp_cum_tip_x(arg0 = 0)
{
    if (diphallia_pill == false)
    {
        return 0;
    }
    var _tx_twin = arg0 == 1;
    var _tx_rot = 5 - (5 * thrust);
    if (sex_position == 3)
    {
        var _tx_len = top_penis_length;
        return _tx_twin ? (dsin(-_tx_rot) * 80 * _tx_len) : (dsin(_tx_rot) * 69 * _tx_len);
    }
    if (sex_position == 0)
    {
        var _tx_len = top_penis_length * custom_mating_press_scale;
        return _tx_twin ? (dsin(-_tx_rot) * 80 * _tx_len) : (dsin(_tx_rot) * 69 * _tx_len);
    }
    var _tx_scale_y = (image_yscale - top_breath) * (1 + (0.1 * insert_thrust)) * top_penis_length * custom_cowgirl_scale;
    return _tx_twin ? (-dsin(_tx_rot) * 66 * _tx_scale_y) : (dsin(_tx_rot) * 53 * _tx_scale_y);
}

function func_ovulate()
{
    var obj = instance_create_depth(x, y, depth - 1, oOvulation);
    ovum_count += 1;
}

function func_impregnation()
{
    var impreg_range = 99;
    var impregnation_chance = random(impreg_range);
    var virility_factor = (virility_modifier - (contraceptive_pill * 1.3)) * (stat_pump_volume * 4);
    var multipreg_chance = base_multipreg_chance;
    var fertilization_count = 0;
    var fertilization_divisor = 1;
    var fertilization_maxed = false;
    while (fertilization_count < ovum_count)
    {
        multipreg_chance /= fertilization_divisor;
        if (impregnation_chance > (impreg_range - (multipreg_chance * virility_factor)) && fertilization_maxed == false)
        {
            fertilization_count += 1;
            fertilization_divisor *= 2;
            if (fertilization_count > fertilization_max)
            {
                fertilization_maxed = true;
                fertilization_count = fertilization_max;
            }
        }
        else
        {
            break;
        }
    }
    if (fertilization_count > 0)
    {
        ovum_count -= fertilization_count;
        impregnate = true;
        impregnation_counter += fertilization_count;
        impregnation_combo += fertilization_count;
        futa_score += (2500 * fertilization_count);
        score_combo += (2500 * fertilization_count);
        score_combo_scale = 1.5;
        score_combo_timer = 240;
        var wife_climax_pleasure = (1 - power(0.8, fertilization_count)) * (50 + random(50 * wife_reproductive_response));
        wife_climax_type = "breeding";
        func_wife_pleasure_add(wife_climax_pleasure);
        var char_suffix = "";
        switch (top_sprite)
        {
            case sFutaMatingFurry:
                char_suffix = "_furry";
                break;
            case sFutaMatingPressDevil:
                char_suffix = "_devil";
                break;
            case sFutaMatingPressAndroid:
                char_suffix = "_android";
                break;
            case sFutaMatingPressSlime:
                char_suffix = "_slime";
                break;
            case custom_mating_press:
                char_suffix = "";
                break;
        }
        if (oDialogueManager.top_dialogue_timer < 1 || oDialogueManager.wife_dialogue_timer < 1)
        {
            var is_drip = drip_repeat != 0;
            var is_pill = contraceptive_pill;
            var lover_keys = [];
            var wife_keys = [];
            if (is_pill)
            {
                if (is_drip)
                {
                    array_push(lover_keys, "drip_contraceptive_impregnate" + char_suffix, "drip_contraceptive_impregnate");
                    array_push(wife_keys, "wife_drip_contraceptive_impregnate" + char_suffix, "wife_drip_contraceptive_impregnate");
                }
                array_push(lover_keys, "contraceptive_impregnate" + char_suffix, "contraceptive_impregnate");
                array_push(wife_keys, "wife_contraceptive_impregnate" + char_suffix, "wife_contraceptive_impregnate");
            }
            if (is_drip)
            {
                array_push(lover_keys, "drip_impregnate" + char_suffix, "drip_impregnate");
                array_push(wife_keys, "wife_drip_impregnate" + char_suffix, "wife_drip_impregnate");
            }
            array_push(lover_keys, "impregnate" + char_suffix, "impregnate");
            array_push(wife_keys, "wife_impregnate" + char_suffix, "wife_impregnate");
            var final_lover = "";
            var final_wife = "";
            for (var i = 0; i < array_length(lover_keys); i++)
            {
                if (oDialogueManager.pick_from_dialogue_json(lover_keys[i]) != "")
                {
                    final_lover = lover_keys[i];
                    break;
                }
            }
            for (var i = 0; i < array_length(wife_keys); i++)
            {
                if (oDialogueManager.pick_from_dialogue_json(wife_keys[i]) != "")
                {
                    final_wife = wife_keys[i];
                    break;
                }
            }
            oDialogueManager.trigger_dialogue(final_lover, final_wife, 180, 0);
        }
        for (var i = 0; i < fertilization_count; i++)
        {
            var obj = instance_create_depth(x, y, depth - (impregnation_counter - i), oImpregnate);
            obj.cum_color = cum_color;
        }
        var word_list = breeding_words;
        if (fertilization_count == 2)
        {
            word_list = breeding_words_2;
        }
        if (fertilization_count == 3)
        {
            word_list = breeding_words_3;
        }
        if (fertilization_count == 8)
        {
            word_list = breeding_words_8;
        }
        if (fertilization_count == 11)
        {
            word_list = breeding_words_11;
        }
        if (fertilization_count == 13)
        {
            word_list = breeding_words_13;
        }
        if (fertilization_maxed == false)
        {
            if (fertilization_count == 1 || word_list != breeding_words)
            {
                ds_list_insert(score_combo_mods, 0, word_list[irandom(array_length(word_list) - 1)]);
            }
            else
            {
                ds_list_insert(score_combo_mods, 0, word_list[irandom(array_length(word_list) - 1)] + " x" + string(fertilization_count));
            }
        }
        else if (fertilization_count == 1 || word_list != breeding_words)
        {
            ds_list_insert(score_combo_mods, 0, word_list[irandom(array_length(word_list) - 1)] + "!");
        }
        else
        {
            ds_list_insert(score_combo_mods, 0, word_list[irandom(array_length(word_list) - 1)] + " x" + string(fertilization_count) + "!");
        }
        milestone_index = -1;
        for (var i = 0; i < array_length(breeding_milestone_count); i++)
        {
            if (impregnation_counter >= breeding_milestone_count[i])
            {
                milestone_index = i;
            }
            else
            {
                break;
            }
        }
        if (milestone_index > last_milestone_index)
        {
            var milestone_text = breeding_milestone_text[milestone_index];
            ds_list_insert(score_combo_mods, 0, "=" + milestone_text + "=");
            last_milestone_index = milestone_index;
        }
        while (ds_list_size(score_combo_mods) > max_combo_display)
        {
            ds_list_delete(score_combo_mods, ds_list_size(score_combo_mods) - 1);
        }
    }
    else if (drip_repeat == 1)
    {
        if (oDialogueManager.top_dialogue_timer < 1 && oDialogueManager.wife_dialogue_timer < 1)
        {
            oDialogueManager.trigger_dialogue("drip", "wife_drip", 120, 1);
        }
    }
    score_combo += (100 + (5 * score_combo_mult));
    futa_score += (100 + (5 * score_combo_mult));
    score_combo_mult += 1;
    score_combo_timer = 240;
    score_combo_scale = 1.5;
}

function func_reset_pills()
{
    mega_sperm_pill = false;
    equine_pill = false;
    knotted_pill = false;
    extra_thick_pill = false;
    diphallia_pill = false;
    ovulation_pill = false;
    stamina_pill = false;
    leaky_pill = false;
    hyper_breeding_pill = false;
    blockage_pill = false;
    quickshot_pill = false;
    reverse_speed_pill = false;
    edge_addict_pill = false;
    premature_pill = false;
    edge_lover_pill = false;
    pound_town_pill = false;
    livestream_pill = false;
    growth_cascade_pill = false;
    savor_pill = false;
    if (three_pump_champ_pill)
    {
        user_pumps_max = three_pump_champ_saved_pumps;
        cum_volume_modifier /= 3;
    }
    three_pump_champ_pill = false;
}

comment = "arg0 is an array of items, arg1 is an array of weights. Returns an item with probability determined by the weights.";

function func_weighted_pick(arg0, arg1)
{
    var total = 0;
    for (var i = 0; i < array_length(arg1); i++)
    {
        total += arg1[i];
    }
    var r = random(total);
    for (var i = 0; i < array_length(arg0); i++)
    {
        r -= arg1[i];
        if (r <= 0)
        {
            return arg0[i];
        }
    }
    return arg0[array_length(arg0) - 1];
}

comment = "x, y, radius, stats_array, labels_array, max_labels_array, ring_count, color";

function draw_radar_chart(arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7)
{
    var count = array_length(arg3);
    if (count < 3)
    {
        exit;
    }
    var step_deg = 360 / count;
    var outer = array_create(count);
    for (var i = 0; i < count; i++)
    {
        var angle_deg = (i * step_deg) + 90;
        var ox = arg0 + lengthdir_x(arg2, angle_deg);
        var oy = arg1 + lengthdir_y(arg2, angle_deg);
        outer[i] = [ox, oy, angle_deg];
    }
    var prev_color = draw_get_color();
    var prev_alpha = draw_get_alpha();
    draw_set_alpha(0.75);
    draw_set_color(make_color_rgb(180, 180, 180));
    for (var r = 1; r <= arg6; r++)
    {
        var scale = r / arg6;
        for (var i = 0; i < count; i++)
        {
            var next = (i + 1) % count;
            var sx = arg0 + ((outer[i][0] - arg0) * scale);
            var sy = arg1 + ((outer[i][1] - arg1) * scale);
            var nx = arg0 + ((outer[next][0] - arg0) * scale);
            var ny = arg1 + ((outer[next][1] - arg1) * scale);
            draw_line(sx, sy, nx, ny);
        }
    }
    draw_set_alpha(1);
    draw_set_color(make_color_rgb(160, 160, 160));
    for (var i = 0; i < count; i++)
    {
        draw_line(arg0, arg1, outer[i][0], outer[i][1]);
    }
    var points = array_create(count);
    for (var i = 0; i < count; i++)
    {
        var raw = real(arg3[i]);
        var capped = clamp(raw, 0, 1);
        var px = arg0 + ((outer[i][0] - arg0) * capped);
        var py = arg1 + ((outer[i][1] - arg1) * capped);
        points[i] = [px, py, raw >= 1];
    }
    draw_set_alpha(0.45);
    draw_set_color(arg7);
    for (var i = 0; i < count; i++)
    {
        var next = (i + 1) % count;
        draw_triangle(arg0, arg1, points[i][0], points[i][1], points[next][0], points[next][1], false);
    }
    draw_set_alpha(1);
    for (var i = 0; i < count; i++)
    {
        var next = (i + 1) % count;
        draw_line(points[i][0], points[i][1], points[next][0], points[next][1]);
        if (points[i][2])
        {
            draw_set_color(c_yellow);
        }
        else
        {
            draw_set_color(c_white);
        }
        draw_circle(points[i][0], points[i][1], 1, false);
        draw_set_color(c_white);
    }
    if (is_array(arg4))
    {
        var label_offset = 2;
        var bottom_labels = [];
        if ((count % 2) == 0)
        {
            bottom_labels[0] = count div 2;
        }
        else
        {
            bottom_labels[0] = (count - 1) div 2;
            bottom_labels[1] = (count + 1) div 2;
        }
        for (var i = 0; i < count; i++)
        {
            if (i >= array_length(arg4))
            {
                break;
            }
            var text = arg4[i];
            if (points[i][2])
            {
                if (is_array(arg5))
                {
                    text = arg5[i];
                }
                draw_set_color(c_yellow);
            }
            else
            {
                draw_set_color(prev_color);
            }
            var dx = outer[i][0] - arg0;
            var dy = outer[i][1] - arg1;
            var len = sqrt(sqr(dx) + sqr(dy));
            if (len == 0)
            {
                len = 1;
            }
            var ux = dx / len;
            var uy = dy / len;
            var lx = outer[i][0] + (ux * label_offset) + 1;
            var ly = outer[i][1] + (uy * label_offset) + 1;
            if (array_contains(bottom_labels, i))
            {
                draw_set_halign(fa_center);
            }
            else if (dx > 0)
            {
                draw_set_halign(fa_left);
            }
            else if (dx < 0)
            {
                draw_set_halign(fa_right);
            }
            else
            {
                draw_set_halign(fa_center);
            }
            if (dy < 0)
            {
                draw_set_valign(fa_bottom);
            }
            else if (dy > 0)
            {
                draw_set_valign(fa_top);
            }
            else
            {
                draw_set_valign(fa_middle);
            }
            draw_text(lx, ly, text);
        }
        draw_set_halign(fa_left);
        draw_set_valign(fa_middle);
    }
    draw_set_color(prev_color);
    draw_set_alpha(prev_alpha);
}

function func_reset_sex_stats()
{
    comment = "flags and states";
    insert = false;
    orgasm = false;
    knotted = false;
    wife_climax = false;
    wife_climax_stage = false;
    impregnate = false;
    condom = false;
    broken_condom = false;
    has_paused_thrust = false;
    reenter_flag = false;
    giga_pump = false;
    func_reset_pills();
    if (top_sprite == custom_mating_press || top_sprite == legacy_custom_mating_press)
    {
        func_apply_custom_futa_stats();
    }
    comment = "timers and progress";
    sex_progress = 0;
    deep_pause_timer = 0;
    knotted_timer = -1;
    orgasm_timer = -1;
    orgasm_pumps = -1;
    knot_timer = 0;
    savor_timer = -1;
    savor_pull_count = 0;
    savor_smooth_depth = 0;
    drip_repeat_timer = 0;
    reenter_timer = 0;
    edge_snap_timer = 0;
    desperate_edge_timer = 0;
    comment = "counters and scores";
    deep_clench_count = 0;
    knot_attempt = 0;
    knot_state = 0;
    futa_score = 0;
    loads = 0;
    wife_pleasure = 0;
    wife_climax_counter = 0;
    impregnation_counter = 0;
    drip_repeat = 0;
    desperate_edge_state = 0;
    ball_pulse_count = 0;
    comment = "physics and volume";
    clench_ratio = 0;
    fill_amount = 0;
    condom_volume = 0;
    condom_size = 0;
    humping_prev = 0;
    current_hump_pullback = 0.1;
    hump_ratio = 0;
    edge_charge = 0;
    comment = "pacing reset";
    if (slap_boost > 0)
    {
        slap_boost = 0;
    }
    alarm[0] = 1;
    comment = "instance cleanup";
    oBackground.cum = false;
    var objects_to_clear = [oCum, oCondom, oImpregnate, oBucket];
    for (var i = 0; i < array_length(objects_to_clear); i++)
    {
        with (objects_to_clear[i])
        {
            instance_destroy();
        }
    }
}

function spawn_condom_handler(arg0)
{
    oAudioManager.play_sfx(sndCondomOff, 0, 1, 1);
    var spawn_count = (diphallia_pill == true) ? 2 : 1;
    var split_size = condom_size;
    var split_vol = condom_volume / spawn_count;
    var split_liters = stat_liters / spawn_count;
    var split_sperm = stat_sperm_cell / spawn_count;
    for (i = 0; i < spawn_count; i++)
    {
        var condom_spawn = instance_create_depth(random_range(100, room_width - 100), mouse_y + 48, depth - 1, oCondom);
        condom_spawn.side = (spawn_count == 2) ? ((i == 0) ? -1 : 1) : 0;
        condom_spawn.condom_size = split_size;
        condom_spawn.condom_volume = split_vol;
        condom_spawn.stat_liters = split_liters;
        condom_spawn.stat_sperm_cell = split_sperm;
        condom_spawn.condom_color = condom_color;
        condom_spawn.stat_duration = stat_duration;
        condom_spawn.stat_pumps = stat_pumps;
        condom_spawn.cum_color = cum_color;
        if (top_sprite == sFutaMatingPressClown)
        {
            condom_spawn.sprite_index = sFutaCondomBalloonAnimal;
            if (condom_spawn.condom_size > 1.25)
            {
                condom_spawn.condom_size /= 2;
                condom_spawn.image_index = 3;
            }
            else
            {
                condom_spawn.image_index = 2;
            }
        }
        else if (condom_spawn.condom_size > 1.25)
        {
            condom_spawn.condom_size /= 2;
            condom_spawn.image_index = 6;
        }
        if (arg0)
        {
            condom_spawn.grab = true;
        }
    }
    if (condom_volume > 0)
    {
        oAudioManager.play_sfx(choose(sndSlosh1, sndSlosh2, sndSlosh3), 0, 1.25 - (0.25 * condom_size), 0.75);
    }
    condom_size = 0;
    condom_volume = 0;
    stat_liters = 0;
    stat_sperm_cell = 0;
    stat_duration = 0;
    stat_pumps = 0;
    condom = false;
    broken_condom = false;
}

sprite_list = [sFutaCondom, sFutaCondom2, sFutaCowgirl, sFutaCowgirlAndroid, sFutaCowgirlDevil, sFutaCowgirlFurry, sFutaCowgirlKnottedHorse, sFutaCowgirlSlime, sFutaMatingFurry, sFutaMatingPress, sFutaMatingPressAndroid, sFutaMatingPressDevil, sFutaMatingPressKnottedHorse, sFutaMatingPressSlime, sFutaXray, sFutaXrayAndroid, sFutaXrayHorse, sFutaXrayKnotted, sFutaXrayKnottedHorse, sFutaXraySlime];

function func_texture_pack_replace(arg0)
{
    for (var i = 0; i < array_length(sprite_list); i++)
    {
        var _filename = "custom_stuff/texture_packs/" + arg0 + "/" + sprite_get_name(sprite_list[i]) + ".png";
        if (!file_exists(_filename))
        {
            _filename = "texture_packs/" + arg0 + "/" + sprite_get_name(sprite_list[i]) + ".png";
        }
        if (file_exists(_filename))
        {
            sprite_replace(sprite_list[i], _filename, global.sprite_backup[i].frames, false, false, global.sprite_backup[i].xorig, global.sprite_backup[i].yorig);
        }
        else if (i < array_length(global.sprite_backup))
        {
            sprite_assign(sprite_list[i], global.sprite_backup[i].sprite);
        }
    }
}

function func_texture_pack_backup_vanilla()
{
    global.sprite_backup = [];
    for (var i = 0; i < array_length(sprite_list); i += 1)
    {
        var _spr_item = sprite_list[i];
        var _entry = 
        {
            sprite: _spr_item,
            frames: sprite_get_number(_spr_item),
            xorig: sprite_get_xoffset(_spr_item),
            yorig: sprite_get_yoffset(_spr_item)
        };
        array_push(global.sprite_backup, _entry);
    }
}

function func_list_texture_packs()
{
    var _dir = "custom_stuff/texture_packs/";
    var _file = tc_ff_first(_dir + "*", 16);
    if (_file == "")
    {
        tc_ff_close();
        _dir = "texture_packs/";
        _file = tc_ff_first(_dir + "*", 16);
    }
    var _packs = [];
    var has_default = false;
    while (_file != "")
    {
        if (_file != "." && _file != "..")
        {
            array_push(_packs, _file);
            if (_file == "default")
            {
                has_default = true;
            }
        }
        _file = tc_ff_next();
    }
    tc_ff_close();
    if (!has_default)
    {
        array_insert(_packs, 0, "default");
    }
    if (array_length(_packs) == 0)
    {
        _packs = ["default"];
    }
    texture_packs = _packs;
    texture_pack_number = 0;
    chosen_texture_pack = "default";
}

function find_texture_pack_index(arg0)
{
    var found_texture_pack_index = 0;
    for (i = 0; i < array_length(texture_packs); i++)
    {
        if (texture_packs[i] == arg0)
        {
            found_texture_pack_index = i;
            break;
        }
    }
    chosen_texture_pack = (found_texture_pack_index == 0) ? texture_packs[0] : texture_packs[found_texture_pack_index];
    texture_pack_number = found_texture_pack_index;
}

func_texture_pack_backup_vanilla();
func_list_texture_packs();

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
    ini_write_real("values", "cum_shot_mult", cum_shot_mult);
    ini_write_real("features", "hearts_toggle", hearts_toggle);
    ini_write_real("features", "frustration_toggle", frustration_toggle);
    ini_write_real("features", "rand_pumps_toggle", rand_pumps_toggle);
    ini_write_real("features", "pop_sound_toggle", global.pop_sound_toggle);
    ini_write_real("features", "kiss_toggle", kiss_toggle);
    ini_write_real("features", "drip_toggle", drip_toggle);
    ini_write_real("features", "cum_batching_toggle", cum_batching_toggle);
    ini_write_real("features", "custom_clench_toggle", custom_clench_toggle);
    ini_write_real("features", "continuous_toggle", continuous_toggle);
    ini_write_string("features", "texture_pack", chosen_texture_pack);
    ini_write_string("features", "dialogue_pack", oDialogueManager.chosen_dialogue);
    ini_write_real("features", "dialogue_toggle", oDialogueManager.dialogue_toggle);
    ini_write_real("features", "char_dialogue_toggle", char_dialogue_toggle);
    ini_write_real("dialogue", "dialogue_display_index", global.dialogue_display_index);
    ini_write_real("dialogue", "speaker_type_index", global.speaker_type_index);
    ini_write_real("dialogue", "dialogue_cooldown", oDialogueManager.dialogue_cooldown);
    ini_write_real("dialogue", "dialogue_additional_duration", global.dialogue_additional_duration);
    ini_write_real("dialogue", "text_scale_l", text_scale_l);
    ini_write_real("dialogue", "text_scale_w", text_scale_w);
    ini_write_real("dialogue", "max_lover_dialogue_width", max_lover_dialogue_width);
    ini_write_real("dialogue", "max_wife_dialogue_width", max_wife_dialogue_width);
    ini_write_real("dialogue", "top_dlg_x", top_dlg_x);
    ini_write_real("dialogue", "top_dlg_y", top_dlg_y);
    ini_write_real("dialogue", "wife_dlg_x", wife_dlg_x);
    ini_write_real("dialogue", "wife_dlg_y", wife_dlg_y);
    ini_write_real("dialogue", "top_dialogue_color", oDialogueManager.top_dialogue_color);
    ini_write_real("dialogue", "wife_dialogue_color", oDialogueManager.wife_dialogue_color);
    ini_write_real("bunny_panel", "panel_x", bunny_panel_x_saved);
    ini_write_real("bunny_panel", "panel_y", bunny_panel_y_saved);
    ini_write_real("bunny_panel", "small_x", bunny_small_x_saved);
    ini_write_real("bunny_panel", "small_y", bunny_small_y_saved);
    ini_write_real("custom_sounds", "Futa_index", cs_futa_pack_index);
    ini_write_real("custom_sounds", "Futa_alt_index", cs_futa_alt_index);
    ini_write_real("custom_sounds", "Futa_moan_chance_slow", cs_moan_chance_slow);
    ini_write_real("custom_sounds", "Futa_moan_chance_fast", cs_moan_chance_fast);
    ini_write_real("custom_sounds", "Futa_orgasm_grunt_chance", cs_orgasm_grunt_chance);
    ini_write_real("custom_sounds", "Wife_pack_index", cs_wife_pack_index);
    ini_write_real("custom_sounds", "Wife_alt_index", cs_wife_alt_index);
    ini_write_real("custom_sounds", "Wife_moan_chance_slow", cs_wife_moan_chance_slow);
    ini_write_real("custom_sounds", "Wife_moan_chance_fast", cs_wife_moan_chance_fast);
    ini_write_real("custom_sounds", "Wife_kiss_enabled", cs_wife_kiss_enabled);
    ini_write_real("background", "bg_randomize_colors", bg_randomize_colors);
    ini_write_real("background", "saved_bg_wallpaper", saved_bg_wallpaper);
    ini_write_real("background", "saved_bg_carpet", saved_bg_carpet);
    ini_write_real("background", "saved_bg_trim", saved_bg_trim);
    ini_write_real("background", "saved_bg_dresser", saved_bg_dresser);
    ini_write_real("background", "saved_bg_mattress", saved_bg_mattress);
    ini_write_real("background", "saved_bg_frame", saved_bg_frame);
    ini_write_real("background", "saved_bg_ship", saved_bg_ship);
    ini_write_real("background", "saved_bg_console", saved_bg_console);
    ini_write_real("background", "saved_bg_screen", saved_bg_screen);
    ini_write_real("background", "saved_bg_glass", saved_bg_glass);
    ini_write_real("background", "saved_bg_vip_wall", saved_bg_vip_wall);
    ini_write_real("background", "saved_bg_vip_stage", saved_bg_vip_stage);
    ini_write_real("background", "saved_bg_vip_pole", saved_bg_vip_pole);
    ini_write_real("background", "saved_bg_vip_underwear", saved_bg_vip_underwear);
    ini_write_real("background", "saved_bg_vip_condoms", saved_bg_vip_condoms);
    ini_write_real("background", "saved_bg_vip_lotion", saved_bg_vip_lotion);
    ini_write_real("background", "saved_bg_vip_mattress", saved_bg_vip_mattress);
    ini_write_real("background", "saved_bg_vip_frame", saved_bg_vip_frame);
    ini_write_real("background", "saved_bg_beach_water", saved_bg_beach_water);
    ini_write_real("background", "saved_bg_beach_sky", saved_bg_beach_sky);
    ini_write_real("background", "saved_bg_beach_sun", saved_bg_beach_sun);
    ini_write_real("background", "saved_bg_beach_clouds", saved_bg_beach_clouds);
    ini_write_real("background", "saved_bg_beach_sand", saved_bg_beach_sand);
    ini_write_real("background", "saved_bg_beach_stuff", saved_bg_beach_stuff);
    ini_write_real("background", "saved_bg_office_wall", saved_bg_office_wall);
    ini_write_real("background", "saved_bg_office_floor", saved_bg_office_floor);
    ini_write_real("background", "saved_bg_office_desk", saved_bg_office_desk);
    ini_write_real("background", "saved_bg_dungeon_floor", saved_bg_dungeon_floor);
    ini_write_real("background", "saved_bg_dungeon_wall", saved_bg_dungeon_wall);
    ini_write_real("background", "saved_bg_dungeon_gate", saved_bg_dungeon_gate);
    ini_write_real("background", "saved_bg_dungeon_chest", saved_bg_dungeon_chest);
    ini_write_real("background", "saved_bg_dungeon_chesttrim", saved_bg_dungeon_chesttrim);
    ini_write_real("background", "saved_bg_dungeon_torch", saved_bg_dungeon_torch);
    ini_write_real("background", "saved_bg_dungeon_flame", saved_bg_dungeon_flame);
    ini_write_real("radio", "track_index", radio_track_index);
    ini_write_real("radio", "volume", radio_volume);
    ini_write_real("radio", "shuffle", radio_shuffle);
    ini_write_real("manual", "pumps_speed", manual_pump_speed);
    ini_write_real("manual", "thrust_strength", manual_thrust_strength);
    ini_write_real("manual", "thrust_sensitivity", manual_thrust_sens);
    ini_write_real("manual", "sensitivity", manual_hip_sens);
    ini_write_real("values2", "combo_text_max", combo_text_max);
    ini_write_real("manual", "last_mode", manual_last_mode);
    ini_write_real("manual", "auto_pumps", manual_auto_pumps);
    ini_write_real("values2", "machinegun_toggle", machinegun_toggle);
    ini_write_real("values2", "mg_interval_min", mg_interval_min);
    ini_write_real("values2", "mg_interval_max", mg_interval_max);
    ini_write_real("values2", "mg_spread", mg_spread);
    ini_write_real("values2", "mg_burst_min", mg_burst_min);
    ini_write_real("values2", "mg_burst_max", mg_burst_max);
    ini_write_real("values2", "overflow_delay", overflow_delay);
    ini_write_real("responses", "wife_climax", wife_climax_stamina);
    ini_write_real("responses", "wife_womb", wife_womb_capacity);
    ini_write_real("title", "skip_disclaimer", skip_disclaimer);
    ini_close();
    show_debug_message("saved game");
}

if (file_exists("setting_data.sav"))
{
    var temp_dialogue = -1;
    var temp_texture_pack = -1;
    ini_open("setting_data.sav");
    global.vol_master = ini_read_real("options", "master_audio", 1);
    global.vol_sfx = ini_read_real("options", "sound_sfx", 1);
    global.vol_voice = ini_read_real("options", "voice_fx", 1);
    global.vol_ambient = ini_read_real("options", "ambient_vol", 1);
    global.audio_master_on = ini_read_real("options", "master_audio_toggle", true);
    global.audio_sfx_on = ini_read_real("options", "sound_sfx_toggle", true);
    global.audio_voice_on = ini_read_real("options", "voice_fx_toggle", true);
    skip_disclaimer = bool(ini_read_real("title", "skip_disclaimer", false));
    xray = bool(ini_read_real("options", "xray", true));
    futa_pussy_toggle = ini_read_real("types", "vagina_toggle", true);
    knotting_toggle = ini_read_real("mechanics", "knotting_toggle", true);
    knotted_max_time = ini_read_real("mechanics", "knotted_max_time", 600);
    womb_inflation_toggle = ini_read_real("mechanics", "womb_inflation_toggle", true);
    womb_inflation_scale = ini_read_real("mechanics", "womb_inflation_scale", 1);
    slip_toggle = ini_read_real("mechanics", "slip_toggle", false);
    slip_chance = ini_read_real("mechanics", "slip_chance", 1);
    reenter_toggle = ini_read_real("mechanics", "reenter_toggle", false);
    reenter_max_timer = ini_read_real("mechanics", "reenter_max_timer", false);
    condom_break_toggle = ini_read_real("mechanics", "condom_break_toggle", false);
    condom_break_threshold = ini_read_real("mechanics", "condom_break_threshold", 10);
    pump_delay = ini_read_real("values", "pump_delay", 90);
    cum_shot_mult = ini_read_real("values", "cum_shot_mult", 1);
    stroke_depth = ini_read_real("values", "stroke_depth", 1);
    stroke_speed = ini_read_real("values", "stroke_speed", 1);
    rand_pumps_toggle = ini_read_real("features", "rand_pumps_toggle", false);
    hearts_toggle = ini_read_real("features", "hearts_toggle", true);
    frustration_toggle = ini_read_real("features", "frustration_toggle", true);
    global.pop_sound_toggle = ini_read_real("features", "pop_sound_toggle", true);
    kiss_toggle = ini_read_real("features", "kiss_toggle", 1);
    drip_toggle = ini_read_real("features", "drip_toggle", true);
    cum_batching_toggle = ini_read_real("features", "cum_batching_toggle", false);
    custom_clench_toggle = ini_read_real("features", "custom_clench_toggle", 0);
    continuous_toggle = bool(ini_read_real("features", "continuous_toggle", false));
    temp_texture_pack = ini_read_string("features", "texture_pack", "default");
    temp_dialogue = ini_read_string("features", "dialogue_pack", "aathefintree.json");
    oDialogueManager.dialogue_toggle = ini_read_real("features", "dialogue_toggle", true);
    char_dialogue_toggle = ini_read_real("features", "char_dialogue_toggle", true);
    dialogue_display_index = ini_read_real("dialogue", "dialogue_display_index", 0);
    global.speaker_type_index = ini_read_real("dialogue", "speaker_type_index", 0);
    oDialogueManager.dialogue_cooldown = ini_read_real("dialogue", "dialogue_cooldown", 30);
    global.dialogue_additional_duration = ini_read_real("dialogue", "dialogue_additional_duration", 0);
    text_scale_l = ini_read_real("dialogue", "text_scale_l", 1);
    text_scale_w = ini_read_real("dialogue", "text_scale_w", 1);
    max_lover_dialogue_width = ini_read_real("dialogue", "max_lover_dialogue_width", 200);
    max_wife_dialogue_width = ini_read_real("dialogue", "max_wife_dialogue_width", 200);
    top_dlg_x = ini_read_real("dialogue", "top_dlg_x", 0);
    top_dlg_y = ini_read_real("dialogue", "top_dlg_y", 0);
    wife_dlg_x = ini_read_real("dialogue", "wife_dlg_x", 3);
    wife_dlg_y = ini_read_real("dialogue", "wife_dlg_y", 0);
    oDialogueManager.top_dialogue_color = ini_read_real("dialogue", "top_dialogue_color", 12976127);
    oDialogueManager.wife_dialogue_color = ini_read_real("dialogue", "wife_dialogue_color", 13408767);
    oDialogueManager.current_top_color = oDialogueManager.top_dialogue_color;
    oDialogueManager.current_wife_color = oDialogueManager.wife_dialogue_color;
    bunny_panel_x_saved = ini_read_real("bunny_panel", "panel_x", 300);
    bunny_panel_y_saved = ini_read_real("bunny_panel", "panel_y", 30);
    bunny_small_x_saved = ini_read_real("bunny_panel", "small_x", 300);
    bunny_small_y_saved = ini_read_real("bunny_panel", "small_y", 25);
    cs_futa_pack_index = ini_read_real("custom_sounds", "Futa_index", 0);
    cs_futa_alt_index = ini_read_real("custom_sounds", "Futa_alt_index", 0);
    cs_moan_chance_slow = ini_read_real("custom_sounds", "Futa_moan_chance_slow", 0.4);
    cs_moan_chance_fast = ini_read_real("custom_sounds", "Futa_moan_chance_fast", 0.55);
    cs_orgasm_grunt_chance = ini_read_real("custom_sounds", "Futa_orgasm_grunt_chance", 0.45);
    cs_wife_pack_index = ini_read_real("custom_sounds", "Wife_pack_index", 0);
    cs_wife_alt_index = ini_read_real("custom_sounds", "Wife_alt_index", 0);
    cs_wife_moan_chance_slow = ini_read_real("custom_sounds", "Wife_moan_chance_slow", 0.35);
    cs_wife_moan_chance_fast = ini_read_real("custom_sounds", "Wife_moan_chance_fast", 0.55);
    cs_wife_kiss_enabled = ini_read_real("custom_sounds", "Wife_kiss_enabled", true);
    bg_randomize_colors = ini_read_real("background", "bg_randomize_colors", true);
    saved_bg_wallpaper = ini_read_real("background", "saved_bg_wallpaper", -1);
    saved_bg_carpet = ini_read_real("background", "saved_bg_carpet", -1);
    saved_bg_trim = ini_read_real("background", "saved_bg_trim", -1);
    saved_bg_dresser = ini_read_real("background", "saved_bg_dresser", -1);
    saved_bg_mattress = ini_read_real("background", "saved_bg_mattress", -1);
    saved_bg_frame = ini_read_real("background", "saved_bg_frame", -1);
    saved_bg_ship = ini_read_real("background", "saved_bg_ship", -1);
    saved_bg_console = ini_read_real("background", "saved_bg_console", -1);
    saved_bg_screen = ini_read_real("background", "saved_bg_screen", -1);
    saved_bg_glass = ini_read_real("background", "saved_bg_glass", -1);
    saved_bg_vip_wall = ini_read_real("background", "saved_bg_vip_wall", -1);
    saved_bg_vip_stage = ini_read_real("background", "saved_bg_vip_stage", -1);
    saved_bg_vip_pole = ini_read_real("background", "saved_bg_vip_pole", -1);
    saved_bg_vip_underwear = ini_read_real("background", "saved_bg_vip_underwear", -1);
    saved_bg_vip_condoms = ini_read_real("background", "saved_bg_vip_condoms", -1);
    saved_bg_vip_lotion = ini_read_real("background", "saved_bg_vip_lotion", -1);
    saved_bg_vip_mattress = ini_read_real("background", "saved_bg_vip_mattress", -1);
    saved_bg_vip_frame = ini_read_real("background", "saved_bg_vip_frame", -1);
    saved_bg_beach_water = ini_read_real("background", "saved_bg_beach_water", -1);
    saved_bg_beach_sky = ini_read_real("background", "saved_bg_beach_sky", -1);
    saved_bg_beach_sun = ini_read_real("background", "saved_bg_beach_sun", -1);
    saved_bg_beach_clouds = ini_read_real("background", "saved_bg_beach_clouds", -1);
    saved_bg_beach_sand = ini_read_real("background", "saved_bg_beach_sand", -1);
    saved_bg_beach_stuff = ini_read_real("background", "saved_bg_beach_stuff", -1);
    saved_bg_office_wall = ini_read_real("background", "saved_bg_office_wall", -1);
    saved_bg_office_floor = ini_read_real("background", "saved_bg_office_floor", -1);
    saved_bg_office_desk = ini_read_real("background", "saved_bg_office_desk", -1);
    saved_bg_dungeon_floor = ini_read_real("background", "saved_bg_dungeon_floor", -1);
    saved_bg_dungeon_wall = ini_read_real("background", "saved_bg_dungeon_wall", -1);
    saved_bg_dungeon_gate = ini_read_real("background", "saved_bg_dungeon_gate", -1);
    saved_bg_dungeon_chest = ini_read_real("background", "saved_bg_dungeon_chest", -1);
    saved_bg_dungeon_chesttrim = ini_read_real("background", "saved_bg_dungeon_chesttrim", -1);
    saved_bg_dungeon_torch = ini_read_real("background", "saved_bg_dungeon_torch", -1);
    saved_bg_dungeon_flame = ini_read_real("background", "saved_bg_dungeon_flame", -1);
    radio_track_index = ini_read_real("radio", "track_index", 0);
    radio_volume = ini_read_real("radio", "volume", 1);
    radio_shuffle = ini_read_real("radio", "shuffle", 0);
    manual_pump_speed = clamp(ini_read_real("manual", "pumps_speed", 4), 1, 6);
    manual_thrust_sens = clamp(ini_read_real("manual", "thrust_sensitivity", 0.05), 0.01, 0.15);
    manual_thrust_strength = clamp(ini_read_real("manual", "thrust_strength", 2), 0.5, 3.5);
    manual_hip_sens = clamp(ini_read_real("manual", "sensitivity", 0.5), 0.5, 1);
    combo_text_max = clamp(ini_read_real("values2", "combo_text_max", 0), 0, 16);
    max_combo_display = combo_text_max;
    manual_last_mode = clamp(ini_read_real("manual", "last_mode", 1), 1, 2);
    manual_auto_pumps = bool(ini_read_real("manual", "auto_pumps", 0));
    machinegun_toggle = bool(ini_read_real("values2", "machinegun_toggle", false));
    mg_interval_min = clamp(ini_read_real("values2", "mg_interval_min", 4), 2, 20);
    mg_interval_max = clamp(ini_read_real("values2", "mg_interval_max", 14), 2, 20);
    mg_spread = clamp(ini_read_real("values2", "mg_spread", 0.2), 0.1, 0.5);
    mg_burst_min = clamp(ini_read_real("values2", "mg_burst_min", 1), 1, 10);
    mg_burst_max = clamp(ini_read_real("values2", "mg_burst_max", 2), 1, 10);
    overflow_delay = clamp(ini_read_real("values2", "overflow_delay", 0), 0, 2);
    wife_climax_stamina = clamp(ini_read_real("responses", "wife_climax", 100), 100, 2000);
    wife_pleasure_threshold = wife_climax_stamina;
    wife_pleasure_max = wife_climax_stamina;
    wife_womb_capacity = clamp(ini_read_real("responses", "wife_womb", 20), 1, 100);
    fill_max = wife_womb_capacity;
    ini_close();
    if (radio_has_tracks)
    {
        radio_track_index = clamp(radio_track_index, 0, ds_list_size(radio_track_list) - 1);
    }
    else
    {
        radio_track_index = 0;
    }
    if (cs_futa_pack_index > 0 && cs_futa_pack_index <= ds_list_size(cs_futa_packs))
    {
        func_cs_load_pack(cs_futa_pack_index - 1);
        func_cs_apply_alt(cs_futa_alt_index);
    }
    if (cs_wife_pack_index > 0 && cs_wife_pack_index <= ds_list_size(cs_futa_packs))
    {
        func_cs_wife_load_pack(cs_wife_pack_index - 1);
        func_cs_wife_apply_alt(cs_wife_alt_index);
    }
    show_debug_message("loaded save");
    oDialogueManager.func_load_dialogue(temp_dialogue);
    if (temp_texture_pack != "default")
    {
        find_texture_pack_index(temp_texture_pack);
        func_texture_pack_replace(temp_texture_pack);
    }
}
else
{
    func_save_settings();
}
var _rg_pool = ["mega_sperm_pill", "equine_pill", "knotted_pill", "extra_thick_pill", "diphallia_pill", "ovulation_pill", "stamina_pill", "leaky_pill", "hyper_breeding_pill", "blockage_pill", "quickshot_pill", "reverse_speed_pill", "edge_addict_pill", "premature_pill", "edge_lover_pill", "pound_town_pill", "livestream_pill", "growth_cascade_pill", "savor_pill", "three_pump_champ_pill"];
ini_open("setting_data.sav");
var _rg_saved_k = real(ini_read_string("nevergiveup", "k", "0"));
var _rg_saved_cry = ini_read_string("nevergiveup", "nevergonnamakeyoucry", "");
ini_close();
var _rg_already_done = _rg_saved_cry != "";
var _rg_tampered = false;
if (_rg_already_done && _rg_saved_k != 0)
{
    var _rg_decoded = (real(_rg_saved_cry) ^ _rg_saved_k) - 7919;
    if (_rg_decoded < 0 || _rg_decoded > 19)
    {
        _rg_tampered = true;
    }
}
if (_rg_tampered)
{
    ini_open("setting_data.sav");
    ini_write_string("nevergiveup", "k", "0");
    ini_write_string("nevergiveup", "nevergonnamakeyoucry", "");
    ini_write_string("nevergiveup", "nevergonnasaygoodbye", "");
    ini_close();
    _rg_already_done = false;
}
if (!_rg_already_done)
{
}

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
    else if (variable_struct_exists(arg0, "touch_drag_last_y"))
    {
        variable_struct_remove(arg0, "touch_drag_last_y");
    }
    arg0.scroll_lerp = lerp(arg0.scroll_lerp, arg0.scroll, 1);
    if (abs(arg0.scroll - arg0.scroll_lerp) < 0.01)
    {
        arg0.scroll_lerp = arg0.scroll;
    }
}

function func_peek_enter_room()
{
    if (!peek_closed_during_play)
    {
        return false;
    }
    peek_mode = 0;
    prev_peek_mode = -1;
    peek_closed_during_play = false;
    title = false;
    muffle_pending = false;
    muffle_delay_timer = 0;
    audio_bus_main.effects[0] = undefined;
    audio_bus_main.effects[1] = undefined;
}

function func_peek_keyhole_half_width(arg0, arg1)
{
    var centre_y = (room_height / 2) - 35;
    var radius = 56 + arg1;
    var dy = arg0 - centre_y;
    var half_width = 0;
    if (abs(dy) < radius)
    {
        half_width = sqrt(max(0, (radius * radius) - (dy * dy)));
    }
    var stem_top = ((room_height / 2) + 4) - arg1;
    var stem_bottom = (room_height / 2) + 90 + arg1;
    if (arg0 >= stem_top && arg0 <= stem_bottom)
    {
        var stem_fraction = (arg0 - stem_top) / (stem_bottom - stem_top);
        half_width = max(half_width, 17 + arg1 + (27 * stem_fraction));
    }
    return half_width;
}

function func_peek_keyhole_surround()
{
    var centre_x = room_width / 2;
    var surround_colour = make_color_rgb(12, 10, 8);
    for (var strip_start = 0; strip_start < room_height; strip_start += 120)
    {
        var strip_end = min(room_height, strip_start + 120);
        draw_primitive_begin(pr_trianglestrip);
        for (var scan_y = strip_start; scan_y <= strip_end; scan_y += 1)
        {
            var edge_x = centre_x - func_peek_keyhole_half_width(scan_y, 0);
            draw_vertex_color(0, scan_y, surround_colour, 1);
            draw_vertex_color(edge_x, scan_y, surround_colour, 1);
        }
        draw_primitive_end();
    }
    for (var strip_start = 0; strip_start < room_height; strip_start += 120)
    {
        var strip_end = min(room_height, strip_start + 120);
        draw_primitive_begin(pr_trianglestrip);
        for (var scan_y = strip_start; scan_y <= strip_end; scan_y += 1)
        {
            var edge_x = centre_x + func_peek_keyhole_half_width(scan_y, 0);
            draw_vertex_color(edge_x, scan_y, surround_colour, 1);
            draw_vertex_color(room_width, scan_y, surround_colour, 1);
        }
        draw_primitive_end();
    }
    for (var rim = 0; rim < 2; rim += 1)
    {
        var inner_padding = 0;
        var outer_padding = 1;
        var rim_colour = make_color_rgb(172, 138, 80);
        if (rim == 0)
        {
            inner_padding = 1;
            outer_padding = 3;
            rim_colour = make_color_rgb(88, 67, 41);
        }
        for (var strip_start = 0; strip_start < room_height; strip_start += 120)
        {
            var strip_end = min(room_height, strip_start + 120);
            draw_primitive_begin(pr_trianglestrip);
            for (var scan_y = strip_start; scan_y <= strip_end; scan_y += 1)
            {
                var inner_width = func_peek_keyhole_half_width(scan_y, inner_padding);
                var outer_width = func_peek_keyhole_half_width(scan_y, outer_padding);
                draw_vertex_color(centre_x - outer_width, scan_y, rim_colour, 1);
                draw_vertex_color(centre_x - inner_width, scan_y, rim_colour, 1);
            }
            draw_primitive_end();
        }
        for (var strip_start = 0; strip_start < room_height; strip_start += 120)
        {
            var strip_end = min(room_height, strip_start + 120);
            draw_primitive_begin(pr_trianglestrip);
            for (var scan_y = strip_start; scan_y <= strip_end; scan_y += 1)
            {
                var inner_width = func_peek_keyhole_half_width(scan_y, inner_padding);
                var outer_width = func_peek_keyhole_half_width(scan_y, outer_padding);
                draw_vertex_color(centre_x + inner_width, scan_y, rim_colour, 1);
                draw_vertex_color(centre_x + outer_width, scan_y, rim_colour, 1);
            }
            draw_primitive_end();
        }
    }
}

ec_timer = irandom_range(4, 15);
ec_active = false;
ec_frame = 0;
ec_dir = 1;
ec_clench_timer = 0;
ec_hold_timer = 0;
vc_timer = irandom_range(10, 30);
vc_active = false;
vc_frame = 0;
vc_dir = 1;
vc_clench_timer = 0;
vc_hold_timer = 0;
global.favs_futa = ds_map_create();
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

function func_save_futa_offset(arg0, arg1, arg2, arg3)
{
    var _folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
    var _path = string(_folder) + "/custom_data.futa";
    if (!file_exists(_path)) exit;
    var _file = file_text_open_read(_path);
    if (_file < 0) exit;
    var _contents = "";
    while (!file_text_eof(_file)) { _contents += file_text_readln(_file); }
    file_text_close(_file);
    var _new_x_line = arg0 + "=\"" + string(arg2) + "\"";
    var _new_y_line = arg1 + "=\"" + string(arg3) + "\"";
    var _has_x = string_pos(arg0 + "=", _contents) > 0;
    var _has_y = string_pos(arg1 + "=", _contents) > 0;
    if (_has_x)
    {
        var _start = string_pos(arg0 + "=", _contents);
        var _end = _start;
        while (_end <= string_length(_contents) && string_char_at(_contents, _end) != "\n") { _end++; }
        _contents = string_copy(_contents, 1, _start - 1) + _new_x_line + string_copy(_contents, _end, (string_length(_contents) - _end) + 1);
    }
    if (_has_y)
    {
        var _start = string_pos(arg1 + "=", _contents);
        var _end = _start;
        while (_end <= string_length(_contents) && string_char_at(_contents, _end) != "\n") { _end++; }
        _contents = string_copy(_contents, 1, _start - 1) + _new_y_line + string_copy(_contents, _end, (string_length(_contents) - _end) + 1);
    }
    if (!_has_x || !_has_y)
    {
        var _has_portrait = string_pos("[portrait]", _contents) > 0;
        if (_has_portrait)
        {
            var _insert_pos = string_pos("[portrait]", _contents) + string_length("[portrait]");
            var _before = string_copy(_contents, 1, _insert_pos - 1);
            var _after = string_copy(_contents, _insert_pos, (string_length(_contents) - _insert_pos) + 1);
            var _inject = "";
            if (!_has_x) _inject += ("\n" + _new_x_line);
            if (!_has_y) _inject += ("\n" + _new_y_line);
            _contents = _before + _inject + _after;
        }
        else
        {
            _contents += "\n[portrait]\n";
            if (!_has_x) _contents += (_new_x_line + "\n");
            if (!_has_y) _contents += (_new_y_line + "\n");
        }
    }
    try
    {
        var _out = file_text_open_write(_path);
        if (_out >= 0)
        {
            file_text_write_string(_out, _contents);
            file_text_close(_out);
        }
    }
    catch (ex) {}
}

function func_save_wife_offset(arg0, arg1, arg2, arg3)
{
    var _folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
    var _path_wife = string(_folder) + "/custom_data.wife";
    var _path_spouse = string(_folder) + "/custom_data.spouse";
    var _path = file_exists(_path_wife) ? _path_wife : _path_spouse;
    if (!file_exists(_path)) exit;
    var _file = file_text_open_read(_path);
    if (_file < 0) exit;
    var _contents = "";
    while (!file_text_eof(_file)) { _contents += file_text_readln(_file); }
    file_text_close(_file);
    var _new_x_line = arg0 + "=\"" + string(arg2) + "\"";
    var _new_y_line = arg1 + "=\"" + string(arg3) + "\"";
    var _has_x = string_pos(arg0 + "=", _contents) > 0;
    var _has_y = string_pos(arg1 + "=", _contents) > 0;
    if (_has_x)
    {
        var _start = string_pos(arg0 + "=", _contents);
        var _end = _start;
        while (_end <= string_length(_contents) && string_char_at(_contents, _end) != "\n") { _end++; }
        _contents = string_copy(_contents, 1, _start - 1) + _new_x_line + string_copy(_contents, _end, (string_length(_contents) - _end) + 1);
    }
    if (_has_y)
    {
        var _start = string_pos(arg1 + "=", _contents);
        var _end = _start;
        while (_end <= string_length(_contents) && string_char_at(_contents, _end) != "\n") { _end++; }
        _contents = string_copy(_contents, 1, _start - 1) + _new_y_line + string_copy(_contents, _end, (string_length(_contents) - _end) + 1);
    }
    if (!_has_x || !_has_y)
    {
        var _has_portrait = string_pos("[portrait]", _contents) > 0;
        if (_has_portrait)
        {
            var _insert_pos = string_pos("[portrait]", _contents) + string_length("[portrait]");
            var _before = string_copy(_contents, 1, _insert_pos - 1);
            var _after = string_copy(_contents, _insert_pos, (string_length(_contents) - _insert_pos) + 1);
            var _inject = "";
            if (!_has_x) _inject += ("\n" + _new_x_line);
            if (!_has_y) _inject += ("\n" + _new_y_line);
            _contents = _before + _inject + _after;
        }
        else
        {
            _contents += "\n[portrait]\n";
            if (!_has_x) _contents += (_new_x_line + "\n");
            if (!_has_y) _contents += (_new_y_line + "\n");
        }
    }
    try
    {
        var _out = file_text_open_write(_path);
        if (_out >= 0)
        {
            file_text_write_string(_out, _contents);
            file_text_close(_out);
        }
    }
    catch (ex) {}
}

function func_save_futa_cum_offset(arg0, arg1)
{
    var _folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
    var _path = string(_folder) + "/custom_data.futa";
    if (!file_exists(_path)) exit;
    var _file = file_text_open_read(_path);
    if (_file < 0) exit;
    var _contents = "";
    while (!file_text_eof(_file)) { _contents += file_text_readln(_file); }
    file_text_close(_file);
    var _new_line = arg0 + " = \"" + string(arg1) + "\"";
    var _has_key = string_pos(arg0 + " =", _contents) > 0;
    if (_has_key)
    {
        var _start = string_pos(arg0 + " =", _contents);
        var _end = _start;
        while (_end <= string_length(_contents) && string_char_at(_contents, _end) != "\n") { _end++; }
        _contents = string_copy(_contents, 1, _start - 1) + _new_line + string_copy(_contents, _end, (string_length(_contents) - _end) + 1);
    }
    else
    {
        var _has_cumpos = string_pos("[CumPos]", _contents) > 0;
        if (_has_cumpos)
        {
            var _insert_pos = string_pos("[CumPos]", _contents) + string_length("[CumPos]");
            var _before = string_copy(_contents, 1, _insert_pos - 1);
            var _after = string_copy(_contents, _insert_pos, (string_length(_contents) - _insert_pos) + 1);
            _contents = _before + "\n" + _new_line + _after;
        }
        else
        {
            _contents += "\n[CumPos]\n" + _new_line + "\n";
        }
    }
    try
    {
        var _out = file_text_open_write(_path);
        if (_out >= 0)
        {
            file_text_write_string(_out, _contents);
            file_text_close(_out);
        }
    }
    catch (ex) {}
}

function func_save_futa_condom_offset(arg0, arg1)
{
    var _folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
    var _path = string(_folder) + "/custom_data.futa";
    if (!file_exists(_path)) exit;
    var _file = file_text_open_read(_path);
    if (_file < 0) exit;
    var _contents = "";
    while (!file_text_eof(_file)) { _contents += file_text_readln(_file); }
    file_text_close(_file);
    var _new_line = arg0 + " = \"" + string(arg1) + "\"";
    var _has_key = string_pos(arg0 + " =", _contents) > 0;
    if (_has_key)
    {
        var _start = string_pos(arg0 + " =", _contents);
        var _end = _start;
        while (_end <= string_length(_contents) && string_char_at(_contents, _end) != "\n") { _end++; }
        _contents = string_copy(_contents, 1, _start - 1) + _new_line + string_copy(_contents, _end, (string_length(_contents) - _end) + 1);
    }
    else
    {
        var _has_condom = string_pos("[condom]", _contents) > 0;
        if (_has_condom)
        {
            var _insert_pos = string_pos("[condom]", _contents) + string_length("[condom]");
            var _before = string_copy(_contents, 1, _insert_pos - 1);
            var _after = string_copy(_contents, _insert_pos, (string_length(_contents) - _insert_pos) + 1);
            _contents = _before + "\n" + _new_line + _after;
        }
        else
        {
            _contents += "\n[condom]\n" + _new_line + "\n";
        }
    }
    try
    {
        var _out = file_text_open_write(_path);
        if (_out >= 0)
        {
            file_text_write_string(_out, _contents);
            file_text_close(_out);
        }
    }
    catch (ex) {}
}

function func_play_insertion_sfx()
{
    if (ds_list_size(custom_insert_list) > 0)
    {
        var _c_snd = ds_list_find_value(custom_insert_list, irandom(ds_list_size(custom_insert_list) - 1));
        if (_c_snd != undefined && audio_exists(_c_snd))
        {
            oAudioManager.play_sfx(_c_snd, 0, 1, 1);
            return true;
        }
    }
    var _ipick = (insert_snd_last == 0) ? (irandom(6) + 1) : (irandom(5) + 1);
    if (insert_snd_last != 0 && _ipick >= insert_snd_last)
    {
        _ipick += 1;
    }
    insert_snd_last = _ipick;
    var _sname = "Insertion" + string(_ipick);
    var _isnd = asset_get_index(_sname);
    if (_isnd != -1)
    {
        oAudioManager.play_sfx(_isnd, 0, 1, 1);
    }
    return true;
}

function func_play_pullout_sfx()
{
    if (ds_list_size(custom_pullout_list) > 0)
    {
        var _c_snd = ds_list_find_value(custom_pullout_list, irandom(ds_list_size(custom_pullout_list) - 1));
        if (_c_snd != undefined && audio_exists(_c_snd))
        {
            oAudioManager.play_sfx(_c_snd, 0, 1, 1);
            return true;
        }
    }
    var _ppick = (pullout_snd_last == 0) ? (irandom(6) + 1) : (irandom(5) + 1);
    if (pullout_snd_last != 0 && _ppick >= pullout_snd_last)
    {
        _ppick += 1;
    }
    pullout_snd_last = _ppick;
    var _sname = "Pullout" + string(_ppick);
    var _psnd = asset_get_index(_sname);
    if (_psnd != -1)
    {
        oAudioManager.play_sfx(_psnd, 0, 1, 1);
    }
    return true;
}

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
    var _csnd_roll = irandom(3);
    if (_csnd_roll == last_condom_break_snd)
    {
        _csnd_roll = (_csnd_roll + 1) & 3;
    }
    last_condom_break_snd = _csnd_roll;
    var _sname = (_csnd_roll == 0) ? "sndCondomBreak" : ("sndCondomBreak" + string(_csnd_roll + 1));
    var _csnd_pick = asset_get_index(_sname);
    if (_csnd_pick != -1)
    {
        oAudioManager.play_sfx(_csnd_pick, 0, 1, 1);
    }
    else
    {
        oAudioManager.play_sfx(sndCondomBreak, 0, 1, 1);
    }
    return true;
}
