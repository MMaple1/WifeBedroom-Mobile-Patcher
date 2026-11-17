draw_text_transformed(menu_cx, menu_start_y + menu_pad, "LOVER", 0.65, 0.65, 0);
        draw_set_font(fntFontSmall);
        draw_set_color(_close_nl_hover ? make_color_rgb(255, 120, 120) : c_white);
        draw_text_transformed(_close_nl_x, _close_nl_y, "X", 0.6, 0.6, 0);
        draw_set_font(fntFontBig);
        if (_close_nl_hover && mouse_check_button_pressed(mb_left))
        {
            newlover_menu_toggle = false; 
        }