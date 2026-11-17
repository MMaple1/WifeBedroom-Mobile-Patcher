        f_mate = string(arg0) + "/custom_mating_press.png";
        var _test_w = sprite_add(f_mate, 1, false, false, 0, 0);
        var _w_frame_w = (sprite_origin_x > 0) ? (sprite_origin_x * 2) : 160;
        var _w_frames = 4;
        if (sprite_exists(_test_w) && _test_w != -1)
        {
            var _w_total_w = sprite_get_width(_test_w);
            sprite_delete(_test_w);
            _w_frames = max(1, round(_w_total_w / _w_frame_w));
        }
        if (sprite_exists(legacy_custom_wife_mating_press))
        {
            sprite_delete(legacy_custom_wife_mating_press);
        }
        legacy_custom_wife_mating_press = sprite_add(f_mate, _w_frames, false, false, sprite_origin_x, sprite_origin_y);
        custom_wife_mating_press_scale = 160 / _w_frame_w;
        sprite_set_offset(legacy_custom_wife_mating_press, sprite_origin_x, sprite_origin_y);