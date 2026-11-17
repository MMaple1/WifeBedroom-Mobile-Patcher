if (_fab_over && _mob_touch_p)
{
    mob_expanded = !mob_expanded;
    mob_scroll_y = 0;
    mob_is_dragging = false;
}

// Quick Access Buttons: [R] [N] [C] [O] displayed to the left of the main overlay button
if (mob_expanded)
{
    var _qb_w = 32;
    var _qb_h = 26;
    var _qb_gap = 5;
    var _qbtns = [
        ["R", ord("R"), make_color_rgb(220, 60, 60)],      // Reset
        ["N", ord("N"), _c_mob_accent],                    // Climax
        ["C", ord("C"), make_color_rgb(180, 0, 255)],     // Wife Climax
        ["O", ord("O"), make_color_rgb(0, 210, 110)]       // Ovulate
    ];

    for (var _qi = 0; _qi < 4; _qi++)
    {
        var _qbx1 = _fab_x1 - ((4 - _qi) * (_qb_w + _qb_gap));
        var _qby1 = _fab_y1;
        var _qbx2 = _qbx1 + _qb_w;
        var _qby2 = _qby1 + _qb_h;
        
        var _qb_over = point_in_rectangle(_mob_tx, _mob_ty, _qbx1, _qby1, _qbx2, _qby2);
        var _qb_data = _qbtns[_qi];
        var _qb_lbl = _qb_data[0];
        var _qb_key = _qb_data[1];
        var _qb_col = _qb_data[2];

        draw_set_alpha((_qb_over && _mob_touch_d) ? 0.85 : 0.65);
        draw_set_color((_qb_over && _mob_touch_d) ? _c_mob_btn_press : _c_mob_bg);
        draw_roundrect_ext(_qbx1, _qby1, _qbx2, _qby2, 8, 8, false);

        draw_set_alpha(0.85);
        draw_set_color(_qb_col);
        draw_roundrect_ext(_qbx1, _qby1, _qbx2, _qby2, 8, 8, true);

        draw_set_color(c_white);
        draw_text((_qbx1 + _qbx2) * 0.5, (_qby1 + _qby2) * 0.5, _qb_lbl);

        if (_qb_over && _mob_touch_p)
        {
            if (_qb_key == ord("R"))
            {
                func_reset_sex_stats();
                sex_progress = 0;
                edge_charge = 0;
            }
            else if (_qb_key == ord("C"))
            {
                func_wife_climax();
            }
            else if (_qb_key == ord("O"))
            {
                func_ovulate();
            }
            else if (_qb_key == ord("N"))
            {
                orgasm_start = true;
                orgasm = true;
                keyboard_key_press(ord("N"));
                mob_release_key = ord("N");
            }
            else
            {
                keyboard_key_press(_qb_key);
                mob_release_key = _qb_key;
            }
        }
    }
}