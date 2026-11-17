            f_mate = string(arg0) + "/custom_mating_press.png";
            var _test_m = sprite_add(f_mate, 1, false, false, 0, 0);
            var _frame_w = (sprite_origin_x > 0) ? (sprite_origin_x * 2) : 160;
            var _mf = 9;
            if (sprite_exists(_test_m) && _test_m != -1)
            {
                var _mw = sprite_get_width(_test_m);
                sprite_delete(_test_m);
                _mf = max(1, round(_mw / _frame_w));
            }
            var _temp_mate = sprite_add(f_mate, _mf, false, false, sprite_origin_x, sprite_origin_y);
            if (sprite_exists(_temp_mate) && _temp_mate != -1)
            {
                is_legacy_custom = true;
                if (sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press > 189)
                {
                    sprite_delete(legacy_custom_mating_press);
                }
                legacy_custom_mating_press = _temp_mate;
                custom_mating_press_scale = 160 / _frame_w;
                sprite_set_offset(legacy_custom_mating_press, sprite_origin_x, sprite_origin_y);
            }