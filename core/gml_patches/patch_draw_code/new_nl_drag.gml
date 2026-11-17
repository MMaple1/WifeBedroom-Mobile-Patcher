        // Fluid boundary clamping for New Lover panel
        newlover_menu_cx = clamp(newlover_menu_cx, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
        var _nl_min_offset = portrait_y - room_height + 4;
        var _nl_max_offset = portrait_y - total_h - 4;
        newlover_menu_cy_end_offset = clamp(newlover_menu_cy_end_offset, _nl_min_offset, _nl_max_offset);

        var menu_cx = newlover_menu_cx;
        var menu_end_y = portrait_y - newlover_menu_cy_end_offset;
        var menu_start_y = menu_end_y - total_h;
        var menu_cy = (menu_start_y + menu_end_y) * 0.5;

        comment = "drag handle = title bar area";
        var _close_nl_pre_x = menu_cx + (menu_w_px * 0.5) - 7;
        var _close_nl_pre_y = menu_start_y + menu_pad + 1;
        var _close_nl_pre_hover = point_in_rectangle(mouse_x, mouse_y, _close_nl_pre_x - 6, _close_nl_pre_y - 2, _close_nl_pre_x + 6, _close_nl_pre_y + 9);
        var can_drag_nl = point_in_rectangle(mouse_x, mouse_y, menu_cx - (menu_w_px * 0.5), menu_start_y - 2, menu_cx + (menu_w_px * 0.5), menu_start_y + menu_pad + title_h + 8);
        if (mouse_check_button_pressed(mb_left) && can_drag_nl && !_close_nl_pre_hover)
        {
            newlover_dragging = true;
            drag_offset_x = newlover_menu_cx - mouse_x;
            drag_offset_y = portrait_y - newlover_menu_cy_end_offset - mouse_y;
        }
        if (newlover_dragging)
        {
            newlover_menu_cx = clamp(mouse_x + drag_offset_x, (menu_w_px * 0.5) + 4, room_width - ((menu_w_px * 0.5) + 4));
            newlover_menu_cy_end_offset = clamp(portrait_y - (mouse_y + drag_offset_y), _nl_min_offset, _nl_max_offset);
            menu_cx = newlover_menu_cx;
            menu_end_y = portrait_y - newlover_menu_cy_end_offset;
            menu_start_y = menu_end_y - total_h;
            menu_cy = (menu_start_y + menu_end_y) * 0.5;
            if (mouse_check_button_released(mb_left))
            {
                newlover_dragging = false;
            }
        }
        var _close_nl_x = menu_cx + (menu_w_px * 0.5) - 7;
        var _close_nl_y = menu_start_y + menu_pad + 1;
        var _close_nl_hover = point_in_rectangle(mouse_x, mouse_y, _close_nl_x - 12, _close_nl_y - 6, _close_nl_x + 12, _close_nl_y + 14);