function func_radio_scan()
{
    ds_list_clear(radio_track_list);
    var _base = (os_type == os_android || os_type == os_ios) ? "custom_music" : (tc_wd + "/custom_music");
    var _f = tc_ff_first(_base + "/*.ogg", 0);