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

function tc_dir_exists(arg0)
{
    arg0 = tc_norm_path(arg0);
    if (string_char_at(arg0, string_length(arg0)) == "/")
    {
        arg0 = string_copy(arg0, 1, string_length(arg0) - 1);
    }
    return directory_exists(arg0) || file_exists(arg0 + "/_manifest.txt") || file_exists(arg0);
}

function tc_ff_first(arg0, arg1)
{
    tc_ff_items = -1;
    var _m = tc_norm_path(arg0);
    var _cut = string_last_pos("/", _m);
    var _mf = (_cut > 0) ? (string_copy(_m, 1, _cut) + "_manifest.txt") : "_manifest.txt";
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
default_x = x;
default_y = y;
body_jiggle = 0;
body_jiggle_move = 0;
cum = false;
cum_color = -1;
background_id = 0;
for (var i = 0; i < 4; i++)
{
    starfield_scale[i] = 0.25 * i;
}
animated_background_frame = 0;
rain_offset = 0;
bedroom_rain_enabled = irandom(99) < 30;
bedroom_rain_chance_initial = 40;
bedroom_rain_shift_chance = 15;
bedroom_was_active = false;
custom_background_enabled = false;
custom_background_loaded = false;
custom_background_sprite = -1;
custom_background_use_subimages = false;
custom_background_folder_index = -1;
custom_background_folders = ds_list_create();
custom_background_breathe = false;
custom_foreground_front = false;
custom_background_name_array = [];
bedroom_wallpapercolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
bedroom_trimcolor = choose(16777215, 12632256, 12632256, 8421504, 4210752, 2171174);
bedroom_dressercolor = make_colour_hsv(random_range(20, 30), random_range(64, 128), random_range(48, 255));
bedroom_carpetcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
bedroom_mattresscolor = make_colour_hsv(random(255), random_range(0, 64), random_range(128, 256));
bedroom_mattressframecolor = make_colour_hsv(random_range(15, 30), random_range(64, 168), random_range(48, 200));
starship_shipcolor = make_colour_hsv(random_range(140, 200), random_range(80, 180), random_range(60, 160));
starship_consolecolor = make_colour_hsv(random_range(0, 255), random_range(40, 120), random_range(80, 180));
starship_screencolor = make_colour_hsv(random_range(110, 140), random_range(160, 255), random_range(255, 255));
starship_glasscolor = make_colour_hsv(random_range(170, 220), random_range(60, 140), random_range(180, 255));
vip_wallcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
vip_stagecolor = make_colour_hsv(random_range(20, 40), random_range(64, 128), random_range(80, 200));
vip_polecolor = make_colour_hsv(random_range(30, 50), random_range(100, 200), random_range(150, 255));
vip_underwearcolor = make_colour_hsv(random(255), random_range(100, 200), random_range(150, 255));
vip_condomscolor = make_colour_hsv(random(255), random_range(80, 180), random_range(120, 255));
vip_lotioncolor = make_colour_hsv(random_range(0, 30), random_range(0, 60), random_range(200, 255));
vip_mattresscolor = make_colour_hsv(random(255), random_range(0, 64), random_range(128, 255));
vip_framecolor = make_colour_hsv(random_range(15, 30), random_range(64, 168), random_range(48, 200));
beach_watercolor = make_colour_hsv(random_range(25, 45), random_range(80, 180), random_range(180, 255));
beach_skycolor = make_colour_hsv(random_range(25, 45), random_range(80, 160), random_range(180, 240));
beach_suncolor = make_colour_hsv(random_range(20, 50), random_range(0, 60), random_range(220, 255));
beach_cloudscolor = make_colour_hsv(random_range(25, 45), random_range(40, 120), random_range(200, 255));
beach_sandcolor = make_colour_hsv(random_range(15, 35), random_range(60, 140), random_range(180, 255));
beach_stuffcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
office_wallcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
office_floorcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
office_deskcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
dungeon_floorcolor = make_colour_hsv(random_range(0, 65), random_range(60, 90), random_range(170, 200));
dungeon_wallcolor = make_colour_hsv(random_range(0, 30), random_range(0, 150), random_range(180, 255));
dungeon_gatecolor = make_colour_hsv(random_range(0, 0), random_range(0, 10), random_range(150, 255));
dungeon_chestcolor = make_colour_hsv(random_range(20, 35), random_range(60, 140), random_range(40, 120));
dungeon_chesttrimcolor = make_colour_hsv(random_range(30, 50), random_range(100, 200), random_range(100, 200));
dungeon_torchcolor = make_colour_hsv(random_range(15, 35), random_range(80, 160), random_range(80, 180));
dungeon_flamecolor = make_colour_hsv(random_range(0, 255), random_range(150, 255), random_range(200, 255));
func_recolor_bedroom();
func_scan_custom_backgrounds();

function func_recolor_bedroom()
{
    bedroom_wallpapercolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
    bedroom_trimcolor = choose(16777215, 12632256, 12632256, 8421504, 4210752, 2171174);
    bedroom_dressercolor = make_colour_hsv(random_range(20, 30), random_range(64, 128), random_range(48, 255));
    bedroom_carpetcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
    bedroom_mattresscolor = make_colour_hsv(random(255), random_range(0, 64), random_range(128, 256));
    bedroom_mattressframecolor = make_colour_hsv(random_range(15, 30), random_range(64, 168), random_range(48, 200));
    starship_shipcolor = make_colour_hsv(random_range(140, 200), random_range(80, 180), random_range(60, 160));
    starship_consolecolor = make_colour_hsv(random_range(0, 255), random_range(40, 120), random_range(80, 180));
    starship_screencolor = make_colour_hsv(random_range(110, 140), random_range(160, 255), random_range(255, 255));
    starship_glasscolor = make_colour_hsv(random_range(170, 220), random_range(60, 140), random_range(180, 255));
    vip_wallcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
    vip_stagecolor = make_colour_hsv(random_range(20, 40), random_range(64, 128), random_range(80, 200));
    vip_polecolor = make_colour_hsv(random_range(30, 50), random_range(100, 200), random_range(150, 255));
    vip_underwearcolor = make_colour_hsv(random(255), random_range(100, 200), random_range(150, 255));
    vip_condomscolor = make_colour_hsv(random(255), random_range(80, 180), random_range(120, 255));
    vip_lotioncolor = make_colour_hsv(random_range(0, 30), random_range(0, 60), random_range(200, 255));
    vip_mattresscolor = make_colour_hsv(random(255), random_range(0, 64), random_range(128, 255));
    vip_framecolor = make_colour_hsv(random_range(15, 30), random_range(64, 168), random_range(48, 200));
    beach_watercolor = make_colour_hsv(random_range(25, 45), random_range(80, 180), random_range(180, 255));
    beach_skycolor = make_colour_hsv(random_range(25, 45), random_range(80, 160), random_range(180, 240));
    beach_suncolor = make_colour_hsv(random_range(20, 50), random_range(0, 60), random_range(220, 255));
    beach_cloudscolor = make_colour_hsv(random_range(25, 45), random_range(40, 120), random_range(200, 255));
    beach_sandcolor = make_colour_hsv(random_range(15, 35), random_range(60, 140), random_range(180, 255));
    beach_stuffcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
    office_wallcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
    office_floorcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
    office_deskcolor = make_colour_hsv(random(255), random_range(64, 128), random_range(96, 255));
    dungeon_floorcolor = make_colour_hsv(random_range(0, 65), random_range(60, 90), random_range(170, 200));
    dungeon_wallcolor = make_colour_hsv(random_range(0, 30), random_range(0, 150), random_range(180, 255));
    dungeon_gatecolor = make_colour_hsv(random_range(0, 0), random_range(0, 10), random_range(150, 255));
    dungeon_chestcolor = make_colour_hsv(random_range(20, 35), random_range(60, 140), random_range(40, 120));
    dungeon_chesttrimcolor = make_colour_hsv(random_range(30, 50), random_range(100, 200), random_range(100, 200));
    dungeon_torchcolor = make_colour_hsv(random_range(15, 35), random_range(80, 160), random_range(80, 180));
    dungeon_flamecolor = make_colour_hsv(random_range(0, 255), random_range(150, 255), random_range(200, 255));
}

function func_set_custom_background_sprite(arg0)
{
    if (!sprite_exists(arg0))
    {
        return false;
    }
    custom_background_sprite = arg0;
    custom_background_use_subimages = true;
    custom_background_enabled = true;
    return true;
}

function func_clear_custom_background()
{
    if (custom_background_use_subimages && sprite_exists(custom_background_sprite))
    {
        sprite_delete(custom_background_sprite);
    }
    custom_background_enabled = false;
    custom_background_sprite = -1;
    custom_background_use_subimages = false;
    custom_background_folder_index = -1;
    custom_background_breathe = false;
    custom_foreground_front = false;
    x = default_x;
    y = default_y;
}

function func_scan_custom_backgrounds()
{
    ds_list_clear(custom_background_folders);
    custom_background_name_array = [];
    var _base_dir = (file_exists("custom_stuff/custom_bedrooms/_manifest.txt") || file_exists("assets/custom_stuff/custom_bedrooms/_manifest.txt")) ? "custom_stuff/custom_bedrooms" : "custom_bedrooms";
    if (!file_exists(_base_dir + "/_manifest.txt") && tc_wd != "" && os_type != os_android && os_type != os_ios)
    {
        _base_dir = tc_wd + "/" + _base_dir;
    }
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

function func_check_custom_background(arg0)
{
    var _exists = file_exists(arg0 + "/custom_data.bedroom");
    if (_exists)
    {
        var _bg_name = "";
        ini_open(arg0 + "/custom_data.bedroom");
        _bg_name = ini_read_string("info", "name", "");
        ini_close();
        array_push(custom_background_name_array, _bg_name);
    }
    return _exists;
}

function func_load_custom_background(arg0)
{
    if (arg0 < 0 || arg0 >= ds_list_size(custom_background_folders))
    {
        return false;
    }
    var _path = ds_list_find_value(custom_background_folders, arg0);
    var _bg_path = _path + "/background.png";
    if (!file_exists(_bg_path))
    {
        if (file_exists(_path + "/custom_background.png"))
        {
            _bg_path = _path + "/custom_background.png";
        }
        else
        {
            return false;
        }
    }
    var _breathe = false;
    var _fg_front = false;
    var _config_path = _path + "/custom_data.bedroom";
    ini_open(_config_path);
    _breathe = ini_read_real("background", "foreground_breathe", false);
    _fg_front = ini_read_real("background", "foreground_front", false);
    ini_close();
    func_clear_custom_background();
    var _spr = sprite_add(_bg_path, 4, false, false, 220, 128);
    if (!sprite_exists(_spr) || sprite_get_number(_spr) < 4)
    {
        if (sprite_exists(_spr))
        {
            sprite_delete(_spr);
        }
        return false;
    }
    var _loaded = func_set_custom_background_sprite(_spr);
    if (_loaded)
    {
        custom_background_folder_index = arg0;
        custom_background_breathe = _breathe;
        custom_foreground_front = _fg_front;
    }
    return _loaded;
}
