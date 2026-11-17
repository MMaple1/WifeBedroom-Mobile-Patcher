        var menu_cx = newwife_menu_x;
        var menu_cy = newwife_menu_y;
        var menu_start_y = menu_cy - (total_h * 0.5);
        var menu_end_y = menu_cy + (total_h * 0.5);
        comment = "drag handle = title bar";
        var can_drag_nw = point_in_rectangle(mouse_x, mouse_y, menu_cx - (menu_w_px * 0.5), menu_start_y, menu_cx + (menu_w_px * 0.5), menu_start_y + menu_pad + title_h + 4);
        if (mouse_check_button_pressed(mb_left) && can_drag_nw)
        {
            newwife_dragging = true;
            drag_offset_x = newwife_menu_x - mouse_x;
            drag_offset_y = newwife_menu_y - mouse_y;
        }
        if (newwife_dragging)
        {
            newwife_menu_x = mouse_x + drag_offset_x;
            newwife_menu_y = mouse_y + drag_offset_y;
            menu_cx = newwife_menu_x;
            menu_cy = newwife_menu_y;
            menu_start_y = menu_cy - (total_h * 0.5);
            menu_end_y = menu_cy + (total_h * 0.5);
            if (mouse_check_button_released(mb_left))
            {
                newwife_dragging = false;
            }
        }