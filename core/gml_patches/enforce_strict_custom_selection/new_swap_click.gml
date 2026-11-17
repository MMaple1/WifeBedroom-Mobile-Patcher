                        if (os_type == os_android || os_type == os_ios)
                        {
                            keyboard_virtual_hide();
                        }
                        selector_search_focused = false;
                        var _is_legacy_futa = file_exists(_sel_folder + "/custom_data.futa") && !file_exists(_sel_folder + "/custom_futa_mating_press_0.png");
                        is_legacy_custom = _is_legacy_futa;
                        func_load_custom_futa(_sel_folder, custom_futa_alt_index);
                        custom_lover_toggle = true;
                        forced_sprite = is_legacy_custom ? legacy_custom_mating_press : custom_mating_press;
                        if (forced_sprite != -1 && sprite_exists(forced_sprite))
                        {
                            top_sprite = forced_sprite;
                            func_apply_custom_futa_stats();
                        }
                        else
                        {
                            top_sprite = sFutaMatingPress;
                        }
                        func_top_speak("intro");
                        loads = 0;
                        sex_progress = 0;
                    }
                    else
                    {
                        if (os_type == os_android || os_type == os_ios)
                        {
                            keyboard_virtual_hide();
                        }
                        selector_search_focused = false;
                        custom_wife_index = _ci;
                        custom_wife_alt_index = 0;
                        var _sel_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        var _is_legacy_spouse = file_exists(_sel_folder + "/custom_data.spouse") || file_exists(_sel_folder + "/custom_mating_press.png");
                        if (_is_legacy_spouse)
                        {
                            func_load_custom_spouse(_sel_folder);
                            legacy_custom_wife_toggle = true;
                            custom_wife_toggle = true;
                            forced_bottom = legacy_custom_wife_mating_press;
                        }
                        else
                        {
                            func_load_custom_wife(_sel_folder, custom_wife_alt_index);
                            legacy_custom_wife_toggle = false;
                            custom_wife_toggle = true;
                            forced_bottom = custom_wife_mating_press;
                        }
                        if (forced_bottom != -1 && sprite_exists(forced_bottom))
                        {
                            bottom_sprite = forced_bottom;
                            func_apply_custom_wife_stats();
                        }
                        else
                        {
                            bottom_sprite = sWifeMatingPress;
                        }
                        func_validate_sex_position();