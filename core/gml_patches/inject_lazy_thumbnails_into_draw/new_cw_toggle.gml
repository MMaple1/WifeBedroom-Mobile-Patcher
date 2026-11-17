                    else
                    {
                        var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        func_load_custom_wife(selected_folder, custom_wife_alt_index);
                        func_validate_sex_position();
                        func_apply_custom_wife_stats();
                        var _fb = legacy_custom_wife_toggle ? legacy_custom_wife_mating_press : custom_wife_mating_press;
                        if (_fb != -1 && sprite_exists(_fb))
                        {
                            bottom_sprite = _fb;
                        }
                        else
                        {
                            bottom_sprite = sWifeMatingPress;
                        }
                    }