function tc_ff_first(arg0, arg1)
{
    tc_ff_items = -1;
    var _m = tc_norm_path(arg0);
    var _cut = string_last_pos("/", _m);
    var _mf = (_cut > 0) ? (string_copy(_m, 1, _cut) + "_manifest.txt") : "_manifest.txt";
    if (!file_exists(_mf))
    {
        if (os_type == os_android || os_type == os_ios) return "";
        return file_find_first(arg0, arg1);
    }
    var _pat = string_lower(string_delete(_m, 1, _cut));
    var _suf = (string_char_at(_pat, 1) == "*") ? string_delete(_pat, 1, 1) : "";
    tc_ff_items = [];
    var _f = file_text_open_read(_mf);
    if (_f != -1)
    {
        while (!file_text_eof(_f))
        {
            var _ln = string_replace_all(string_replace_all(file_text_readln(_f), chr(13), ""), chr(10), "");
            var _lo = string_lower(_ln);
            var _ok = _ln != "" && _lo != "_manifest.txt";
            if (_ok && string_char_at(_pat, 1) == "*")
            {
                _ok = _suf == "" || (string_length(_lo) >= string_length(_suf) && string_copy(_lo, (string_length(_lo) - string_length(_suf)) + 1, string_length(_suf)) == _suf);
            }
            else if (_ok)
            {
                _ok = _lo == _pat;
            }
            if (_ok)
            {
                array_push(tc_ff_items, _ln);
            }
        }
        file_text_close(_f);
    }
    if (os_type != os_android && os_type != os_ios)
    {
        var _real = file_find_first(arg0, arg1);
        while (_real != "")
        {
            if (!array_contains(tc_ff_items, _real))
            {
                array_push(tc_ff_items, _real);
            }
            _real = file_find_next();
        }
        file_find_close();
    }
    tc_ff_pos = 0;
    return tc_ff_next();
}

function tc_ff_next()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type == os_android || os_type == os_ios) return "";
        return file_find_next();
    }
    if (tc_ff_pos >= array_length(tc_ff_items))
    {
        return "";
    }
    tc_ff_pos++;
    return tc_ff_items[tc_ff_pos - 1];
}

function tc_ff_close()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type != os_android && os_type != os_ios) file_find_close();
    }
    tc_ff_items = -1;
    tc_ff_pos = 0;
}