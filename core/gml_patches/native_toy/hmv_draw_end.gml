var _hmv_s = hmv_speaker_size;
var _hmv_glow_l = hmv_speaker_pulse;
if (hmv_speaker_l_hover)
{
    _hmv_glow_l = max(_hmv_glow_l, 0.5);
}
if (hmv_active)
{
    _hmv_glow_l = max(_hmv_glow_l, 0.3);
}
draw_set_alpha(0.55 + (_hmv_glow_l * 0.45));
draw_set_color(make_color_rgb(60 + (_hmv_glow_l * 140), 60 + (_hmv_glow_l * 140), 75 + (_hmv_glow_l * 140)));
draw_rectangle(hmv_speaker_l_x, hmv_speaker_l_y + (_hmv_s * 0.15), hmv_speaker_l_x + (_hmv_s * 0.55), hmv_speaker_l_y + _hmv_s, false);
draw_set_color(c_black);
draw_rectangle(hmv_speaker_l_x, hmv_speaker_l_y + (_hmv_s * 0.15), hmv_speaker_l_x + (_hmv_s * 0.55), hmv_speaker_l_y + _hmv_s, true);
draw_circle(hmv_speaker_l_x + (_hmv_s * 0.28), hmv_speaker_l_y + (_hmv_s * 0.4), _hmv_s * 0.14, false);
draw_circle(hmv_speaker_l_x + (_hmv_s * 0.28), hmv_speaker_l_y + (_hmv_s * 0.78), _hmv_s * 0.16, false);
draw_set_color(make_color_rgb(200 + (_hmv_glow_l * 55), 200 + (_hmv_glow_l * 55), 215 + (_hmv_glow_l * 40)));
draw_circle(hmv_speaker_l_x + (_hmv_s * 0.28), hmv_speaker_l_y + (_hmv_s * 0.4), _hmv_s * 0.06, false);
draw_circle(hmv_speaker_l_x + (_hmv_s * 0.28), hmv_speaker_l_y + (_hmv_s * 0.78), _hmv_s * 0.07, false);
if (_hmv_glow_l > 0.05)
{
    draw_set_alpha(_hmv_glow_l * 0.5);
    draw_set_color(c_white);
    draw_circle(hmv_speaker_l_x + (_hmv_s * 0.28), hmv_speaker_l_y + (_hmv_s * 0.55), (_hmv_s * 0.75) + (_hmv_glow_l * 12), true);
}
var _hmv_glow_r = hmv_speaker_pulse;
if (hmv_speaker_r_hover)
{
    _hmv_glow_r = max(_hmv_glow_r, 0.5);
}
if (hmv_active)
{
    _hmv_glow_r = max(_hmv_glow_r, 0.3);
}
draw_set_alpha(0.55 + (_hmv_glow_r * 0.45));
draw_set_color(make_color_rgb(60 + (_hmv_glow_r * 140), 60 + (_hmv_glow_r * 140), 75 + (_hmv_glow_r * 140)));
draw_rectangle(hmv_speaker_r_x, hmv_speaker_r_y + (_hmv_s * 0.15), hmv_speaker_r_x + (_hmv_s * 0.55), hmv_speaker_r_y + _hmv_s, false);
draw_set_color(c_black);
draw_rectangle(hmv_speaker_r_x, hmv_speaker_r_y + (_hmv_s * 0.15), hmv_speaker_r_x + (_hmv_s * 0.55), hmv_speaker_r_y + _hmv_s, true);
draw_circle(hmv_speaker_r_x + (_hmv_s * 0.28), hmv_speaker_r_y + (_hmv_s * 0.4), _hmv_s * 0.14, false);
draw_circle(hmv_speaker_r_x + (_hmv_s * 0.28), hmv_speaker_r_y + (_hmv_s * 0.78), _hmv_s * 0.16, false);
draw_set_color(make_color_rgb(200 + (_hmv_glow_r * 55), 200 + (_hmv_glow_r * 55), 215 + (_hmv_glow_r * 40)));
draw_circle(hmv_speaker_r_x + (_hmv_s * 0.28), hmv_speaker_r_y + (_hmv_s * 0.4), _hmv_s * 0.06, false);
draw_circle(hmv_speaker_r_x + (_hmv_s * 0.28), hmv_speaker_r_y + (_hmv_s * 0.78), _hmv_s * 0.07, false);
if (_hmv_glow_r > 0.05)
{
    draw_set_alpha(_hmv_glow_r * 0.5);
    draw_set_color(c_white);
    draw_circle(hmv_speaker_r_x + (_hmv_s * 0.28), hmv_speaker_r_y + (_hmv_s * 0.55), (_hmv_s * 0.75) + (_hmv_glow_r * 12), true);
}
draw_set_alpha(1);
draw_set_color(c_white);
