var _wife_names = [];
var _mf_pw = "custom_wives/_manifest.txt";
var _mf_wife = file_text_open_read(_mf_pw);
if (_mf_wife == -1 && _wd != "")
{
    _mf_wife = file_text_open_read(_wd + "/custom_wives/_manifest.txt");
}
if (_mf_wife != -1)
{
    while (!file_text_eof(_mf_wife))
    {
        var _mf_line2 = string_replace_all(string_replace_all(file_text_readln(_mf_wife), chr(13), ""), chr(10), "");
        if (_mf_line2 != "" && _mf_line2 != "_manifest.txt")
        {
            array_push(_wife_names, _mf_line2);
        }
    }
    file_text_close(_mf_wife);
}
if (array_length(_wife_names) == 0)
{
    var _w_buf = buffer_load(_mf_pw);
    if (_w_buf == -1 && _wd != "")
    {
        _w_buf = buffer_load(_wd + "/custom_wives/_manifest.txt");
    }
    if (_w_buf != -1)
    {
        var _w_str = string_replace_all(buffer_read(_w_buf, buffer_string), chr(13), "");
        buffer_delete(_w_buf);
        var _cur_wline = "";
        for (var _ci = 1; _ci <= string_length(_w_str); _ci++)
        {
            var _ch = string_char_at(_w_str, _ci);
            if (_ch == chr(10))
            {
                if (_cur_wline != "" && _cur_wline != "_manifest.txt")
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
        if (_cur_wline != "" && _cur_wline != "_manifest.txt")
        {
            array_push(_wife_names, _cur_wline);
        }
    }
}