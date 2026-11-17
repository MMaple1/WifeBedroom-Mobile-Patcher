    if (title == true && mouse_check_button_pressed(mb_left) && point_in_rectangle(mouse_x, mouse_y, room_width - 124, 0, room_width, 44))
    {
        tb_profile = (tb_profile + 1) % array_length(tb_profile_names);