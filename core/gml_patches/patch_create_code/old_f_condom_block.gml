            f_condom = string(arg0) + "/custom_condom.png";
            if (file_exists(f_condom))
            {
                if (sprite_exists(legacy_custom_condom))
                {
                    sprite_delete(legacy_custom_condom);
                }
                legacy_custom_condom = sprite_add(f_condom, 2, false, false, sprite_origin_x, sprite_origin_y);
            }