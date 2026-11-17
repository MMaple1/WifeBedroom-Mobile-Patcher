for (var _fi = 0; _fi < array_length(_futa_names); _fi++)
{
    var _file = _futa_names[_fi];
    var _full_path = _is_mobile ? ("custom_futas/" + _file) : (_wd + "/custom_futas/" + _file);
    if (_futa_manifest || tc_dir_exists(_full_path))