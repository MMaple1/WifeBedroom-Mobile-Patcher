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
            else if (_bkcode == 77) // [M] MAN - directly toggles manual mode WITHOUT closing drawer!
            {
                if (variable_instance_exists(id, "manual_mode"))
                {
                    manual_mode = (manual_mode == 0) ? 1 : ((manual_mode == 1) ? 2 : 0);
                    if (variable_instance_exists(id, "manual_ui_visible"))
                        manual_ui_visible = (manual_mode > 0);
                }
            }
            else if (_bkcode == 84) // [T] PEEK - directly toggles peek screen with zero warning interruption
            {
                title = !title;
                peek_closed_during_play = true;
                disclaimer = false;
                mob_expanded = false;
            }
            else if (_bkcode == 71) // [G] GHOST - directly toggles ghost mode WITHOUT closing drawer!
            {
                if (variable_instance_exists(id, "futa_ghost_toggle"))
                {
                    futa_ghost_toggle = !futa_ghost_toggle;
                    futa_ghost_alpha = futa_ghost_toggle ? 0.5 : 1;
                }
            }
            else if (_bkcode == 81) // [Q] REROLL - directly rerolls character favoring custom assets WITHOUT closing drawer!
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
                loads = 0;
            }
            else if (_bkcode == 72) // [H] HITBOX - directly toggles hitbox AND closes overlay!
            {
                mob_hitbox_active = !mob_hitbox_active;
                mob_expanded = false;
            }
            else if (_bkcode == "RESET_DEFAULTS") // [RESET OPTIONS] - resets ALL options and non-default variables to defaults
            {
                // Audio
                global.vol_master = 1;
                global.vol_sfx = 1;
                global.vol_voice = 1;
                global.vol_ambient = 1;
                global.audio_master_on = true;
                global.audio_sfx_on = true;
                global.audio_voice_on = true;

                // Visuals & Types
                skip_disclaimer = false;
                xray = true;
                futa_pussy_toggle = true;
                futa_ghost_toggle = false;
                futa_ghost_alpha = 1;

                // Mechanics
                knotting_toggle = true;
                knotted_max_time = 600;
                womb_inflation_toggle = true;
                womb_inflation_scale = 1;
                slip_toggle = false;
                slip_chance = 1;
                reenter_toggle = false;
                reenter_max_timer = false;
                condom_break_toggle = false;
                condom_break_threshold = 10;

                // Values
                pump_delay = 90;
                cum_shot_mult = 1;
                stroke_depth = 1;
                stroke_speed = 1;

                // Features
                rand_pumps_toggle = false;
                hearts_toggle = true;
                frustration_toggle = true;
                global.pop_sound_toggle = true;
                kiss_toggle = 1;
                drip_toggle = true;
                cum_batching_toggle = false;
                custom_clench_toggle = 0;
                continuous_toggle = false;

                // Texture Pack
                if (chosen_texture_pack != "default")
                {
                    func_texture_pack_replace("default");
                    chosen_texture_pack = "default";
                }

                // Dialogue
                if (instance_exists(oDialogueManager)) { oDialogueManager.dialogue_toggle = true; }
                char_dialogue_toggle = true;
                global.dialogue_display_index = 0;
                dialogue_display_index = 0;
                global.speaker_type_index = 0;
                oDialogueManager.dialogue_cooldown = 30;
                global.dialogue_additional_duration = 0;
                text_scale_l = 1;
                text_scale_w = 1;
                max_lover_dialogue_width = 200;
                max_wife_dialogue_width = 200;
                top_dlg_x = 0;
                top_dlg_y = 0;
                wife_dlg_x = 3;
                wife_dlg_y = 0;
                oDialogueManager.top_dialogue_color = 12976127;
                oDialogueManager.wife_dialogue_color = 13408767;
                oDialogueManager.current_top_color = 12976127;
                oDialogueManager.current_wife_color = 13408767;
                oDialogueManager.chosen_dialogue = "aathefintree.json";
                oDialogueManager.func_load_dialogue("aathefintree.json");

                // Bunny Panel
                bunny_panel_x_saved = 300;
                bunny_panel_y_saved = 30;
                bunny_small_x_saved = 300;
                bunny_small_y_saved = 25;

                // Custom Sounds
                cs_futa_pack_index = 0;
                cs_futa_alt_index = 0;
                cs_moan_chance_slow = 0.4;
                cs_moan_chance_fast = 0.55;
                cs_orgasm_grunt_chance = 0.45;
                cs_wife_pack_index = 0;
                cs_wife_alt_index = 0;
                cs_wife_moan_chance_slow = 0.35;
                cs_wife_moan_chance_fast = 0.55;
                cs_wife_kiss_enabled = true;

                // Background Colors
                bg_randomize_colors = true;
                saved_bg_wallpaper = -1;
                saved_bg_carpet = -1;
                saved_bg_trim = -1;
                saved_bg_dresser = -1;
                saved_bg_mattress = -1;
                saved_bg_frame = -1;
                saved_bg_ship = -1;
                saved_bg_console = -1;
                saved_bg_screen = -1;
                saved_bg_glass = -1;
                saved_bg_vip_wall = -1;
                saved_bg_vip_stage = -1;
                saved_bg_vip_pole = -1;
                saved_bg_vip_underwear = -1;
                saved_bg_vip_condoms = -1;
                saved_bg_vip_lotion = -1;
                saved_bg_vip_mattress = -1;
                saved_bg_vip_frame = -1;
                saved_bg_beach_water = -1;
                saved_bg_beach_sky = -1;
                saved_bg_beach_sun = -1;
                saved_bg_beach_clouds = -1;
                saved_bg_beach_sand = -1;
                saved_bg_beach_stuff = -1;
                saved_bg_office_wall = -1;
                saved_bg_office_floor = -1;
                saved_bg_office_desk = -1;
                saved_bg_dungeon_floor = -1;
                saved_bg_dungeon_wall = -1;
                saved_bg_dungeon_gate = -1;
                saved_bg_dungeon_chest = -1;
                saved_bg_dungeon_chesttrim = -1;
                saved_bg_dungeon_torch = -1;
                saved_bg_dungeon_flame = -1;

                // Radio
                radio_track_index = 0;
                radio_volume = 1;
                radio_shuffle = 0;

                // Manual Mode & Values2
                manual_mode = 0;
                manual_ui_visible = false;
                manual_pump_speed = 4;
                manual_thrust_sens = 0.05;
                manual_thrust_strength = 2;
                manual_hip_sens = 0.5;
                combo_text_max = 0;
                max_combo_display = 0;
                manual_last_mode = 1;
                manual_auto_pumps = false;
                machinegun_toggle = false;
                mg_interval_min = 4;
                mg_interval_max = 14;
                mg_spread = 0.2;
                mg_burst_min = 1;
                mg_burst_max = 2;
                overflow_delay = 0;

                // Responses
                wife_climax_stamina = 100;
                wife_pleasure_threshold = 100;
                wife_pleasure_max = 100;
                wife_womb_capacity = 20;
                fill_max = 20;

                // Gameplay State
                func_reset_sex_stats();
                sex_progress = 0;
                edge_charge = 0;
                loads = 0;
                wife_climax_counter = 0;
                impregnation_counter = 0;
                body_jiggle = 0;

                // Panel Positions & Menu States
                newlover_menu_cx = 65;
                newlover_menu_cy_end_offset = 50;
                newwife_menu_x = room_width - 260;
                newwife_menu_y = room_height - 100;
                options_toggle = false;
                radial_menu_open = false;
                radial_sub_menu = "";
                background_menu_toggle = false;
                position_menu_toggle = false;
                pill_menu_toggle = false;
                dialogue_menu_toggle = false;
                radio_toggle = false;
                tab_quicknav_open = false;
                actions_menu_toggle = false;
                color_picker_active = false;
                futa_selector_open = false;
                newlover_menu_toggle = false;
                newwife_menu_toggle = false;
                mob_hitbox_active = false;
                keyboard_key_release(ord("H"));
                mob_expanded = false;

                // Delete persisted settings file and save clean defaults
                if (file_exists("setting_data.sav"))
                    file_delete("setting_data.sav");
                if (file_exists(working_directory + "/setting_data.sav"))
                    file_delete(working_directory + "/setting_data.sav");
                func_save_settings();

                oAudioManager.play_sfx(asset_get_index("StarshipOUT"), 1);
            }
            else
            {
                keyboard_key_press(_bkcode);
                mob_release_key = _bkcode;
            }
        }