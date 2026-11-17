            f_port = string(arg0) + "/custom_portrait.png";
            if (file_exists(f_port))
            {
                if (sprite_exists(legacy_custom_portrait))
                {
                    sprite_delete(legacy_custom_portrait);
                }
                legacy_custom_portrait = sprite_add(f_port, 10, false, false, portrait_origin_x, portrait_origin_y);
            }
            else
            {
                legacy_custom_portrait = -1;
            }