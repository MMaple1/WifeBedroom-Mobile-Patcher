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
                        func_load_custom_wife(_sel_folder, custom_wife_alt_index);
                        custom_wife_toggle = true;
                        var forced_bottom = legacy_custom_wife_toggle ? legacy_custom_wife_mating_press : custom_wife_mating_press;
                        bottom_sprite = forced_bottom;
                        func_validate_sex_position();
                        func_apply_custom_wife_stats();
                        func_bottom_speak("intro");
                    }