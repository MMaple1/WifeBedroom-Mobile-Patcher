            f_mate = string(arg0) + "/custom_mating_press.png";
            if (file_exists(f_mate))
            {
                if (sprite_exists(legacy_custom_mating_press))
                {
                    sprite_delete(legacy_custom_mating_press);
                }
                legacy_custom_mating_press = sprite_add(f_mate, 9, false, false, mp_origin_x, mp_origin_y);
            }