var _cs_bases = ["custom_sounds/futa", "custom_sounds"];
for (var _bi = 0; _bi < array_length(_cs_bases); _bi++)
{
    var _base = _cs_bases[_bi];
    var _cs_file = tc_ff_first(_base + "/*", 16);
    while (_cs_file != "")
    {
        if (_cs_file != "." && _cs_file != ".." && _cs_file != "futa" && _cs_file != "wife (placeholder)" && _cs_file != "sfx (placeholder)")
        {
            var _cs_full = _base + "/" + _cs_file;
            if (file_exists(_cs_full + "/moan_slow/_manifest.txt") || file_exists(_cs_full + "/moan_fast/_manifest.txt") || file_exists(_cs_full + "/_manifest.txt") || tc_dir_exists(_cs_full))
            {
                if (ds_list_find_index(cs_futa_pack_names, _cs_file) == -1)
                {
                    ds_list_add(cs_futa_packs, _cs_full);
                    ds_list_add(cs_futa_pack_names, _cs_file);
                }
            }
        }
        _cs_file = tc_ff_next();
    }
    tc_ff_close();
}