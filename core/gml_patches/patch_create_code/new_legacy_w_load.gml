                var _w_port = _full_path + "/custom_portrait.png";
                var _w_spr = -1;
                if (!_is_mobile && file_exists(_w_port))
                {
                    _w_spr = sprite_add(_w_port, 10, false, false, 32, 48);
                }
                ds_list_add(wife_selector_portraits, _w_spr);