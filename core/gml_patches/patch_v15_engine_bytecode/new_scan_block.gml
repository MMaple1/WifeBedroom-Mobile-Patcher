var _manifest_p = "custom/_manifest.txt";
if (!file_exists(_manifest_p) && game_dir != "")
{
    _manifest_p = game_dir + "/custom/_manifest.txt";
}
var _mani_buf = buffer_load(_manifest_p);
if (_mani_buf != -1)
{
    var _mani_str = buffer_read(_mani_buf, buffer_string);
    buffer_delete(_mani_buf);
    var _m_len = string_length(_mani_str);
    var _start_idx = 1;
    var _pos = 1;
    while (_pos <= _m_len)
    {
        var _c = string_char_at(_mani_str, _pos);
        if (_c == "\n" || _c == "\r")
        {
            if (_pos > _start_idx)
            {
                var _m_line = string_copy(_mani_str, _start_idx, _pos - _start_idx);
                while (string_char_at(_m_line, 1) == " ") _m_line = string_delete(_m_line, 1, 1);
                while (string_char_at(_m_line, string_length(_m_line)) == " ") _m_line = string_delete(_m_line, string_length(_m_line), 1);
                if (_m_line != "" && _m_line != "_manifest.txt")
                {
                    var _file = (os_type == os_android || os_type == os_ios) ? ("custom/" + _m_line) : (game_dir + "/custom/" + _m_line);
                    if (file_exists(_file + "/custom_data.futa"))
                    {
                        if (ds_list_find_index(custom_lover_folders, _file) == -1) ds_list_add(custom_lover_folders, _file);
                    }
                    else if (file_exists(_file + "/custom_data.spouse") || file_exists(_file + "/custom_data.wife"))
                    {
                        if (ds_list_find_index(custom_partner_folders, _file) == -1) ds_list_add(custom_partner_folders, _file);
                    }
                    else if (file_exists(_file + "/custom_data.bedroom"))
                    {
                        if (ds_list_find_index(custom_bedroom_folders, _file) == -1) ds_list_add(custom_bedroom_folders, _file);
                    }
                }
            }
            _start_idx = _pos + 1;
        }
        _pos++;
    }
    if (_pos > _start_idx)
    {
        var _m_line = string_copy(_mani_str, _start_idx, _pos - _start_idx);
        while (string_char_at(_m_line, 1) == " ") _m_line = string_delete(_m_line, 1, 1);
        while (string_char_at(_m_line, string_length(_m_line)) == " ") _m_line = string_delete(_m_line, string_length(_m_line), 1);
        if (_m_line != "" && _m_line != "_manifest.txt")
        {
            var _file = (os_type == os_android || os_type == os_ios) ? ("custom/" + _m_line) : (game_dir + "/custom/" + _m_line);
            if (file_exists(_file + "/custom_data.futa"))
            {
                if (ds_list_find_index(custom_lover_folders, _file) == -1) ds_list_add(custom_lover_folders, _file);
            }
            else if (file_exists(_file + "/custom_data.spouse") || file_exists(_file + "/custom_data.wife"))
            {
                if (ds_list_find_index(custom_partner_folders, _file) == -1) ds_list_add(custom_partner_folders, _file);
            }
            else if (file_exists(_file + "/custom_data.bedroom"))
            {
                if (ds_list_find_index(custom_bedroom_folders, _file) == -1) ds_list_add(custom_bedroom_folders, _file);
            }
        }
    }
    if (ds_list_size(custom_lover_folders) > 0 || ds_list_size(custom_partner_folders) > 0 || ds_list_size(custom_bedroom_folders) > 0)
    {
        custom_sprite_loaded = true;
        tutorial = false;
    }
}
if (true && mobile == false)