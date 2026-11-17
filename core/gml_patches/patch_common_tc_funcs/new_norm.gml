function tc_is_save_path(arg0)
{
    // true for a path inside the game's own save folder (folders created on the phone)
    var _gs = game_save_id;
    while (string_length(_gs) > 1 && string_char_at(_gs, string_length(_gs)) == "/")
    {
        _gs = string_copy(_gs, 1, string_length(_gs) - 1);
    }
    return string_length(_gs) > 1 && string_pos(_gs, string(arg0)) == 1;
}

function tc_norm_path(arg0)
{
    arg0 = string(arg0);
    while (string_pos("//", arg0) > 0)
    {
        arg0 = string_replace_all(arg0, "//", "/");
    }
    if ((os_type == os_android || os_type == os_ios) && !tc_is_save_path(arg0))
    {
        while (string_char_at(arg0, 1) == "/")
        {
            arg0 = string_delete(arg0, 1, 1);
        }
    }
    return arg0;
}