            f_port = string(arg0) + "/custom_portrait.png";
            if (file_exists(f_port))
            {
                if (sprite_exists(legacy_custom_portrait))
                {
                    sprite_delete(legacy_custom_portrait);
                }
                legacy_custom_portrait = sprite_add(f_port, 10, false, false, portrait_origin_x, portrait_origin_y);
                if (!sprite_exists(legacy_custom_portrait) || legacy_custom_portrait == -1)
                {
                    var _test_p = sprite_add(f_port, 1, false, false, 0, 0);
                    if (sprite_exists(_test_p) && _test_p != -1)
                    {
                        var _pw = sprite_get_width(_test_p);
                        var _ph = sprite_get_height(_test_p);
                        sprite_delete(_test_p);
                        var _p_frames = max(1, round(_pw / _ph));
                        legacy_custom_portrait = sprite_add(f_port, _p_frames, false, false, portrait_origin_x, portrait_origin_y);
                    }
                }
            }