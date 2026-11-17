    var _btns = [
        ["[M] MAN:" + _man_status, 77, 1, manual_mode > 0, make_color_rgb(0, 210, 110)],
        ["[T] " + _peek_status, 84, 0, 0, 16777215],
        ["[G] GHOST", 71, 1, futa_ghost_toggle, _c_mob_accent],
        ["[Q] REROLL", 81, 0, 0, 16777215],
        ["[H] HITBOX", 72, 1, mob_hitbox_active, make_color_rgb(160, 0, 220)],
        ["[RESET OPTIONS]", "RESET_DEFAULTS", 0, 0, make_color_rgb(255, 140, 0)]
    ];
    if (variable_instance_exists(id, "manual_mode") && manual_mode > 0 && variable_instance_exists(id, "radial_menu_open"))
    {
        array_insert(_btns, 1, ["[RADIAL MENU]", "RADIAL", 1, radial_menu_open, make_color_rgb(0, 180, 230)]);
    }

    // Auto-close overlay menu if anywhere outside the overlay boxes is tapped
    var _in_quick_bar = point_in_rectangle(_mob_tx, _mob_ty, _fab_x1 - (4 * (32 + 5)), _fab_y1, _fab_x1, _fab_y2);
    if (_mob_touch_p && !_in_drawer && !_in_quick_bar && !_fab_over)
    {
        mob_expanded = false;
        mob_scroll_y = 0;
        mob_is_dragging = false;
    }