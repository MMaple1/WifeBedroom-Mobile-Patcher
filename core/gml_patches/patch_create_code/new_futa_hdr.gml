function func_load_custom_futa(arg0, arg1 = 0)
{
    arg0 = tc_norm_path(arg0);
    is_legacy_custom = false;
    if (file_exists(string(arg0) + "/custom_mating_press.png") || !file_exists(string(arg0) + "/custom_futa_mating_press_0.png"))