                    case 8:
                        var custom_count = ds_list_size(custom_futas_folder);
                        if (custom_count > 0)
                        {
                            custom_futa_index = irandom(custom_count - 1);
                            var selected_folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
                            var randomizer_alt_max = 1;
                            while (file_exists(string(selected_folder) + "/custom_futa_mating_press_alt_" + string(randomizer_alt_max) + ".png"))
                            {
                                randomizer_alt_max++;
                            }
                            custom_futa_alt_index = irandom(randomizer_alt_max - 1);
                            func_load_custom_futa(selected_folder, custom_futa_alt_index);
                            forced_sprite = custom_mating_press;
                            custom_lover_toggle = true;
                        }
                        break;