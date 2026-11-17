    if (custom_sprite_loaded == true)
    {
        draw_text_ext_color(room_width / 2, room_height / 2, "WARNING:\n\nThis game contains explicit content intended for adults only. It also contains fetishistic content (i.e. futanari, excessive liquids) that may not be suitable for everyone. It is also intended to display a polyamorous relationship, but may come across as cuckoldry/NTR depending on how you interact with it.\n\nPlayer discretion is advised.\nClick to continue", 16, 320, c_white, c_white, c_white, c_white, disclaimer_scale * title_scale);
    }
    else
    {
        draw_text_ext_color(room_width / 2, room_height / 2, "\n\n\nCustom futas must be placed in /custom_futas\nCustoom wives must be placed in /custom_wives\nClick to continue", 16, 320, c_red, c_red, c_red, c_red, disclaimer_scale * title_scale);
    }