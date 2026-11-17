var _tc_hx = options_x + 58;
var _tc_hy = options_y + 12;
var _tc_hh = point_in_rectangle(mouse_x, mouse_y, _tc_hx - 28, _tc_hy + 1, _tc_hx + 28, _tc_hy + 9);
draw_sprite_ext(sButtonBack, 1, _tc_hx, _tc_hy + 5, 4.2, 1, 0, tc_hyper ? 65535 : 16777215, 0.5 + (0.5 * _tc_hh) + (0.5 * tc_hyper));
draw_set_halign(1);
draw_set_valign(0);
draw_text_ext_transformed(_tc_hx, _tc_hy, tc_hyper ? "HYPER: ON" : "HYPER: OFF", 12, 100, 0.5, 0.5, 0);
if (mouse_check_button_pressed(1) && _tc_hh && title == false)
{
    tc_hyper = !tc_hyper;
    if (tc_hyper)
    {
        var _tc_f = file_text_open_write(game_save_id + "hyper_sizes.on");
        file_text_write_string(_tc_f, "1");
        file_text_close(_tc_f);
    }
    else
    {
        file_delete(game_save_id + "hyper_sizes.on");
    }
}
