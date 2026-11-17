function func_get_custom_audio(arg0, arg1)
{
    arg1 = tc_norm_path(arg1);
    var _has_manifest = file_exists(arg1 + "/_manifest.txt");
    if (_has_manifest || tc_dir_exists(arg1))
    {
        ds_list_clear(arg0);
        show_debug_message("scanning folder: " + string(arg1));
        var _file = tc_ff_first(string(arg1) + "/*.ogg", 0);