    ds_list_clear(custom_background_folders);
    custom_background_name_array = [];
    var _b_buf = buffer_load("custom_bedrooms/_manifest.txt");
    if (_b_buf == -1 && working_directory != "") _b_buf = buffer_load(working_directory + "/custom_bedrooms/_manifest.txt");
    if (_b_buf == -1) _b_buf = buffer_load("custom_stuff/custom_bedrooms/_manifest.txt");
    if (_b_buf != -1)
    {
        var _str_b = buffer_read(_b_buf, buffer_string);
        buffer_delete(_b_buf);
        var _len_b = string_length(_str_b);
        var _cur_b = "";
        for (var _pb = 1; _pb <= _len_b; _pb++)
        {
            var _cb = string_char_at(_str_b, _pb);
            if (_cb == chr(10) || _cb == chr(13))
            {
                _cur_b = string_trim(_cur_b);
                if (_cur_b != "" && _cur_b != "_manifest.txt")
                {
                    var _bp = "custom_bedrooms/" + _cur_b;
                    if (func_check_custom_background(_bp))
                    {
                        ds_list_add(custom_background_folders, _bp);
                        custom_background_loaded = true;
                    }
                }
                _cur_b = "";
            }
            else
            {
                _cur_b += _cb;
            }
        }
        _cur_b = string_trim(_cur_b);
        if (_cur_b != "" && _cur_b != "_manifest.txt")
        {
            var _bp2 = "custom_bedrooms/" + _cur_b;
            if (func_check_custom_background(_bp2))
            {
                ds_list_add(custom_background_folders, _bp2);
                custom_background_loaded = true;
            }
        }
    }