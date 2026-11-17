function menu_scroll_update(arg0, arg1, arg2)
{
    if (mouse_wheel_up() || mouse_wheel_down())
    {
        arg0.scroll += mouse_wheel_down() - mouse_wheel_up();
        arg0.scroll = median(arg0.scroll, 0, max(0, arg1 - arg2));
    }
    arg0.scroll_lerp = lerp(arg0.scroll_lerp, arg0.scroll, 1);
    if (abs(arg0.scroll - arg0.scroll_lerp) < 0.01)
    {
        arg0.scroll_lerp = arg0.scroll;
    }
}
