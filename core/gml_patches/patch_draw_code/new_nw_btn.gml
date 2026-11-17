var _mob_touch_nw = false;
    for (var _d = 0; _d < 3; _d++)
    {
        if (device_mouse_check_button_pressed(_d, mb_left))
        {
            var _dx = device_mouse_x(_d);
            var _dy = device_mouse_y(_d);
            if (_dx >= (mm_x4 - 14) && _dx <= (mm_x4 + 14) && _dy >= (mm_y4 - 10) && _dy <= (mm_y4 + 10))
                _mob_touch_nw = true;
        }
    }
    var _mouse_hit_nw = point_in_rectangle(mouse_x, mouse_y, mm_x4 - 14, mm_y4 - 10, mm_x4 + 14, mm_y4 + 10);
    mm_press4 = _mouse_hit_nw || _mob_touch_nw;