function check_custom_futa(arg0)
{
    arg0 = tc_norm_path(arg0);
    var is_legacy = false;
    if (file_exists(string(arg0) + "/custom_mating_press.png"))
    {
        is_legacy = check_custom_image_size(arg0);
    }
    check_struct = {};
    if (is_legacy)
    {
        check_struct.custom_data = file_exists(string(arg0) + "/custom_data.futa");
        check_struct.custom_portrait = file_exists(string(arg0) + "/custom_portrait.png");
        check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_mating_press.png");
        check_struct.custom_cowgirls = file_exists(string(arg0) + "/custom_reverse_cowgirl.png");
        check_struct.custom_xray = file_exists(string(arg0) + "/custom_xray.png");
    }
    else
    {
        check_struct.custom_data = file_exists(string(arg0) + "/custom_data.futa");
        check_struct.custom_portrait = file_exists(string(arg0) + "/custom_futa_portrait_0.png");
        check_struct.custom_mating_press = file_exists(string(arg0) + "/custom_futa_mating_press_0.png");
        check_struct.custom_cowgirls = file_exists(string(arg0) + "/custom_futa_cowgirls_0.png");
        check_struct.custom_xray = file_exists(string(arg0) + "/custom_futa_xray_0.png");
    }
    return check_struct;
}