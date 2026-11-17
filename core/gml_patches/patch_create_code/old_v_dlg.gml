function func_load_vanilla_dialogue(arg0)
{
    custom_dialogue_set_top = -1;
    var _path = working_directory + "dialogue/" + arg0;
    if (!file_exists(_path))
    {
        exit;
    }