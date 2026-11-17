var _futa_names = [];
var _mf_p = "custom_futas/_manifest.txt";
var _mf_futa = file_text_open_read(_mf_p);
if (_mf_futa == -1 && _wd != "")
{
    _mf_futa = file_text_open_read(_wd + "/custom_futas/_manifest.txt");
}
if (_mf_futa != -1)
{
    while (!file_text_eof(_mf_futa))
    {
        var _mf_line = string_replace_all(string_replace_all(file_text_readln(_mf_futa), chr(13), ""), chr(10), "");
        if (_mf_line != "" && _mf_line != "_manifest.txt")
        {
            array_push(_futa_names, _mf_line);
        }
    }
    file_text_close(_mf_futa);
}
if (array_length(_futa_names) == 0)
{
    var _f_buf = buffer_load(_mf_p);
    if (_f_buf == -1 && _wd != "")
    {
        _f_buf = buffer_load(_wd + "/custom_futas/_manifest.txt");
    }
    if (_f_buf != -1)
    {
        var _f_str = string_replace_all(buffer_read(_f_buf, buffer_string), chr(13), "");
        buffer_delete(_f_buf);
        var _cur_line = "";
        for (var _ci = 1; _ci <= string_length(_f_str); _ci++)
        {
            var _ch = string_char_at(_f_str, _ci);
            if (_ch == chr(10))
            {
                if (_cur_line != "" && _cur_line != "_manifest.txt")
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
        if (_cur_line != "" && _cur_line != "_manifest.txt")
        {
            array_push(_futa_names, _cur_line);
        }
    }
}