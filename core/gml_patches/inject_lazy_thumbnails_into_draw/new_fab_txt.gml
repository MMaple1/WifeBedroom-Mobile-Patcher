if (mob_expanded)
{
    draw_set_color(c_white);
    draw_set_halign(fa_center);
    draw_set_valign(fa_middle);
    draw_text((_fab_x1 + _fab_x2) * 0.5, (_fab_y1 + _fab_y2) * 0.5, "X");
}
else
{
    var _mid_x = (_fab_x1 + _fab_x2) * 0.5;
    var _mid_y = (_fab_y1 + _fab_y2) * 0.5;
    draw_set_color(c_white);
    draw_set_alpha(0.85);
    draw_rectangle(_mid_x - 7, _mid_y - 5, _mid_x + 7, _mid_y - 4, false);
    draw_rectangle(_mid_x - 7, _mid_y - 1, _mid_x + 7, _mid_y, false);
    draw_rectangle(_mid_x - 7, _mid_y + 3, _mid_x + 7, _mid_y + 4, false);
}