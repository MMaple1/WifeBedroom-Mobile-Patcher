custom_xray = sprite_add(f_xray, 18, false, false, 80, (custom_xray_offset_y > 0) ? (84 - custom_xray_offset_y) : (84 + custom_xray_offset_y));
        var _px_w = sprite_get_width(custom_xray);
        if (_px_w > 0 && _px_w != 160)
        {
            var _px_sc = 160 / _px_w;
            var _px_yoff = (custom_xray_offset_y > 0) ? (84 - custom_xray_offset_y) : (84 + custom_xray_offset_y);
            sprite_set_offset(custom_xray, 80 / _px_sc, _px_yoff / _px_sc);
        }