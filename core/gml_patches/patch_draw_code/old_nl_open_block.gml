    if (newlover_menu_toggle == false)
    {
        if (button_newlover_press == true && mouse_check_button_pressed(mb_left))
        {
            newlover_menu_toggle = true;
            newwife_menu_toggle = false;
            if (oBackground.background_id == 3)
            {
                oAudioManager.play_sfx(asset_get_index("StarshipIN"), 1);
            }
            else if (oBackground.background_id == 2)
            {
                oAudioManager.play_sfx(asset_get_index("OfficeIN"), 1);
            }
            else if (oBackground.background_id == 5)
            {
                oAudioManager.play_sfx(asset_get_index("VipIN"), 1);
            }
            else if (oBackground.background_id == 1)
            {
                oAudioManager.play_sfx(asset_get_index("BeachIN"), 1);
            }
            else if (oBackground.background_id == 4)
            {
                oAudioManager.play_sfx(asset_get_index("DungeonIN"), 1);
            }
            else if (oBackground.background_id == 0)
            {
                oAudioManager.play_sfx(asset_get_index("BedroomIN"), 1);
            }
        }
        if (keyboard_check_pressed(ord("Q")) && options_toggle == false && selector_search_focused == false)
        {
            func_randomize_top();
            sex_progress = 0;
            edge_charge = 0;
            edge_snap_timer = 0;
            desperate_edge_state = 0;
            desperate_edge_timer = 0;
            edge_control_lock = false;
            futa_score = 0;
            loads = 0;
            wife_climax_counter = 0;
            impregnation_counter = 0;
            body_jiggle = 0.025;
            alarm[0] = 1;
            oAudioManager.play_sfx(sndCloth, 0, random_range(0.8, 1.2), 0.6);
        }
    }