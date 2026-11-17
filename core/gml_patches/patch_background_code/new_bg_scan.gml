function func_scan_custom_backgrounds()
{
    ds_list_clear(custom_background_folders);
    custom_background_name_array = [];
    var _base_dir = (os_type == os_android || os_type == os_ios) ? "custom_bedrooms" : (tc_wd + "/custom_bedrooms");
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