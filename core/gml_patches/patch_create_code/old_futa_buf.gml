var _f_buf = buffer_load("custom_futas/_manifest.txt");
if (_f_buf == -1 && _wd != "")
{
    _f_buf = buffer_load(_wd + "/custom_futas/_manifest.txt");
}
if (_f_buf != -1)
{
    var _f_str = buffer_read(_f_buf, buffer_string);
    buffer_delete(_f_buf);
    _f_str = string_replace_all(_f_str, "\r", "");
    var _cur_line = "";
    for (var _ci = 1; _ci <= string_length(_f_str); _ci++)
    {
        var _ch = string_char_at(_f_str, _ci);
        if (_ch == "\n")
        {
            if (_cur_line != "")
            {
                array_push(_futa_names, _cur_line);
                _cur_line = "";
            }
        }
        else
        {
            _cur_line += _ch;
        }
    }
    if (_cur_line != "")
    {
        array_push(_futa_names, _cur_line);
    }
}
else
{
    var _ff_futa = tc_ff_first(_wd + "/custom_futas/*", 16);
    while (_ff_futa != "")
    {
        array_push(_futa_names, _ff_futa);
        _ff_futa = tc_ff_next();
    }
    tc_ff_close();
}