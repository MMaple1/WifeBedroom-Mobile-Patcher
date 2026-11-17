for (var _fi = 0; _fi < array_length(_futa_names); _fi++)
{
    var _file = _futa_names[_fi];
    var _full_path = _is_mobile ? ("custom_futas/" + _file) : (_wd + "/custom_futas/" + _file);
    if (_is_mobile && _futa_manifest)
    {
        custom_sprite_loaded = true;
        tutorial = false;
        ds_list_add(custom_futas_folder, _full_path);
        ds_list_add(futa_selector_names, _file);
        ds_list_add(futa_selector_has_deepthroat, true);
        ds_list_add(futa_selector_has_alts, false);
        ds_list_add(futa_selector_portraits, -1);
    }
    else if (_futa_manifest || tc_dir_exists(_full_path))