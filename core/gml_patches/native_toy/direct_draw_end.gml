if (tb_enabled && title == true)
{
    var _tb_ha = draw_get_halign();
    var _tb_va = draw_get_valign();
    draw_set_halign(fa_right);
    draw_set_valign(fa_top);
    var _tb_label = "TOY: OPEN INTIFACE CENTRAL";
    if (tb_state == 3)
    {
        _tb_label = "TOY: SEARCHING...";
        if (array_length(tb_dev_idx) > 0)
        {
            _tb_label = "TOY: " + string_upper(tb_dev_name[0]);
        }
    }
    _tb_label += ("\nPOWER: " + tb_profile_names[tb_profile] + " (TAP)");
    if (tb_state == 3 && tb_ping_ms <= 0)
    {
        _tb_label += "\nSAFETY: SET MAX PING TIME IN INTIFACE";
    }
    var _tb_hit = point_in_rectangle(mouse_x, mouse_y, room_width - 124, 0, room_width, 44);
    draw_text_color(room_width - 6, 6, _tb_label, c_white, c_white, c_white, c_white, 0.65 + (0.35 * _tb_hit));
    draw_set_halign(_tb_ha);
    draw_set_valign(_tb_va);
}
