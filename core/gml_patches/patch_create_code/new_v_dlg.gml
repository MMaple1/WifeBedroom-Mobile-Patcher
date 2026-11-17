function func_load_vanilla_dialogue(arg0)
{
    custom_dialogue_set_top = -1;
    var _path = (os_type == os_android || os_type == os_ios) ? ("dialogue/" + arg0) : (working_directory + "dialogue/" + arg0);
    if (!file_exists(_path))
    {
        _path = "dialogue_packs/" + arg0;
        if (!file_exists(_path))
        {
            exit;
        }
    }