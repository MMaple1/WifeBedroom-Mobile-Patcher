function func_load_custom_wife(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    if (file_exists(string(arg0) + "/custom_data.spouse") || file_exists(string(arg0) + "/custom_mating_press.png") || !file_exists(string(arg0) + "/custom_wife_mating_press_0.png"))