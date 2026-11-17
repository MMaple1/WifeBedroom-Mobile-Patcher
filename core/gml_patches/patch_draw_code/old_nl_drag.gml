        var menu_cx = newlover_menu_cx;
        var menu_end_y = portrait_y - newlover_menu_cy_end_offset;
        var menu_start_y = menu_end_y - total_h;
        var menu_cy = (menu_start_y + menu_end_y) * 0.5;
        comment = "drag handle = title bar area";
        var can_drag_nl = point_in_rectangle(mouse_x, mouse_y, menu_cx - (menu_w_px * 0.5), menu_start_y, menu_cx + (menu_w_px * 0.5), menu_start_y + menu_pad + title_h + 4);
        if (mouse_check_button_pressed(mb_left) && can_drag_nl)
        {
            newlover_dragging = true;
            drag_offset_x = newlover_menu_cx - mouse_x;
            drag_offset_y = portrait_y - newlover_menu_cy_end_offset - mouse_y;
        }
        if (newlover_dragging)
        {
            newlover_menu_cx = mouse_x + drag_offset_x;
            newlover_menu_cy_end_offset = portrait_y - (mouse_y + drag_offset_y);
            menu_cx = newlover_menu_cx;
            menu_end_y = portrait_y - newlover_menu_cy_end_offset;
            menu_start_y = menu_end_y - total_h;
            menu_cy = (menu_start_y + menu_end_y) * 0.5;
            if (mouse_check_button_released(mb_left))
            {
                newlover_dragging = false;
            }
        }