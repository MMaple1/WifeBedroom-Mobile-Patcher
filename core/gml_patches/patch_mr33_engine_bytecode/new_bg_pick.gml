        if (mouse_check_button_released(mb_left) && button_press && variable_struct_exists(bg_menu, "touch_armed") && bg_menu.touch_armed && !bg_menu.touch_moved)
        {
            oBackground.background_id = i;
