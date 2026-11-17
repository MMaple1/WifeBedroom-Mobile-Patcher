var _is_equipped = (_ci == ((selector_mode == 0) ? custom_futa_index : custom_wife_index));
            if (_is_equipped)
            {
                draw_set_alpha(0.35 + (0.15 * sin(current_time * 0.005)));
                draw_set_color(make_color_rgb(255, 215, 0));
                draw_rectangle(_cx - 4, _cy - 4, _cx + _cell_w + 4, _cy + _cell_h + 4, false);
                draw_set_alpha(1);
                draw_rectangle(_cx - 4, _cy - 4, _cx + _cell_w + 4, _cy + _cell_h + 4, true);
                draw_rectangle(_cx - 3, _cy - 3, _cx + _cell_w + 3, _cy + _cell_h + 3, true);
                draw_set_font(fntFontSmall);
                draw_set_halign(fa_center);
                draw_set_valign(fa_bottom);
                draw_set_color(make_color_rgb(255, 225, 60));
                draw_text(_cx + (_cell_w * 0.5), _cy - 4, "★ " + string(_fname));
                draw_set_valign(fa_top);
            }
            draw_set_color(_border_col);
            draw_rectangle(_cx - 2, _cy - 2, _cx + _cell_w + 2, _cy + _cell_h + 2, true);