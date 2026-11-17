            f_condom = string(arg0) + "/custom_condom.png";
            var _temp_cdm = sprite_add(f_condom, 2, false, false, sprite_origin_x, sprite_origin_y);
            if (sprite_exists(_temp_cdm) && _temp_cdm != -1)
            {
                if (sprite_exists(legacy_custom_condom))
                {
                    sprite_delete(legacy_custom_condom);
                }
                legacy_custom_condom = _temp_cdm;
            }