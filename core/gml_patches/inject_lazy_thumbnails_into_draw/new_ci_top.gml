        var _fname = ds_list_find_value(_sel_names, _ci);
        var _fav_map = (selector_mode == 0) ? global.favs_futa : global.favs_wife;
        var _is_fav = ds_map_exists(_fav_map, _fname);
        if (selector_favs_only && !_is_fav)
        {
            continue;
        }
        if (_search_lower != "" && string_pos(_search_lower, string_lower(_fname)) == 0)
        {
            continue;
        }