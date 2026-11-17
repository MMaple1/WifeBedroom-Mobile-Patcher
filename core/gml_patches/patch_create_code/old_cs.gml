var _cs_base = tc_wd + "/custom_sounds/futa";
if (tc_dir_exists(_cs_base))
{
    var _cs_file = tc_ff_first(_cs_base + "/*", 16);
    while (_cs_file != "")
    {
        var _cs_full = _cs_base + "/" + _cs_file;
        if (tc_dir_exists(_cs_full))
        {
            ds_list_add(cs_futa_packs, _cs_full);
            ds_list_add(cs_futa_pack_names, _cs_file);
        }
        _cs_file = tc_ff_next();
    }
    tc_ff_close();
}