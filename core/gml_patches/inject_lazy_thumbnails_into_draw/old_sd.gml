    var _display_text = (selector_search_string == "") ? (selector_search_focused ? "" : "search...") : selector_search_string;
    if (selector_search_focused && (current_time % 1000) < 500)
    {
        _display_text += "|";
    }
    draw_text_transformed(_bar_x1 + 4, (_bar_y1 + _bar_y2) / 2, _display_text, 0.55, 0.55, 0);

    // Draw Favorite Filter Button to the right of search bar
    draw_set_color(selector_favs_only ? make_color_rgb(255, 215, 0) : make_color_rgb(45, 45, 45));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, false);
    draw_set_color(selector_favs_only ? c_white : make_color_rgb(140, 140, 140));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, true);
    draw_set_font(fntFontSmall);
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_set_color(selector_favs_only ? c_black : c_white);
    draw_text((_fav_btn_x1 + _fav_btn_x2) * 0.5, (_bar_y1 + _bar_y2) * 0.5, selector_favs_only ? "FAV: ON" : "FAV: ALL");
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);