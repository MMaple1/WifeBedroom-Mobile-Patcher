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
}