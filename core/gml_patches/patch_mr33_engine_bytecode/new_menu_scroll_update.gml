function menu_scroll_update(arg0, arg1, arg2)
{
    if (!variable_struct_exists(arg0, "touch_armed"))
    {
        arg0.touch_armed = false;
        arg0.touch_moved = false;
        arg0.touch_start_y = 0;
    }
    if (mouse_wheel_up() || mouse_wheel_down())
    {
        arg0.scroll += mouse_wheel_down() - mouse_wheel_up();
        arg0.scroll = median(arg0.scroll, 0, max(0, arg1 - arg2));
    }
    if (mouse_check_button_pressed(mb_left))
    {
        arg0.touch_armed = true;
        arg0.touch_moved = false;
        arg0.touch_start_y = mouse_y;
    }
    if (mouse_check_button(mb_left))
    {
        if (abs(mouse_y - arg0.touch_start_y) > 6)
        {
            arg0.touch_moved = true;
        }
        if (!variable_struct_exists(arg0, "touch_drag_last_y"))
        {
            arg0.touch_drag_last_y = mouse_y;
            arg0.touch_drag_accum = 0;
        }
        else
        {
            arg0.touch_drag_accum += mouse_y - arg0.touch_drag_last_y;
            arg0.touch_drag_last_y = mouse_y;
            var _row_height = 12;
            while (arg0.touch_drag_accum <= -_row_height)
            {
                arg0.scroll -= 1;
                arg0.touch_drag_accum += _row_height;
            }
            while (arg0.touch_drag_accum >= _row_height)
            {
                arg0.scroll += 1;
                arg0.touch_drag_accum -= _row_height;
            }
            arg0.scroll = median(arg0.scroll, 0, max(0, arg1 - arg2));
        }
    }
    else
    {
        if (variable_struct_exists(arg0, "touch_drag_last_y"))
        {
            variable_struct_remove(arg0, "touch_drag_last_y");
        }
        if (!mouse_check_button_released(mb_left))
        {
            arg0.touch_armed = false;
        }
    }
    arg0.scroll_lerp = lerp(arg0.scroll_lerp, arg0.scroll, 1);
    if (abs(arg0.scroll - arg0.scroll_lerp) < 0.01)
    {
        arg0.scroll_lerp = arg0.scroll;
    }
}
