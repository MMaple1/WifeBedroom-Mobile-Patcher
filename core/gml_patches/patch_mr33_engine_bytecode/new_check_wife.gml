function check_custom_wife(arg0)
{
    check_struct = {};
    check_struct.custom_data = file_exists(string(arg0) + "/custom_data.wife") || file_exists(string(arg0) + "/custom_data.spouse") || file_exists(string(arg0) + "/custom_data.futa") || file_exists(string(arg0) + "/custom_data.txt");
    check_struct.custom_wife_mating_press = file_exists(string(arg0) + "/custom_wife_mating_press_0.png") || file_exists(string(arg0) + "/custom_mating_press.png") || file_exists(string(arg0) + "/custom_wife_mating_press.png");
    check_struct.custom_wife_cowgirl = file_exists(string(arg0) + "/custom_wife_cowgirl_0.png") || file_exists(string(arg0) + "/custom_cowgirl.png") || file_exists(string(arg0) + "/custom_wife_cowgirl.png");
    check_struct.custom_wife_reverse_cowgirl = file_exists(string(arg0) + "/custom_wife_reverse_cowgirl_0.png") || file_exists(string(arg0) + "/custom_reverse_cowgirl.png") || file_exists(string(arg0) + "/custom_wife_reverse_cowgirl.png");
    check_struct.custom_wife_portrait = file_exists(string(arg0) + "/custom_wife_portrait_0.png") || file_exists(string(arg0) + "/custom_portrait.png") || file_exists(string(arg0) + "/custom_wife_portrait.png");
    return check_struct;
}