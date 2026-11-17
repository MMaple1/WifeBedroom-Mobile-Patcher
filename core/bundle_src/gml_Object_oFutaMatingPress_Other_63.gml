if (ds_map_find_value(async_load, "id") == pm_dialog)
{
    pm_dialog = -1;
    if (ds_map_find_value(async_load, "status"))
    {
        var _pm_raw = string_replace_all(string_replace_all(string(ds_map_find_value(async_load, "result")), "\n", ""), "\r", "");
        // trim spaces at both ends only (a file path may contain spaces)
        while (string_length(_pm_raw) > 0 && string_char_at(_pm_raw, 1) == " ")
        {
            _pm_raw = string_delete(_pm_raw, 1, 1);
        }
        while (string_length(_pm_raw) > 0 && string_char_at(_pm_raw, string_length(_pm_raw)) == " ")
        {
            _pm_raw = string_delete(_pm_raw, string_length(_pm_raw), 1);
        }
        var _pm_save = game_save_id;
        if (string_char_at(_pm_save, string_length(_pm_save)) == "/")
        {
            _pm_save = string_copy(_pm_save, 1, string_length(_pm_save) - 1);
        }
        var _pm_url = string_replace_all(_pm_raw, " ", "");
        if (string_pos("https://", _pm_url) == 1)
        {
            pm_url = _pm_url;
            pm_http = http_get_file(_pm_url, _pm_save + "/phone_mods_dl.zip");
            pm_status = "Downloading...";
        }
        else if (_pm_raw != "")
        {
            // a file on this phone: copy it into phone_inbox; the inbox check imports it like a shared file
            var _pm_path = _pm_raw;
            if (string_pos("file://", _pm_path) == 1)
            {
                _pm_path = string_replace_all(string_delete(_pm_path, 1, 7), "%20", " ");
            }
            if (string_pos("/sdcard/", _pm_path) == 1)
            {
                _pm_path = "/storage/emulated/0/" + string_delete(_pm_path, 1, 8);
            }
            var _pm_name = filename_name(_pm_path);
            var _pm_low = string_lower(_pm_name);
            var _pm_ext = string_copy(_pm_low, max(1, string_length(_pm_low) - 3), 4);
            var _pm_ext5 = string_copy(_pm_low, max(1, string_length(_pm_low) - 4), 5);
            if (_pm_ext != ".zip" && _pm_ext5 != ".json")
            {
                pm_status = "Enter an https:// link or the path of a .zip or .json file on this phone.";
            }
            else if (!file_exists(_pm_path))
            {
                pm_status = "Cannot open " + _pm_name + ". Android may block that folder: in your file manager, Share the file (or Open with) to this game instead.";
            }
            else
            {
                if (!tc_dir_exists(_pm_save + "/phone_inbox"))
                {
                    directory_create(_pm_save + "/phone_inbox");
                }
                file_copy(_pm_path, _pm_save + "/phone_inbox/" + _pm_name);
                if (file_exists(_pm_save + "/phone_inbox/" + _pm_name))
                {
                    pm_status = "Adding " + _pm_name + "...";
                }
                else
                {
                    pm_status = "Cannot copy " + _pm_name + ". In your file manager, Share the file (or Open with) to this game instead.";
                }
            }
        }
    }
}
