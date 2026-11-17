    ds_list_clear(custom_background_folders);
    var _file = file_find_first(working_directory + "/custom_bedrooms/*", 16);
    while (_file != "")
    {
        var _full_path = working_directory + "/custom_bedrooms/" + _file;
        if (directory_exists(_full_path) && func_check_custom_background(_full_path))
        {
            custom_background_loaded = true;
            ds_list_add(custom_background_folders, _full_path);
            show_debug_message("Loaded custom background pack: " + _file);
        }
        _file = file_find_next();
    }
    file_find_close();