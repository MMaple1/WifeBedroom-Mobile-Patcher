    var _valid_wife_port = -1;
    if (sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1) _valid_wife_port = custom_wife_portrait;
    else if (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1) _valid_wife_port = legacy_custom_wife_portrait;
    else _valid_wife_port = sFutaPortrait1;
    wife_bangs_sprite = _valid_wife_port;

    var _valid_wife_body = -1;
    if (sprite_exists(custom_wife_mating_press) && custom_wife_mating_press != -1) _valid_wife_body = custom_wife_mating_press;
    else if (sprite_exists(legacy_custom_wife_mating_press) && legacy_custom_wife_mating_press != -1) _valid_wife_body = legacy_custom_wife_mating_press;
    else _valid_wife_body = sWifeMatingPress;
    wife_hair_sprite = _valid_wife_body;