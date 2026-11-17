function load_dialogue_file()
{
    var check_load_dialogue = func_load_dialogue(chosen_dialogue);
    if (check_load_dialogue == "")
    {
        exit;
    }
    var _file_name = "dialogue_packs/" + chosen_dialogue;
    if (!file_exists(_file_name))
    {
        if (file_exists("custom_dialogues/" + chosen_dialogue))
        {
            _file_name = "custom_dialogues/" + chosen_dialogue;
        }
    }
    var _buffer = buffer_load(_file_name);
    var _json_string = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);
    var _data = json_parse(_json_string);
    dialogue_json = _data;
    return true;
}