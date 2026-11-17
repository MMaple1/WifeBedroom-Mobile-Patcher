                    case 6:
                        custom_wife_toggle = true;
                        var custom_count = ds_list_size(custom_wives_folder);
                        if (custom_count > 0)
                        {
                            custom_wife_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_wife_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_wife_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_wife(selected_folder, custom_wife_alt_index);
                            func_validate_sex_position();
                            forced_bottom = custom_wife_mating_press;
                        }
                        break;
                    case 7:
                        var vanilla_wives = [sWifeMatingPress, sWifeMatingPressDevil, sWifeMatingPressFurry, sWifeMatingPressSlime, sWifeMatingPressAndroid];
                        forced_bottom = vanilla_wives[irandom(array_length(vanilla_wives) - 1)];
                        custom_wife_toggle = false;
                        legacy_custom_wife_toggle = false;
                        break;
                }
                bottom_skin_color_val = witem_hover_1 ? random_range(200, 500) : (witem_hover_2 ? random_range(175, 200) : (witem_hover_3 ? random_range(80, 150) : -1));
                func_randomize_bottom(forced_bottom, bottom_skin_color_val);