    var _mob_touch_nl = false;
    for (var _d = 0; _d < 3; _d++)
    {
        if (device_mouse_check_button_pressed(_d, mb_left))
        {
            var _dx = device_mouse_x(_d);
            var _dy = device_mouse_y(_d);
            if (_dx >= (portrait_x - 36) && _dx <= (portrait_x + 36) && _dy >= (portrait_y + 48) && _dy <= (portrait_y + 72))
                _mob_touch_nl = true;
        }
    }
    var _mouse_hit_nl = point_in_rectangle(mouse_x, mouse_y, portrait_x - 36, portrait_y + 48, portrait_x + 36, portrait_y + 72);
    button_newlover_press = (_mouse_hit_nl && mouse_check_button(mb_left)) || _mob_touch_nl;