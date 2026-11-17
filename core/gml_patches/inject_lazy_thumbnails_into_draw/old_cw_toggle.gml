                    else
                    {
                        var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        func_load_custom_wife(selected_folder, custom_wife_alt_index);
                        func_validate_sex_position();
                        var forced_bottom = legacy_custom_wife_toggle ? legacy_custom_wife_mating_press : custom_wife_mating_press;
                        if (forced_bottom != -1 && sprite_exists(forced_bottom))
                        {
                            bottom_sprite = forced_bottom;
                            func_apply_custom_wife_stats();
                        }
                        else
                        {
                            func_randomize_bottom();
                        }
                    }