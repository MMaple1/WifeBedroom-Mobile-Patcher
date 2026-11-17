    if (title == true && mouse_check_button_pressed(mb_left) && point_in_rectangle(mouse_x, mouse_y, room_width - 160, 0, room_width, 22))
    {
        tb_retry_count = 0;
        tb_paused_retry = false;
        tb_state = 0;
        tb_retry_at = _tb_now;
        mouse_clear(mb_left);
    }
    if (title == true && mouse_check_button_pressed(mb_left) && point_in_rectangle(mouse_x, mouse_y, room_width - 124, 22, room_width, 44))
    {
        tb_profile = (tb_profile + 1) % array_length(tb_profile_names);