        var _cbx = (room_width / 2) - 170;
        var _cby = room_height - 52;
        var _cb_size = 8;
        var _cb_hover = point_in_rectangle(mouse_x, mouse_y, _cbx - _cb_size, _cby - _cb_size, _cbx + _cb_size, _cby + _cb_size);
        draw_set_alpha(disclaimer_scale * title_scale);
        draw_set_color(c_white);
        draw_rectangle(_cbx - _cb_size, _cby - _cb_size, _cbx + _cb_size, _cby + _cb_size, true);
        if (skip_disclaimer)
        {
            draw_line((_cbx - _cb_size) + 2, _cby, _cbx - 2, (_cby + _cb_size) - 2);
            draw_line(_cbx - 2, (_cby + _cb_size) - 2, (_cbx + _cb_size) - 2, (_cby - _cb_size) + 2);
        }
        draw_set_halign(fa_left);
        draw_text_transformed(_cbx + _cb_size + 4, _cby, "skip", 0.5, 0.5, 0);
        draw_set_halign(fa_center);
        draw_set_alpha(1);
        if (_cb_hover && mouse_check_button_pressed(mb_left) && disclaimer_scale > 0.9)
        {
            skip_disclaimer = !skip_disclaimer;
            func_save_settings();
        }