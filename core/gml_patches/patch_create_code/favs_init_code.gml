
global.favs_futa = ds_map_create();
global.favs_wife = ds_map_create();
selector_favs_only = false;

// Load persisted favorites and enhancement settings from session save component
if (file_exists("setting_data.sav"))
{
    ini_open("setting_data.sav");
    for (var _fi = 0; _fi < ds_list_size(custom_futas_folder); _fi++)
    {
        var _fn = filename_name(ds_list_find_value(custom_futas_folder, _fi));
        if (ini_read_real("favs_futa", _fn, 0) == 1)
        {
            ds_map_add(global.favs_futa, _fn, 1);
        }
    }
    for (var _wi = 0; _wi < ds_list_size(custom_wives_folder); _wi++)
    {
        var _wn = filename_name(ds_list_find_value(custom_wives_folder, _wi));
        if (ini_read_real("favs_wife", _wn, 0) == 1)
        {
            ds_map_add(global.favs_wife, _wn, 1);
        }
    }
    if (ini_key_exists("options", "hyper_sizes")) tc_hyper = bool(ini_read_real("options", "hyper_sizes", false));
    if (ini_key_exists("options", "selector_favs_only")) selector_favs_only = bool(ini_read_real("options", "selector_favs_only", false));
    ini_close();
}
