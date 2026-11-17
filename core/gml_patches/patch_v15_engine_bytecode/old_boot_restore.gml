if (custom_sprite_loaded == true)
{
    if (remember_custom == true)
    {
        if (ds_list_size(custom_lover_folders) > 0)
        {
            custom_lover_selected = custom_lover_previous;
            func_set_custom_lover();
        }
        if (ds_list_size(custom_partner_folders) > 0)
        {
            custom_partner_selected = custom_partner_previous;
            func_set_custom_partner();
        }
    }
    else
    {
        var custom_chance = irandom(3);
        if (custom_chance == 0)
        {
            if (ds_list_size(custom_lover_folders) > 0)
            {
                custom_lover_selected = irandom(ds_list_size(custom_lover_folders) - 1);
                func_set_custom_lover();
            }
            if (ds_list_size(custom_partner_folders) > 0)
            {
                custom_partner_selected = irandom(ds_list_size(custom_partner_folders) - 1);
                func_set_custom_partner();
            }
        }
    }
}