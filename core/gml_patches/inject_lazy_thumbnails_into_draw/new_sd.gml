    var _display_text = (selector_search_string == "") ? (selector_search_focused ? "" : "search...") : selector_search_string;
    if (selector_search_focused && (current_time % 1000) < 500)
    {
        _display_text += "|";
    }
    draw_text_transformed(_bar_x1 + 4, (_bar_y1 + _bar_y2) / 2, _display_text, 0.55, 0.55, 0);
    var _fav_btn_x1 = _bar_x2 + 8;
    var _fav_btn_x2 = _fav_btn_x1 + 48;
    var _fmx = (os_type == os_android || os_type == os_ios) ? device_mouse_x(0) : mouse_x;
    var _fmy = (os_type == os_android || os_type == os_ios) ? device_mouse_y(0) : mouse_y;
    var _fav_btn_hover = point_in_rectangle(_fmx, _fmy, _fav_btn_x1 - 6, _bar_y1 - 6, _fav_btn_x2 + 6, _bar_y2 + 8);
    draw_set_color(selector_favs_only ? make_color_rgb(255, 215, 0) : make_color_rgb(70, 70, 70));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, false);
    draw_set_color(c_white);
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, true);
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_set_color(selector_favs_only ? c_black : c_white);
    draw_text_transformed((_fav_btn_x1 + _fav_btn_x2) * 0.5, (_bar_y1 + _bar_y2) * 0.5, "★ FAV", 0.5, 0.5, 0);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);
    if ((mouse_check_button_pressed(mb_left) || device_mouse_check_button_pressed(0, mb_left)) && _fav_btn_hover)
    {
        selector_favs_only = !selector_favs_only;
        futa_selector_menu.scroll = 0;
        futa_selector_menu.scroll_lerp = 0;
    }