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
                        func_validate_sex_position();
                        func_apply_custom_wife_stats();
                        custom_wife_toggle = true;
                        bottom_sprite = (sprite_exists(legacy_custom_wife_mating_press) && legacy_custom_wife_mating_press != -1) ? legacy_custom_wife_mating_press : ((sprite_exists(custom_wife_mating_press) && custom_wife_mating_press != -1) ? custom_wife_mating_press : sWifeMatingPress);
                        func_bottom_speak("intro");
                    }