draw_text_transformed(menu_cx, menu_start_y + menu_pad, "WIFE", 0.65, 0.65, 0);
        draw_set_font(fntFontSmall);
        draw_set_color(_close_nw_hover ? make_color_rgb(255, 120, 120) : c_white);
        draw_text_transformed(_close_nw_x, _close_nw_y, "X", 0.6, 0.6, 0);
        draw_set_font(fntFontBig);
        if (_close_nw_hover && mouse_check_button_pressed(mb_left))
        {
            newwife_menu_toggle = false; 
        }