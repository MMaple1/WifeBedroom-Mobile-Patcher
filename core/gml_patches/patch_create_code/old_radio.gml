function func_radio_scan()
{
    ds_list_clear(radio_track_list);
    var _base = tc_wd + "/custom_music";
    if (!tc_dir_exists(_base))
    {
        radio_has_tracks = false;
        exit;
    }
    var _f = tc_ff_first(_base + "/*.ogg", 0);