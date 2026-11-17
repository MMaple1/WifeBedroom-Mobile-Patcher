if (title == false && start_timer < 1 && futa_selector_open == false && orgasm == false)
{
    hover_portrait = point_in_rectangle(mouse_x, mouse_y, 10, room_height - 128, 87, room_height - 64);
    kiss_box = point_in_rectangle(mouse_x, mouse_y, (portrait_x - 6) + custom_kiss_x_offset, ((portrait_y + (top_breath * 64)) - 3) + custom_kiss_y_offset, portrait_x + 6 + custom_kiss_x_offset, portrait_y + (top_breath * 64) + 3 + custom_kiss_y_offset);
    boob_box = point_in_rectangle(mouse_x, mouse_y, 10 + custom_boob_x_offset, (room_height - 58) + custom_boob_y_offset, 87 + custom_boob_x_offset, (room_height - 25) + custom_boob_y_offset);
    headpat_press = point_in_rectangle(mouse_x, mouse_y, (portrait_x - 32) + custom_headpat_x_offset, (portrait_y - 56) + custom_headpat_y_offset, portrait_x + 32 + custom_headpat_x_offset, (portrait_y - 24) + custom_headpat_y_offset);
}
else if (futa_selector_open == true)
{
    hover_portrait = false;
    kiss_box = false;
    boob_box = false;
    headpat_press = false;
}