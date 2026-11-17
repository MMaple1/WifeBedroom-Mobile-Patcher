        // Fluid boundary clamping for New Wife panel
        newwife_menu_x = clamp(newwife_menu_x, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
        newwife_menu_y = clamp(newwife_menu_y, (total_h * 0.5) + 4, room_height - ((total_h * 0.5) + 4));

        var menu_cx = newwife_menu_x;
        var menu_cy = newwife_menu_y;
        var menu_start_y = menu_cy - (total_h * 0.5);
        var menu_end_y = menu_cy + (total_h * 0.5);

        comment = "drag handle = title bar";
        var _close_nw_pre_x = menu_cx + (menu_w_px * 0.5) - 7;
        var _close_nw_pre_y = menu_start_y + menu_pad + 1;
        var _close_nw_pre_hover = point_in_rectangle(mouse_x, mouse_y, _close_nw_pre_x - 6, _close_nw_pre_y - 2, _close_nw_pre_x + 6, _close_nw_pre_y + 9);
        var can_drag_nw = point_in_rectangle(mouse_x, mouse_y, menu_cx - (menu_w_px * 0.5), menu_start_y - 2, menu_cx + (menu_w_px * 0.5), menu_start_y + menu_pad + title_h + 8);
        if (mouse_check_button_pressed(mb_left) && can_drag_nw && !_close_nw_pre_hover)
        {
            newwife_dragging = true;
            drag_offset_x = newwife_menu_x - mouse_x;
            drag_offset_y = newwife_menu_y - mouse_y;
        }
        if (newwife_dragging)
        {
            newwife_menu_x = clamp(mouse_x + drag_offset_x, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
            newwife_menu_y = clamp(mouse_y + drag_offset_y, (total_h * 0.5) + 4, room_height - ((total_h * 0.5) + 4));
            menu_cx = newwife_menu_x;
            menu_cy = newwife_menu_y;
            menu_start_y = menu_cy - (total_h * 0.5);
            menu_end_y = menu_cy + (total_h * 0.5);
            if (mouse_check_button_released(mb_left))
            {
                newwife_dragging = false;
            }
        }
        var _close_nw_x = menu_cx + (menu_w_px * 0.5) - 7;
        var _close_nw_y = menu_start_y + menu_pad + 1;
        var _close_nw_hover = point_in_rectangle(mouse_x, mouse_y, _close_nw_x - 12, _close_nw_y - 6, _close_nw_x + 12, _close_nw_y + 14);