
function func_load_custom_metadata(arg0, arg1)
{
    custom_name = "Untitled";
    custom_desc = "???";
    custom_author = "???";
    custom_portrait = sFutaPortrait1;
    custom_portrait_alt = sWifeCanonPortrait;
    custom_thumbnail = sThumbnailBedroom;
    var _ini_file = "";
    if (arg1 == 1) _ini_file = string(arg0) + "/custom_data.futa";
    else if (arg1 == 2)
    {
        _ini_file = string(arg0) + "/custom_data.spouse";
        if (!file_exists(_ini_file)) _ini_file = string(arg0) + "/custom_data.wife";
    }
    else if (arg1 == 3) _ini_file = string(arg0) + "/custom_data.bedroom";
    if (file_exists(_ini_file))
    {
        ini_open(_ini_file);
        custom_name = ini_read_string("info", "name", "Untitled");
        custom_desc = ini_read_string("info", "desc", "???");
        custom_author = ini_read_string("info", "author", "???");
        var _p_ox = ini_read_real("portrait", "origin_x", 64);
        var _p_oy = ini_read_real("portrait", "origin_y", 64);
        ini_close();
        if (arg1 == 1)
        {
            var _p_futa = string(arg0) + "/custom_portrait.png";
            if (!file_exists(_p_futa)) _p_futa = string(arg0) + "/custom_futa_portrait_0.png";
            if (file_exists(_p_futa)) custom_portrait = func_replace_custom_sprite(custom_portrait, _p_futa, 10, _p_ox, _p_oy);
            var _p_futa_alt = string(arg0) + "/custom_portrait_alt.png";
            if (file_exists(_p_futa_alt)) custom_portrait_alt = func_replace_custom_sprite(custom_portrait_alt, _p_futa_alt, 10, _p_ox, _p_oy);
        }
        else if (arg1 == 2)
        {
            var _p_wife = string(arg0) + "/custom_portrait.png";
            if (!file_exists(_p_wife)) _p_wife = string(arg0) + "/custom_wife_portrait_0.png";
            if (file_exists(_p_wife)) custom_portrait_alt = func_replace_custom_sprite(custom_portrait_alt, _p_wife, 10, _p_ox, _p_oy);
        }
        else if (arg1 == 3)
        {
            var _th_p = string(arg0) + "/thumbnail.png";
            if (!file_exists(_th_p)) _th_p = string(arg0) + "/custom_thumbnail.png";
            if (file_exists(_th_p)) custom_thumbnail = func_replace_custom_sprite(custom_thumbnail, _th_p, 1, 0, 0);
        }
    }
}
