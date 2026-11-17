function func_get_custom_audio(arg0, arg1)
{
    if (tc_dir_exists(arg1) == true)
    {
        ds_list_clear(arg0);
        show_debug_message("scanning folder: " + string(arg1));
        var _file = tc_ff_first(string(arg1) + "/*.ogg", 0);