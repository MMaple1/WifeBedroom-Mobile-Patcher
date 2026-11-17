                    if (selector_mode == 0)
                    {
                        custom_futa_index = _ci;
                        custom_futa_alt_index = 0;
                        var _sel_folder = ds_list_find_value(custom_futas_folder, custom_futa_index);
                        custom_default_moans = false;
                        ds_list_clear(custom_moan_slow_list);
                        ds_list_clear(custom_moan_fast_list);
                        ds_list_clear(custom_orgasm_list);
                        ds_list_clear(moan_slow_list);
                        ds_list_clear(moan_fast_list);
                        ds_list_clear(orgasm_list);
                        moan_previous = -1;
                        if (os_type == os_android || os_type == os_ios)
                        {
                            keyboard_virtual_hide();
                        }
                        selector_search_focused = false;
                        func_load_custom_futa(_sel_folder, custom_futa_alt_index);
                        custom_lover_toggle = true;
                        var forced_sprite = is_legacy_custom ? legacy_custom_mating_press : custom_mating_press;
                        top_sprite = forced_sprite;
                        func_apply_custom_futa_stats();
                        func_top_speak("intro");
                        loads = 0;
                        sex_progress = 0;
                    }