function check_custom_futa(arg0)
{
    check_struct = {};
    check_struct.custom_data = true;
    check_struct.custom_portrait = file_exists(string(arg0) + "/custom_futa_portrait_0.png") || file_exists(string(arg0) + "/custom_portrait.png") || file_exists(string(arg0) + "/custom_futa_portrait.png");
    check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_futa_mating_press_0.png") || file_exists(string(arg0) + "/custom_mating_press.png") || file_exists(string(arg0) + "/custom_futa_mating_press.png");
    check_struct.custom_cowgirls = file_exists(string(arg0) + "/custom_futa_cowgirls_0.png") || file_exists(string(arg0) + "/custom_reverse_cowgirl.png") || file_exists(string(arg0) + "/custom_cowgirl.png");
    check_struct.custom_xray = file_exists(string(arg0) + "/custom_futa_xray_0.png") || file_exists(string(arg0) + "/custom_xray.png") || file_exists(string(arg0) + "/custom_futa_xray.png");
    return check_struct;
}