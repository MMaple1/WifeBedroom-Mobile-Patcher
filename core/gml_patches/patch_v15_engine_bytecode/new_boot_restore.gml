if (custom_sprite_loaded == true)
{
    if (remember_custom == true || true)
    {
        if (custom_lover_previous > -1 && custom_lover_previous < ds_list_size(custom_lover_folders))
        {
            custom_lover_selected = custom_lover_previous;
            func_set_custom_lover();
        }
        if (custom_partner_previous > -1 && custom_partner_previous < ds_list_size(custom_partner_folders))
        {
            custom_partner_selected = custom_partner_previous;
            func_set_custom_partner();
        }
        if (custom_bedroom_previous > -1 && custom_bedroom_previous < ds_list_size(custom_bedroom_folders))
        {
            custom_bedroom_selected = custom_bedroom_previous;
            func_set_custom_bedroom();
        }
    }
}