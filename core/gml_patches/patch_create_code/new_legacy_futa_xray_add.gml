legacy_custom_xray = sprite_add(f_xray, 3, false, false, 80, 84);
        var _lfx_w = sprite_get_width(legacy_custom_xray);
        if (_lfx_w > 0 && _lfx_w != 160)
        {
            var _lfx_sc = 160 / _lfx_w;
            sprite_set_offset(legacy_custom_xray, 80 / _lfx_sc, 84 / _lfx_sc);
        }