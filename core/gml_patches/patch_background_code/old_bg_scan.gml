function func_scan_custom_backgrounds()
{
    ds_list_clear(custom_background_folders);
    var _file = tc_ff_first(tc_wd + "/custom_bedrooms/*", 16);
    while (_file != "")
    {
        var _full_path = tc_wd + "/custom_bedrooms/" + _file;
        if (tc_dir_exists(_full_path) && func_check_custom_background(_full_path))
        {
            custom_background_loaded = true;
            ds_list_add(custom_background_folders, _full_path);
            show_debug_message("Loaded custom background pack: " + _file);
        }
        _file = tc_ff_next();
    }
    tc_ff_close();
}