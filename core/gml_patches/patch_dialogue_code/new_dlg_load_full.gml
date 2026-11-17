function load_dialogue_file()
{
    func_load_dialogue(chosen_dialogue);
    if (chosen_dialogue == "")
    {
        return false;
    }
    var _file_name = "dialogue_packs/" + chosen_dialogue;
    if (file_exists("custom_stuff/dialogue_packs/" + chosen_dialogue))
    {
        _file_name = "custom_stuff/dialogue_packs/" + chosen_dialogue;
    }
    else if (!file_exists(_file_name))
    {
        if (file_exists("custom_dialogues/" + chosen_dialogue))
        {
            _file_name = "custom_dialogues/" + chosen_dialogue;
        }
        else if (file_exists("custom_stuff/dialogue/" + chosen_dialogue))
        {
            _file_name = "custom_stuff/dialogue/" + chosen_dialogue;
        }
        else if (file_exists("dialogue/" + chosen_dialogue))
        {
            _file_name = "dialogue/" + chosen_dialogue;
        }
        else if (file_exists(chosen_dialogue))
        {
            _file_name = chosen_dialogue;
        }
        else
        {
            return false;
        }
    }
    var _buffer = buffer_load(_file_name);
    if (_buffer == -1)
    {
        return false;
    }
    var _json_string = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);
    try
    {
        var _data = json_parse(_json_string);
        dialogue_json = _data;
        return true;
    }
    catch (_err)
    {
        show_debug_message("Dialogue JSON parse error bypassed safely");
        return false;
    }
}