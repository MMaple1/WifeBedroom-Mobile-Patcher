    draw_set_color(_head_hover ? _col_hover : _col_idle);
    draw_rectangle(_head_x1, _head_y1, _head_x2, _head_y2, true);
    // Debug hitboxes for Lover and Wife buttons
    draw_set_color(button_newlover_press ? _col_hover : _col_idle);
    draw_rectangle(portrait_x - 36, portrait_y + 48, portrait_x + 36, portrait_y + 72, true);
    draw_set_color(mm_press4 ? _col_hover : _col_idle);
    draw_rectangle((room_width - 332) - 14, (room_height - ui_y_offset) - 10, (room_width - 332) + 14, (room_height - ui_y_offset) + 10, true);
    draw_set_color(c_white);
    draw_set_alpha(1);