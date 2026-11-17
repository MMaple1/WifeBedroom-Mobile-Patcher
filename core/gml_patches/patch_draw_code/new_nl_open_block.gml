    if (!futa_selector_open && !mob_expanded && ((_mouse_hit_nl && mouse_check_button_pressed(mb_left)) || _mob_touch_nl))
    {
        newlover_menu_toggle = !newlover_menu_toggle;
        if (newlover_menu_toggle) newwife_menu_toggle = false;
                if (newlover_menu_toggle)
        {
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
        else
        {
            if (oBackground.background_id == 3)
            {
                oAudioManager.play_sfx(asset_get_index("StarshipOUT"), 1);
            }
            else if (oBackground.background_id == 2)
            {
                oAudioManager.play_sfx(asset_get_index("OfficeOUT"), 1);
            }
            else if (oBackground.background_id == 5)
            {
                oAudioManager.play_sfx(asset_get_index("VipOUT"), 1);
            }
            else if (oBackground.background_id == 1)
            {
                oAudioManager.play_sfx(asset_get_index("BeachOUT"), 1);
            }
            else if (oBackground.background_id == 4)
            {
                oAudioManager.play_sfx(asset_get_index("DungeonOUT"), 1);
            }
            else if (oBackground.background_id == 0)
            {
                oAudioManager.play_sfx(asset_get_index("BedroomOUT"), 1);
            }
        }
    }
    if (newlover_menu_toggle == false)
    {
        if (keyboard_check_pressed(ord("Q")) && options_toggle == false && selector_search_focused == false)
        {
            var _c_count = ds_list_size(custom_futas_folder);
            if (_c_count > 0 && random(1) < 0.85)
            {
                custom_lover_toggle = true;
                custom_futa_index = irandom(_c_count - 1);
                var _rf = ds_list_find_value(custom_futas_folder, custom_futa_index);
                var _alt_max = 1;
                while (file_exists(string(_rf) + "/custom_futa_mating_press_alt_" + string(_alt_max) + ".png"))
                {
                    _alt_max++;
                }
                custom_futa_alt_index = irandom(_alt_max - 1);
                func_load_custom_futa(_rf, custom_futa_alt_index);
                forced_sprite = is_legacy_custom ? legacy_custom_mating_press : custom_mating_press;
                top_sprite = forced_sprite;
                func_apply_custom_futa_stats();
            }
            else
            {
                custom_lover_toggle = false;
                func_randomize_top();
            }
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