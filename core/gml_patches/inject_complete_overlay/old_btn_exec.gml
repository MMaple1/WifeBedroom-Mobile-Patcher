        if (_btn_over && _click_occurred)
        {
            if (_bkcode == "RADIAL")
            {
                if (variable_instance_exists(id, "radial_menu_open"))
                {
                    radial_menu_open = !radial_menu_open;
                    radial_sub_menu = "";
                }
                mob_expanded = false;
            }
            else if (_bkcode == 72)
            {
                mob_hitbox_active = !mob_hitbox_active;
            }
            else
            {
                keyboard_key_press(_bkcode);
                mob_release_key = _bkcode;
            }
        }