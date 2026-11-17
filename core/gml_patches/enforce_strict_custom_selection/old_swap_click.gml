                        func_load_custom_futa(_sel_folder, custom_futa_alt_index);
                        func_apply_custom_futa_stats();
                        func_top_speak("intro");
                        loads = 0;
                        sex_progress = 0;
                    }
                    else
                    {
                        custom_wife_index = _ci;
                        custom_wife_alt_index = 0;
                        var _sel_folder = ds_list_find_value(custom_wives_folder, custom_wife_index);
                        func_load_custom_wife(_sel_folder, custom_wife_alt_index);
                        func_apply_custom_wife_stats();