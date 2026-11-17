function check_custom_wife(arg0)
{
    check_struct = {};
    check_struct.custom_data = file_exists(string(arg0) + "/custom_data.wife");
    check_struct.custom_wife_mating_press = file_exists(string(arg0) + "/custom_wife_mating_press_0.png");
    check_struct.custom_wife_cowgirl = file_exists(string(arg0) + "/custom_wife_cowgirl_0.png");
    check_struct.custom_wife_reverse_cowgirl = file_exists(string(arg0) + "/custom_wife_reverse_cowgirl_0.png");
    check_struct.custom_wife_portrait = file_exists(string(arg0) + "/custom_wife_portrait_0.png");
    return check_struct;
}