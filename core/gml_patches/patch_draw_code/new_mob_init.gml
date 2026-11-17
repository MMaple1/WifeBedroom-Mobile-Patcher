if (!variable_instance_exists(id, "mob_touching_menu"))
{
    mob_touching_menu = false;
}
if (!variable_instance_exists(id, "mob_drag_last_y"))
{
    mob_drag_last_y = 0;
}
if (!variable_instance_exists(id, "mob_init"))
{
    mob_init = true;
    mob_expanded = false;
    mob_hitbox_active = false;
    mob_release_key = -1;
    mob_scroll_y = 0;
    mob_drag_start_y = 0;
    mob_drag_last_y = 0;
    mob_is_dragging = false;
    mob_touching_menu = false;
    mob_lp_timer = 0;
    mob_lp_start_x = 0;
    mob_lp_start_y = 0;

    // Keep phone display awake while game is open
    if (os_type == os_android || os_type == os_ios)
    {
        os_powersave_enable(false);
    }
}

// Auto-save basic settings when closing options menu
if (!variable_instance_exists(id, "_last_opt_tog"))
    _last_opt_tog = options_toggle;
if (_last_opt_tog == true && options_toggle == false)
    func_save_settings();
_last_opt_tog = options_toggle;

// Exit all right-side menus when entering manual mode
if (!variable_instance_exists(id, "_prev_manual_mode"))
    _prev_manual_mode = manual_mode;
if (_prev_manual_mode == 0 && manual_mode > 0)
{
    background_menu_toggle = false;
    position_menu_toggle = false;
    pill_menu_toggle = false;
    dialogue_menu_toggle = false;
    radio_toggle = false;
    tab_quicknav_open = false;
    options_toggle = false;
    actions_menu_toggle = false;
    color_picker_active = false;
    futa_selector_open = false;
    if (os_type == os_android || os_type == os_ios)
        keyboard_virtual_hide();
    selector_search_focused = false;
}
_prev_manual_mode = manual_mode;