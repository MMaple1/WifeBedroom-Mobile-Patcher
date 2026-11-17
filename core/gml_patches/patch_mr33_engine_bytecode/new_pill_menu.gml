if (pill_menu_toggle)
{
{{PILL_DATA}}    var _count = array_length(pill_data);
    total_pill_amount = _count;
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    var pill_rows_per_col = 7;
    var pill_col_width = 68;
    var pill_row_height = 24;
    var pill_start_y = 75;
    for (i = 0; i < _count; i++)
    {
        var _col = i div pill_rows_per_col;
        var _row = i % pill_rows_per_col;
        var b2_x = room_width - 62 - (_col * pill_col_width);
        var b2_y = pill_start_y + (pill_row_height * _row);
        var button_press = point_in_rectangle(mouse_x, mouse_y, b2_x - 32, b2_y - 11, b2_x + 32, b2_y + 11);
        draw_sprite_ext(sButtonBack, 1, b2_x, b2_y, 4, 1.4, 0, c_white, 0.5 + (1 * button_press));
        var btn_name = pill_data[i][0];
        var var_name = pill_data[i][1];
        var is_active = variable_instance_get(id, var_name);
        draw_set_color(is_active ? c_white : c_gray);
        draw_text_transformed(b2_x, b2_y, btn_name, 0.5, 0.5, 0);
        if (mouse_check_button_pressed(mb_left) && button_press)
        {
            if (!(orgasm == true && var_name == "blockage_pill"))
            {
                variable_instance_set(id, var_name, !is_active);
            }
        }
    }
    draw_set_color(c_white);
    draw_set_valign(fa_top);
}
