var file_check = string(arg0) + "/custom_wife_portrait" + _suffix;
    if (!file_exists(file_check)) file_check = string(arg0) + "/custom_portrait.png";
    if (!file_exists(file_check)) file_check = string(arg0) + "/custom_wife_portrait.png";