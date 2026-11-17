        for (var i = 0; i < ds_list_size(custom_lover_folders); i++)
        {
            func_load_custom(ds_list_find_value(custom_lover_folders, i));
            custom_lover_portraits[i][0] = custom_portrait;
            custom_lover_info[i] = string(custom_name) + "\n\n" + string(custom_desc) + "\n\nCreated by " + string(custom_author);
            if (custom_portrait_alt != sWifeCanonPortrait)
            {
                custom_lover_portraits[i][1] = custom_portrait_alt;
            }
        }
        for (var i = 0; i < ds_list_size(custom_partner_folders); i++)
        {
            func_load_custom(ds_list_find_value(custom_partner_folders, i));
            custom_partner_portraits[i] = custom_portrait_alt;
            custom_partner_info[i] = string(custom_name) + "\n\n" + string(custom_desc) + "\n\nCreated by " + string(custom_author);
        }
        for (var i = 0; i < ds_list_size(custom_bedroom_folders); i++)
        {
            func_load_custom(ds_list_find_value(custom_bedroom_folders, i));
            custom_bedroom_thumbnails[i] = custom_thumbnail;
            custom_bedroom_info[i] = string(custom_name) + "\n\n" + string(custom_desc) + "\n\nCreated by " + string(custom_author);
        }