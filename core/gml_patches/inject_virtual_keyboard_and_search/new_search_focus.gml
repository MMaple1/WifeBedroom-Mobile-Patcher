    var _fav_btn_x1 = 20;
    var _fav_btn_x2 = 95;
    var _bar_x1 = 102;
    var _bar_x2 = room_width - 60;
    var _bar_y1 = 4;
    var _bar_y2 = 20;
    var _fav_btn_hover = point_in_rectangle(mouse_x, mouse_y, _fav_btn_x1 - 2, _bar_y1 - 2, _fav_btn_x2 + 2, _bar_y2 + 2);
    var _bar_hover = point_in_rectangle(mouse_x, mouse_y, _bar_x1 - 2, _bar_y1 - 2, _bar_x2 + 2, _bar_y2 + 2);
    if (mouse_check_button_pressed(mb_left))
    {
        if (_fav_btn_hover)
        {
            selector_favs_only = !selector_favs_only;
            futa_selector_menu.scroll = 0;
            futa_selector_menu.scroll_lerp = 0;
            if (selector_search_focused && (os_type == os_android || os_type == os_ios))
            {
                keyboard_virtual_hide();
            }
            selector_search_focused = false;
        }
        else if (_bar_hover)
        {
            if (selector_search_focused == false)
            {
                selector_search_focused = true;
                keyboard_string = selector_search_string;
                if (os_type == os_android || os_type == os_ios)
                {
                    keyboard_virtual_show(0, 0, 0, false);
                }
            }
        }
        else
        {
            if (selector_search_focused && (os_type == os_android || os_type == os_ios))
            {
                keyboard_virtual_hide();
            }
            selector_search_focused = false;
        }
    }
    if (selector_search_focused)
    {
        selector_search_string = keyboard_string;
    }
    if ((keyboard_check_pressed(vk_escape) || keyboard_check_pressed(vk_enter)) && selector_search_focused)
    {
        if (os_type == os_android || os_type == os_ios)
        {
            keyboard_virtual_hide();
        }
        selector_search_focused = false;
        if (keyboard_check_pressed(vk_escape))
        {
            selector_search_string = "";
            keyboard_string = "";
        }
    }
    // Draw Favorite Filter Button
    draw_set_color(selector_favs_only ? make_color_rgb(255, 215, 0) : make_color_rgb(55, 55, 55));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, false);
    draw_set_color(selector_favs_only ? c_white : make_color_rgb(140, 140, 140));
    draw_rectangle(_fav_btn_x1, _bar_y1, _fav_btn_x2, _bar_y2, true);
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_set_color(selector_favs_only ? c_black : c_white);
    draw_text_transformed((_fav_btn_x1 + _fav_btn_x2) * 0.5, (_bar_y1 + _bar_y2) * 0.5, selector_favs_only ? "FAV: ON" : "FAV: ALL", 0.45, 0.45, 0);
    draw_set_halign(fa_left);
    draw_set_valign(fa_top);