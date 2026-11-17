var _w_buf = buffer_load("custom_wives/_manifest.txt");
if (_w_buf == -1 && _wd != "")
{
    _w_buf = buffer_load(_wd + "/custom_wives/_manifest.txt");
}
if (_w_buf != -1)
{
    var _w_str = buffer_read(_w_buf, buffer_string);
    buffer_delete(_w_buf);
    _w_str = string_replace_all(_w_str, "\r", "");
    var _cur_wline = "";
    for (var _ci = 1; _ci <= string_length(_w_str); _ci++)
    {
        var _ch = string_char_at(_w_str, _ci);
        if (_ch == "\n")
        {
            if (_cur_wline != "")
            {
                array_push(_wife_names, _cur_wline);
                _cur_wline = "";
            }
        }
        else
        {
            _cur_wline += _ch;
        }
    }
    if (_cur_wline != "")
    {
        array_push(_wife_names, _cur_wline);
    }
}
else
{
    var _ff_wife = tc_ff_first(_wd + "/custom_wives/*", 16);
    while (_ff_wife != "")
    {
        array_push(_wife_names, _ff_wife);
        _ff_wife = tc_ff_next();
    }
    tc_ff_close();
}