var anatomy_sprite = (wife_xray == -1) ? xray_sprite : wife_xray;
    if (sprite_exists(anatomy_sprite))
    {
        var _aw = sprite_get_width(anatomy_sprite);
        if (_aw > 0 && _aw != 160)
        {
            var _asc = 160 / _aw;
            sprite_set_offset(anatomy_sprite, 80 / _asc, 84 / _asc);
        }
        else
        {
            var _ax_off = sprite_get_xoffset(anatomy_sprite);
            var _ay_off = sprite_get_yoffset(anatomy_sprite);
            if (_ax_off > 120 || _ax_off < 40 || _ay_off > 120 || _ay_off < 40)
                sprite_set_offset(anatomy_sprite, 80, 84);
        }
    }
    if (sprite_exists(xray_sprite))
    {
        var _xw = sprite_get_width(xray_sprite);
        if (_xw > 0 && _xw != 160)
        {
            var _xsc = 160 / _xw;
            sprite_set_offset(xray_sprite, 80 / _xsc, 84 / _xsc);
        }
        else
        {
            var _xx_off = sprite_get_xoffset(xray_sprite);
            var _xy_off = sprite_get_yoffset(xray_sprite);
            if (_xx_off > 120 || _xx_off < 40 || _xy_off > 120 || _xy_off < 40)
                sprite_set_offset(xray_sprite, 80, 84);
        }
    }