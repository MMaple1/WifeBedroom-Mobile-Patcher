        else if (_has_custom_top)
        {
            var _dlg_key = arg0;
            if (_dlg_key == "top_close_to_orgasm")
            {
                _dlg_key = "sex_halfway";
            }
            else if (_dlg_key == "condom_broke")
            {
                _dlg_key = "condom_broken";
            }
            else if (_dlg_key == "remove_full_condom")
            {
                _dlg_key = "condom_off";
            }
            else if (_dlg_key == "sex_after_with_condom")
            {
                _dlg_key = "sex_after";
            }
            else if (_dlg_key == "impregnate")
            {
                _dlg_key = "sex_orgasm";
            }
            else if (_dlg_key == "impregnate_after")
            {
                _dlg_key = "sex_after";
            }
            var _set = oFutaMatingPress.custom_dialogue_set_top;
            if (variable_struct_exists(_set, _dlg_key))
            {
                var _arr = variable_struct_get(_set, _dlg_key);
                if (is_array(_arr) && array_length(_arr) > 0)
                {
                    var _picked = _arr[irandom(array_length(_arr) - 1)];
                    if (_picked != "")
                    {
                        _picked = string_replace_all(_picked, "{0}", inject);
                        _picked = oFutaMatingPress.func_replace_tags(_picked);
                        lover_text = _picked;
                    }
                }
            }
        }
        else
        {
            lover_text = pick_from_dialogue_json(arg0, inject);
        }