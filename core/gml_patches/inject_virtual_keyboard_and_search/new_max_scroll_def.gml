var _max_scroll = max(0, _total_content_w - room_width);
    if (!variable_instance_exists(id, "_sel_jump_done") || !_sel_jump_done)
    {
        _sel_jump_done = true;
        selector_favs_only = false;
        var _cur_idx = (selector_mode == 0) ? custom_futa_index : custom_wife_index;
        if (_cur_idx >= 0 && _cur_idx < _futa_count)
        {
            var _jump_pair = _cur_idx div 2;
            var _jump_scroll = clamp((_jump_pair * (_cell_w + _pad)) - (room_width * 0.5) + (_cell_w * 0.5), 0, _max_scroll);
            futa_selector_menu.scroll = _jump_scroll;
            futa_selector_menu.scroll_lerp = _jump_scroll;
        }
    }