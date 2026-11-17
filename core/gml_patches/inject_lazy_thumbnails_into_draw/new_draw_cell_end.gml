            var _star_hover = point_in_rectangle(mouse_x, mouse_y, _cx + _cell_w - 18, _cy + 2, _cx + _cell_w - 2, _cy + 18);
            draw_set_halign(fa_right);
            draw_set_valign(fa_top);
            draw_set_color(_is_fav ? make_color_rgb(255, 215, 0) : make_color_rgb(120, 120, 120));
            var _bx1 = (_cx + _cell_w) - 16;
            var _by1 = _cy + 2;
            var _bx2 = _bx1 + 14;
            var _by2 = _by1 + 14;
            draw_set_alpha(1);
            draw_set_color(_is_fav ? make_color_rgb(255, 215, 0) : make_color_rgb(35, 35, 35));
            draw_rectangle(_bx1, _by1, _bx2, _by2, false);
            draw_set_color(_is_fav ? c_white : make_color_rgb(120, 120, 120));
            draw_rectangle(_bx1, _by1, _bx2, _by2, true);
            draw_set_color(_is_fav ? c_black : c_white);
            var _bcx = _bx1 + 7;
            var _bcy = _by1 + 7;
            draw_line_width(_bcx - 4, _bcy, _bcx + 4, _bcy, 2);
            draw_line_width(_bcx, _bcy - 4, _bcx, _bcy + 4, 2);
            if ((mouse_check_button_pressed(mb_left) || device_mouse_check_button_pressed(0, mb_left)) && _star_hover && futa_selector_open_timer <= 0)
            {
                ini_open("setting_data.sav");
                var _sec = (selector_mode == 0) ? "favs_futa" : "favs_wife";
                if (_is_fav)
                {
                    ds_map_delete(_fav_map, _fname);
                    ini_key_delete(_sec, _fname);
                }
                else
                {
                    ds_map_add(_fav_map, _fname, 1);
                    ini_write_real(_sec, _fname, 1);
                }
                ini_close();
            }
            comment = "hover detection — highlight and record name";