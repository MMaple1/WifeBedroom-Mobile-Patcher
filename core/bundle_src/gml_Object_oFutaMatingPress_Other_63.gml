if (ds_map_find_value(async_load, "id") == pm_dialog)
{
    pm_dialog = -1;
    if (ds_map_find_value(async_load, "status"))
    {
        var _pm_url = string(ds_map_find_value(async_load, "result"));
        _pm_url = string_replace_all(string_replace_all(string_replace_all(_pm_url, " ", ""), "\n", ""), "\r", "");
        if (string_pos("https://", _pm_url) == 1)
        {
            var _pm_save = game_save_id;
            if (string_char_at(_pm_save, string_length(_pm_save)) == "/")
            {
                _pm_save = string_copy(_pm_save, 1, string_length(_pm_save) - 1);
            }
            pm_url = _pm_url;
            pm_http = http_get_file(_pm_url, _pm_save + "/phone_mods_dl.zip");
            pm_status = "Downloading...";
        }
        else if (_pm_url != "")
        {
            pm_status = "That is not an https:// link.";
        }
    }
}
