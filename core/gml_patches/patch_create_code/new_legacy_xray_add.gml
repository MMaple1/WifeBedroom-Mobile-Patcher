legacy_custom_wife_xray = sprite_add(f_xray, 4, false, false, xray_origin_x, xray_origin_y);
        var _lcwx_w = sprite_get_width(legacy_custom_wife_xray);
        if (_lcwx_w > 0 && _lcwx_w != 160)
        {
            var _lcwx_sc = 160 / _lcwx_w;
            sprite_set_offset(legacy_custom_wife_xray, xray_origin_x / _lcwx_sc, xray_origin_y / _lcwx_sc);
        }