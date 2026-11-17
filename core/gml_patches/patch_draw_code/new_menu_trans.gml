comment = "menu transition - warning displays once on startup, peek mode unaffected";
if (title == true && peek_closed_during_play == false)
{
    if (mouse_check_button_pressed(mb_left) && title_timer < 1)
    {
        if (disclaimer == false && title_from_hotkey == false && skip_disclaimer == false)
        {
            disclaimer = true;
        }
        else
        {
            title = false;
            peek_closed_during_play = true; // Game started! Warning will never interrupt peek mode again
            disclaimer = false;