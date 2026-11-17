custom_wives_folder = ds_list_create();
custom_futas_folder = ds_list_create();

// Android / Mobile Ultra-Fast In-Memory Manifest Streaming for ModRoom v3.3
var _f_buf = buffer_load("custom_futas/_manifest.txt");
if (_f_buf == -1 && working_directory != "") _f_buf = buffer_load(working_directory + "/custom_futas/_manifest.txt");
if (_f_buf == -1) _f_buf = buffer_load("custom_stuff/custom_futas/_manifest.txt");
if (_f_buf != -1)
{
    var _str = buffer_read(_f_buf, buffer_string);
    buffer_delete(_f_buf);
    var _len = string_length(_str);
    var _cur = "";
    for (var _p = 1; _p <= _len; _p++)
    {
        var _c = string_char_at(_str, _p);
        if (_c == chr(10) || _c == chr(13))
        {
            _cur = string_trim(_cur);
            if (_cur != "" && _cur != "_manifest.txt")
            {
                ds_list_add(custom_futas_folder, "custom_futas/" + _cur);
                custom_sprite_loaded = true;
                tutorial = false;
            }
            _cur = "";
        }
        else
        {
            _cur += _c;
        }
    }
    _cur = string_trim(_cur);
    if (_cur != "" && _cur != "_manifest.txt")
    {
        ds_list_add(custom_futas_folder, "custom_futas/" + _cur);
        custom_sprite_loaded = true;
        tutorial = false;
    }
}

var _w_buf = buffer_load("custom_wives/_manifest.txt");
if (_w_buf == -1 && working_directory != "") _w_buf = buffer_load(working_directory + "/custom_wives/_manifest.txt");
if (_w_buf == -1) _w_buf = buffer_load("custom_stuff/custom_wives/_manifest.txt");
if (_w_buf != -1)
{
    var _str_w = buffer_read(_w_buf, buffer_string);
    buffer_delete(_w_buf);
    var _len_w = string_length(_str_w);
    var _cur_w = "";
    for (var _pw = 1; _pw <= _len_w; _pw++)
    {
        var _cw = string_char_at(_str_w, _pw);
        if (_cw == chr(10) || _cw == chr(13))
        {
            _cur_w = string_trim(_cur_w);
            if (_cur_w != "" && _cur_w != "_manifest.txt")
            {
                ds_list_add(custom_wives_folder, "custom_wives/" + _cur_w);
                custom_wife_sprite_loaded = true;
            }
            _cur_w = "";
        }
        else
        {
            _cur_w += _cw;
        }
    }
    _cur_w = string_trim(_cur_w);
    if (_cur_w != "" && _cur_w != "_manifest.txt")
    {
        ds_list_add(custom_wives_folder, "custom_wives/" + _cur_w);
        custom_wife_sprite_loaded = true;
    }
}
