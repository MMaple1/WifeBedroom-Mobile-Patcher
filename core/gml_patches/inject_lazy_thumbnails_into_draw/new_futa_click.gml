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
                        func_apply_custom_futa_stats();
                        custom_lover_toggle = true;
                        top_sprite = (sprite_exists(custom_mating_press) && custom_mating_press != -1) ? custom_mating_press : ((sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press != -1) ? legacy_custom_mating_press : sFutaMatingPress);
                        if (!sprite_exists(penis_sprite) || penis_sprite == -1) penis_sprite = top_sprite;
                        if (!sprite_exists(hair_sprite) || hair_sprite == -1) hair_sprite = top_sprite;
                        func_top_speak("intro");
                        loads = 0;
                        sex_progress = 0;
                    }