for (var _wi = 0; _wi < array_length(_wife_names); _wi++)
{
    var _file = _wife_names[_wi];
    var _full_path = _is_mobile ? ("custom_wives/" + _file) : (_wd + "/custom_wives/" + _file);
    if (_is_mobile && _wife_manifest)
    {
        custom_wife_sprite_loaded = true;
        ds_list_add(custom_wives_folder, _full_path);
        ds_list_add(wife_selector_names, _file);
        ds_list_add(wife_selector_has_cowgirl, true);
        ds_list_add(wife_selector_portraits, -1);
    }
    else if (_wife_manifest || tc_dir_exists(_wd + "/custom_wives/" + _file))