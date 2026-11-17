    var _bar_x2 = room_width - 80;
    var _bar_y1 = 4;
    var _bar_y2 = 19;
    var _bar_hover = point_in_rectangle(mouse_x, mouse_y, _bar_x1, _bar_y1, _bar_x2, _bar_y2);
    if (mouse_check_button_pressed(mb_left))
    {
        if (_bar_hover)
        {
            if (selector_search_focused == false)
            {
                selector_search_focused = true;
                keyboard_string = selector_search_string;
            }
        }
        else
        {
            selector_search_focused = false;
        }
    }
    if (selector_search_focused)
    {
        selector_search_string = keyboard_string;
    }
    if (keyboard_check_pressed(vk_escape) && selector_search_focused)
    {
        selector_search_focused = false;
        selector_search_string = "";
        keyboard_string = "";
    }