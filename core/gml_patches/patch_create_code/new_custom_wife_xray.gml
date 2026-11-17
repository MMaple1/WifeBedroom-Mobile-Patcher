var _cwx_ox = ini_read_real("sprite", "xray_x", ini_read_real("xray", "origin_x", 80));
        var _cwx_oy = ini_read_real("sprite", "xray_y", ini_read_real("xray", "origin_y", 84));
        if (_cwx_ox > 120 || _cwx_ox < 40) _cwx_ox = 80;
        if (_cwx_oy > 120 || _cwx_oy < 40) _cwx_oy = 84;
        custom_wife_xray = sprite_add(file_check, 3, false, false, _cwx_ox, _cwx_oy);
        var _cwx_w = sprite_get_width(custom_wife_xray);
        if (_cwx_w > 0 && _cwx_w != 160)
        {
            var _cwx_sc = 160 / _cwx_w;
            sprite_set_offset(custom_wife_xray, _cwx_ox / _cwx_sc, _cwx_oy / _cwx_sc);
        }