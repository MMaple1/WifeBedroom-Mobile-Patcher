if (ds_map_find_value(async_load, "id") == pm_http)
{
    var _pm_state = ds_map_find_value(async_load, "status");
    if (_pm_state == 1)
    {
        var _pm_got = ds_map_find_value(async_load, "sizeDownloaded");
        if (!is_undefined(_pm_got))
        {
            pm_status = "Downloading... " + string(floor(_pm_got / 1024)) + " KB";
        }
    }
    else
    {
        pm_http = -1;
        var _pm_save = game_save_id;
        if (string_char_at(_pm_save, string_length(_pm_save)) == "/")
        {
            _pm_save = string_copy(_pm_save, 1, string_length(_pm_save) - 1);
        }
        var _pm_zip = _pm_save + "/phone_mods_dl.zip";
        var _pm_fn = pm_url;
        if (string_pos("?", _pm_fn) > 0)
        {
            _pm_fn = string_copy(_pm_fn, 1, string_pos("?", _pm_fn) - 1);
        }
        while (string_pos("/", _pm_fn) > 0)
        {
            _pm_fn = string_delete(_pm_fn, 1, string_pos("/", _pm_fn));
        }
        _pm_fn = string_replace_all(_pm_fn, "%20", "_");
        var _pm_code = ds_map_find_value(async_load, "http_status");
        if (_pm_state == 0 && _pm_code == 200 && file_exists(_pm_zip))
        {
            var _pm_added = 0;
            var _pm_bg = 0;
            var _pm_dlg = 0;
            var _pm_tex = 0;
            var _pm_voice = 0;
            var _pm_dups = 0;
            var _pm_dupdirs = [];
            pm_seq++;
            var _pm_dest = _pm_save + "/phone_mods/dl_" + string_replace_all(string_format(date_current_datetime(), 1, 6), ".", "_") + "_" + string(pm_seq);
            var _pm_base = string_copy(_pm_fn, 1, max(1, string_length(_pm_fn) - 4));
            directory_create(_pm_dest);
            if (zip_unzip(_pm_zip, _pm_dest + "/" + _pm_base + "/") <= 0)
            {
                pm_status = "That file is not a .zip the game can open.";
                var _pm_fl = string_lower(_pm_fn);
                if (string_copy(_pm_fl, string_length(_pm_fl) - 4, 5) == ".json")
                {
                    if (!tc_dir_exists(_pm_save + "/dialogue_packs"))
                    {
                        directory_create(_pm_save + "/dialogue_packs");
                    }
                    file_copy(_pm_zip, _pm_save + "/dialogue_packs/" + _pm_fn);
                    _pm_dlg++;
                    pm_status = "Added dialogue pack " + _pm_fn + " - restart the game to use it.";
                }
                var _pm_xq = [_pm_dest];
                var _pm_xi = 0;
                while (_pm_xi < array_length(_pm_xq))
                {
                    var _pm_xd = _pm_xq[_pm_xi];
                    _pm_xi++;
                    var _pm_xn = [];
                    var _pm_xf = tc_ff_first(_pm_xd + "/*", 16);
                    while (_pm_xf != "")
                    {
                        if (_pm_xf != "." && _pm_xf != "..")
                        {
                            array_push(_pm_xn, _pm_xf);
                        }
                        _pm_xf = tc_ff_next();
                    }
                    tc_ff_close();
                    for (var _pm_xk = 0; _pm_xk < array_length(_pm_xn); _pm_xk++)
                    {
                        if (tc_dir_exists(_pm_xd + "/" + _pm_xn[_pm_xk]))
                        {
                            array_push(_pm_xq, _pm_xd + "/" + _pm_xn[_pm_xk]);
                        }
                        else
                        {
                            file_delete(_pm_xd + "/" + _pm_xn[_pm_xk]);
                        }
                    }
                }
                var _pm_xr = array_length(_pm_xq) - 1;
                while (_pm_xr >= 0)
                {
                    directory_destroy(_pm_xq[_pm_xr]);
                    if (tc_dir_exists(_pm_xq[_pm_xr]))
                    {
                        file_delete(_pm_xq[_pm_xr]);
                    }
                    _pm_xr--;
                }
            }
            else
            {
                _pm_added = 0;
                var _pm_queue = [_pm_dest];
                var _pm_names = ["mod"];
                var _pm_depths = [0];
                var _pm_qi = 0;
                while (_pm_qi < array_length(_pm_queue))
                {
                    var _pm_dir = _pm_queue[_pm_qi];
                    var _pm_name = _pm_names[_pm_qi];
                    var _pm_depth = _pm_depths[_pm_qi];
                    _pm_qi++;
                    if (file_exists(_pm_dir + "/custom_data.futa") || file_exists(_pm_dir + "/custom_data.wife") || file_exists(_pm_dir + "/custom_data.spouse"))
                    {
                        var _pm_dfile = "custom_data.spouse";
                        var _pm_dlist = custom_wives_folder;
                        if (file_exists(_pm_dir + "/custom_data.futa"))
                        {
                            _pm_dfile = "custom_data.futa";
                            _pm_dlist = custom_futas_folder;
                        }
                        else if (file_exists(_pm_dir + "/custom_data.wife"))
                        {
                            _pm_dfile = "custom_data.wife";
                        }
                        var _pm_dup = false;
                        var _pm_hash = "";
                        if (file_exists(_pm_dir + "/" + _pm_dfile))
                        {
                            _pm_hash = md5_file(_pm_dir + "/" + _pm_dfile);
                        }
                        var _pm_pn = [];
                        var _pm_pf = tc_ff_first(_pm_dir + "/*.png", 0);
                        while (_pm_pf != "" && array_length(_pm_pn) < 3)
                        {
                            array_push(_pm_pn, _pm_pf);
                            _pm_pf = tc_ff_next();
                        }
                        tc_ff_close();
                        if (string_length(_pm_hash) == 32 && array_length(_pm_pn) > 0)
                        {
                            var _pm_ph = [];
                            for (var _pm_pj = 0; _pm_pj < array_length(_pm_pn); _pm_pj++)
                            {
                                array_push(_pm_ph, md5_file(_pm_dir + "/" + _pm_pn[_pm_pj]));
                            }
                            for (var _pm_dn = 0; _pm_dn < ds_list_size(_pm_dlist); _pm_dn++)
                            {
                                var _pm_other = string(ds_list_find_value(_pm_dlist, _pm_dn));
                                if (_pm_other != _pm_dir && string_pos(_pm_dest, _pm_other) != 1 && file_exists(_pm_other + "/" + _pm_dfile))
                                {
                                    if (md5_file(_pm_other + "/" + _pm_dfile) == _pm_hash)
                                    {
                                        var _pm_same = true;
                                        for (var _pm_pj = 0; _pm_pj < array_length(_pm_pn); _pm_pj++)
                                        {
                                            if (!file_exists(_pm_other + "/" + _pm_pn[_pm_pj]))
                                            {
                                                _pm_same = false;
                                            }
                                            else if (md5_file(_pm_other + "/" + _pm_pn[_pm_pj]) != _pm_ph[_pm_pj])
                                            {
                                                _pm_same = false;
                                            }
                                        }
                                        if (_pm_same)
                                        {
                                            _pm_dup = true;
                                        }
                                    }
                                }
                            }
                        }
                        if (_pm_dup)
                        {
                            _pm_dups++;
                            array_push(_pm_dupdirs, _pm_dir);
                        }
                        else
                        {
                            var _file = _pm_name;
                            var _pm_path = _pm_dir;
                            if (file_exists(_pm_dir + "/custom_data.futa"))
                            {
                                var _pm_before = ds_list_size(custom_futas_folder);
                                var _full_path = _pm_path;
                                check_struct = check_custom_futa(_full_path);
                                if (check_struct.custom_portrait != -1 && check_struct.custom_mating_press != -1 && check_struct.custom_cowgirls != -1 && check_struct.custom_xray != -1)
                                {
                                    custom_sprite_loaded = true;
                                    tutorial = false;
                                    show_debug_message("SUCCESS: Loaded " + _file);
                                    ds_list_add(custom_futas_folder, _full_path);
                                    ds_list_add(futa_selector_names, _file);
                                    var _has_deep = file_exists(_full_path + "/custom_deepthroat.png");
                                    var _has_alts = file_exists(_full_path + "/custom_futa_cowgirl_alt_1.png") || file_exists(_full_path + "/custom_futa_mating_press_alt_1.png");
                                    ds_list_add(futa_selector_has_deepthroat, _has_deep);
                                    ds_list_add(futa_selector_has_alts, _has_alts);
                                    var _preview_spr = func_futa_selector_portrait(_full_path);
                                    ds_list_add(futa_selector_portraits, _preview_spr);
                                }
                                if (ds_list_size(custom_futas_folder) > _pm_before)
                                {
                                    _pm_added++;
                                }
                            }
                            else
                            {
                                var _pm_before_w = ds_list_size(custom_wives_folder);
                                var _full_path = _pm_path;
                                var _is_legacy_spouse = file_exists(_full_path + "/custom_data.spouse");
                                if (_is_legacy_spouse)
                                {
                                    if (file_exists(_full_path + "/custom_mating_press.png") || file_exists(_full_path + "/custom_reverse_cowgirl.png"))
                                    {
                                        custom_wife_sprite_loaded = true;
                                        show_debug_message("loaded 1.4 legacy spouse: " + _file);
                                        ds_list_add(custom_wives_folder, _full_path);
                                        ds_list_add(wife_selector_names, _file);
                                        var _legacy_has_deep = file_exists(_full_path + "/custom_deepthroat.png");
                                        ds_list_add(wife_selector_has_cowgirl, _legacy_has_deep);
                                        var _w_spr = func_wife_selector_portrait(_full_path);
                                        ds_list_add(wife_selector_portraits, _w_spr);
                                    }
                                }
                                else
                                {
                                    check_struct = check_custom_wife(_full_path);
                                    if (check_struct.custom_wife_cowgirl != -1 && check_struct.custom_wife_reverse_cowgirl != -1 && check_struct.custom_wife_mating_press != -1)
                                    {
                                        custom_wife_has_portrait = check_struct.custom_wife_portrait;
                                        custom_wife_sprite_loaded = true;
                                        show_debug_message("loaded custom wife");
                                        ds_list_add(custom_wives_folder, _full_path);
                                        ds_list_add(wife_selector_names, _file);
                                        var _w_has_cowgirl = file_exists(_full_path + "/custom_wife_cowgirl_0.png");
                                        ds_list_add(wife_selector_has_cowgirl, _w_has_cowgirl);
                                        var _w_spr = func_wife_selector_portrait(_full_path);
                                        ds_list_add(wife_selector_portraits, _w_spr);
                                    }
                                }
                                if (ds_list_size(custom_wives_folder) > _pm_before_w)
                                {
                                    _pm_added++;
                                }
                            }
                        }
                    }
                    else if (_pm_depth < 4)
                    {
                        var _pm_find = tc_ff_first(_pm_dir + "/*", 16);
                        while (_pm_find != "")
                        {
                            if (_pm_find != "." && _pm_find != "..")
                            {
                                array_push(_pm_queue, _pm_dir + "/" + _pm_find);
                                array_push(_pm_names, _pm_find);
                                array_push(_pm_depths, _pm_depth + 1);
                            }
                            _pm_find = tc_ff_next();
                        }
                        tc_ff_close();
                    }
                }
                _pm_bg = 0;
                _pm_dlg = 0;
                _pm_tex = 0;
                _pm_voice = 0;
                var _pm_rchars = 0;
                var _pm_tsrc = [];
                var _pm_tdst = [];
                var _pm_rq = [_pm_dest];
                var _pm_rn = [_pm_base];
                var _pm_rdep = [0];
                var _pm_ri = 0;
                while (_pm_ri < array_length(_pm_rq))
                {
                    var _pm_rd = _pm_rq[_pm_ri];
                    var _pm_rname = _pm_rn[_pm_ri];
                    var _pm_rdepth = _pm_rdep[_pm_ri];
                    _pm_ri++;
                    if (file_exists(_pm_rd + "/custom_data.futa") || file_exists(_pm_rd + "/custom_data.wife") || file_exists(_pm_rd + "/custom_data.spouse"))
                    {
                        _pm_rchars++;
                    }
                    else if (file_exists(_pm_rd + "/custom_data.bedroom"))
                    {
                        var _pm_csrc = [_pm_rd];
                        var _pm_cdst = [_pm_save + "/custom_bedrooms/" + _pm_rname];
                        var _pm_ci = 0;
                        while (_pm_ci < array_length(_pm_csrc))
                        {
                            var _pm_cs = _pm_csrc[_pm_ci];
                            var _pm_cd = _pm_cdst[_pm_ci];
                            _pm_ci++;
                            if (!tc_dir_exists(_pm_cd))
                            {
                                directory_create(_pm_cd);
                            }
                            var _pm_cn = [];
                            var _pm_cf = tc_ff_first(_pm_cs + "/*", 16);
                            while (_pm_cf != "")
                            {
                                if (_pm_cf != "." && _pm_cf != "..")
                                {
                                    array_push(_pm_cn, _pm_cf);
                                }
                                _pm_cf = tc_ff_next();
                            }
                            tc_ff_close();
                            for (var _pm_cx = 0; _pm_cx < array_length(_pm_cn); _pm_cx++)
                            {
                                if (tc_dir_exists(_pm_cs + "/" + _pm_cn[_pm_cx]))
                                {
                                    array_push(_pm_csrc, _pm_cs + "/" + _pm_cn[_pm_cx]);
                                    array_push(_pm_cdst, _pm_cd + "/" + _pm_cn[_pm_cx]);
                                }
                                else
                                {
                                    file_copy(_pm_cs + "/" + _pm_cn[_pm_cx], _pm_cd + "/" + _pm_cn[_pm_cx]);
                                }
                            }
                        }
                        _pm_bg++;
                    }
                    else
                    {
                        var _pm_re = [];
                        var _pm_rf = tc_ff_first(_pm_rd + "/*", 16);
                        while (_pm_rf != "")
                        {
                            if (_pm_rf != "." && _pm_rf != "..")
                            {
                                array_push(_pm_re, _pm_rf);
                            }
                            _pm_rf = tc_ff_next();
                        }
                        tc_ff_close();
                        var _pm_png = 0;
                        var _pm_subs = [];
                        for (var _pm_x = 0; _pm_x < array_length(_pm_re); _pm_x++)
                        {
                            var _pm_en = _pm_re[_pm_x];
                            var _pm_el = string_lower(_pm_en);
                            if (tc_dir_exists(_pm_rd + "/" + _pm_en))
                            {
                                array_push(_pm_subs, _pm_en);
                            }
                            else if (string_copy(_pm_el, string_length(_pm_el) - 4, 5) == ".json")
                            {
                                if (!tc_dir_exists(_pm_save + "/dialogue_packs"))
                                {
                                    directory_create(_pm_save + "/dialogue_packs");
                                }
                                file_copy(_pm_rd + "/" + _pm_en, _pm_save + "/dialogue_packs/" + _pm_en);
                                _pm_dlg++;
                            }
                            else if (string_copy(_pm_el, string_length(_pm_el) - 3, 4) == ".png")
                            {
                                _pm_png++;
                            }
                        }
                        var _pm_isvoice = false;
                        for (var _pm_z = 0; _pm_z < array_length(_pm_subs); _pm_z++)
                        {
                            if (string_lower(_pm_subs[_pm_z]) == "moan_fast" || string_lower(_pm_subs[_pm_z]) == "moan_slow")
                            {
                                _pm_isvoice = true;
                            }
                        }
                        if (_pm_isvoice)
                        {
                            if (!tc_dir_exists(_pm_save + "/phone_voices"))
                            {
                                directory_create(_pm_save + "/phone_voices");
                            }
                            var _pm_csrc = [_pm_rd];
                            var _pm_cdst = [_pm_save + "/phone_voices/" + _pm_rname];
                            var _pm_ci = 0;
                            while (_pm_ci < array_length(_pm_csrc))
                            {
                                var _pm_cs = _pm_csrc[_pm_ci];
                                var _pm_cd = _pm_cdst[_pm_ci];
                                _pm_ci++;
                                if (!tc_dir_exists(_pm_cd))
                                {
                                    directory_create(_pm_cd);
                                }
                                var _pm_cn = [];
                                var _pm_cf = tc_ff_first(_pm_cs + "/*", 16);
                                while (_pm_cf != "")
                                {
                                    if (_pm_cf != "." && _pm_cf != "..")
                                    {
                                        array_push(_pm_cn, _pm_cf);
                                    }
                                    _pm_cf = tc_ff_next();
                                }
                                tc_ff_close();
                                for (var _pm_cx = 0; _pm_cx < array_length(_pm_cn); _pm_cx++)
                                {
                                    if (tc_dir_exists(_pm_cs + "/" + _pm_cn[_pm_cx]))
                                    {
                                        array_push(_pm_csrc, _pm_cs + "/" + _pm_cn[_pm_cx]);
                                        array_push(_pm_cdst, _pm_cd + "/" + _pm_cn[_pm_cx]);
                                    }
                                    else
                                    {
                                        file_copy(_pm_cs + "/" + _pm_cn[_pm_cx], _pm_cd + "/" + _pm_cn[_pm_cx]);
                                    }
                                }
                            }
                            _pm_voice++;
                        }
                        else if (_pm_png >= 3)
                        {
                            array_push(_pm_tsrc, _pm_rd);
                            array_push(_pm_tdst, _pm_save + "/texture_packs/" + _pm_rname);
                        }
                        else if (_pm_rdepth < 4)
                        {
                            for (var _pm_y = 0; _pm_y < array_length(_pm_subs); _pm_y++)
                            {
                                array_push(_pm_rq, _pm_rd + "/" + _pm_subs[_pm_y]);
                                array_push(_pm_rn, _pm_subs[_pm_y]);
                                array_push(_pm_rdep, _pm_rdepth + 1);
                            }
                        }
                    }
                }
                if (_pm_rchars == 0)
                {
                    for (var _pm_t = 0; _pm_t < array_length(_pm_tsrc); _pm_t++)
                    {
                        var _pm_csrc = [_pm_tsrc[_pm_t]];
                        var _pm_cdst = [_pm_tdst[_pm_t]];
                        var _pm_ci = 0;
                        while (_pm_ci < array_length(_pm_csrc))
                        {
                            var _pm_cs = _pm_csrc[_pm_ci];
                            var _pm_cd = _pm_cdst[_pm_ci];
                            _pm_ci++;
                            if (!tc_dir_exists(_pm_cd))
                            {
                                directory_create(_pm_cd);
                            }
                            var _pm_cn = [];
                            var _pm_cf = tc_ff_first(_pm_cs + "/*", 16);
                            while (_pm_cf != "")
                            {
                                if (_pm_cf != "." && _pm_cf != "..")
                                {
                                    array_push(_pm_cn, _pm_cf);
                                }
                                _pm_cf = tc_ff_next();
                            }
                            tc_ff_close();
                            for (var _pm_cx = 0; _pm_cx < array_length(_pm_cn); _pm_cx++)
                            {
                                if (tc_dir_exists(_pm_cs + "/" + _pm_cn[_pm_cx]))
                                {
                                    array_push(_pm_csrc, _pm_cs + "/" + _pm_cn[_pm_cx]);
                                    array_push(_pm_cdst, _pm_cd + "/" + _pm_cn[_pm_cx]);
                                }
                                else
                                {
                                    file_copy(_pm_cs + "/" + _pm_cn[_pm_cx], _pm_cd + "/" + _pm_cn[_pm_cx]);
                                }
                            }
                        }
                        _pm_tex++;
                    }
                }
                if (_pm_added > 0)
                {
                    for (var _pm_dd = 0; _pm_dd < array_length(_pm_dupdirs); _pm_dd++)
                    {
                        var _pm_xq = [_pm_dupdirs[_pm_dd]];
                        var _pm_xi = 0;
                        while (_pm_xi < array_length(_pm_xq))
                        {
                            var _pm_xd = _pm_xq[_pm_xi];
                            _pm_xi++;
                            var _pm_xn = [];
                            var _pm_xf = tc_ff_first(_pm_xd + "/*", 16);
                            while (_pm_xf != "")
                            {
                                if (_pm_xf != "." && _pm_xf != "..")
                                {
                                    array_push(_pm_xn, _pm_xf);
                                }
                                _pm_xf = tc_ff_next();
                            }
                            tc_ff_close();
                            for (var _pm_xk = 0; _pm_xk < array_length(_pm_xn); _pm_xk++)
                            {
                                if (tc_dir_exists(_pm_xd + "/" + _pm_xn[_pm_xk]))
                                {
                                    array_push(_pm_xq, _pm_xd + "/" + _pm_xn[_pm_xk]);
                                }
                                else
                                {
                                    file_delete(_pm_xd + "/" + _pm_xn[_pm_xk]);
                                }
                            }
                        }
                        var _pm_xr = array_length(_pm_xq) - 1;
                        while (_pm_xr >= 0)
                        {
                            directory_destroy(_pm_xq[_pm_xr]);
                            if (tc_dir_exists(_pm_xq[_pm_xr]))
                            {
                                file_delete(_pm_xq[_pm_xr]);
                            }
                            _pm_xr--;
                        }
                    }
                }
                else
                {
                    var _pm_xq = [_pm_dest];
                    var _pm_xi = 0;
                    while (_pm_xi < array_length(_pm_xq))
                    {
                        var _pm_xd = _pm_xq[_pm_xi];
                        _pm_xi++;
                        var _pm_xn = [];
                        var _pm_xf = tc_ff_first(_pm_xd + "/*", 16);
                        while (_pm_xf != "")
                        {
                            if (_pm_xf != "." && _pm_xf != "..")
                            {
                                array_push(_pm_xn, _pm_xf);
                            }
                            _pm_xf = tc_ff_next();
                        }
                        tc_ff_close();
                        for (var _pm_xk = 0; _pm_xk < array_length(_pm_xn); _pm_xk++)
                        {
                            if (tc_dir_exists(_pm_xd + "/" + _pm_xn[_pm_xk]))
                            {
                                array_push(_pm_xq, _pm_xd + "/" + _pm_xn[_pm_xk]);
                            }
                            else
                            {
                                file_delete(_pm_xd + "/" + _pm_xn[_pm_xk]);
                            }
                        }
                    }
                    var _pm_xr = array_length(_pm_xq) - 1;
                    while (_pm_xr >= 0)
                    {
                        directory_destroy(_pm_xq[_pm_xr]);
                        if (tc_dir_exists(_pm_xq[_pm_xr]))
                        {
                            file_delete(_pm_xq[_pm_xr]);
                        }
                        _pm_xr--;
                    }
                }
                var _pm_what = "";
                if (_pm_added > 0)
                {
                    _pm_what += (string(_pm_added) + " character(s) ");
                }
                if (_pm_bg > 0)
                {
                    _pm_what += (string(_pm_bg) + " background(s) ");
                }
                if (_pm_dlg > 0)
                {
                    _pm_what += (string(_pm_dlg) + " dialogue file(s) ");
                }
                if (_pm_tex > 0)
                {
                    _pm_what += (string(_pm_tex) + " texture pack(s) ");
                }
                if (_pm_voice > 0)
                {
                    _pm_what += (string(_pm_voice) + " voice pack(s) ");
                }
                if (_pm_what == "")
                {
                    if (_pm_dups > 0)
                    {
                        pm_status = "Already installed - nothing new was added.";
                    }
                    else
                    {
                        pm_status = "Nothing the game can use was found in that file.";
                    }
                }
                else
                {
                    pm_status = "Added " + _pm_what;
                    if (_pm_dups > 0)
                    {
                        pm_status += ("- skipped " + string(_pm_dups) + " already installed ");
                    }
                    if ((_pm_bg + _pm_dlg + _pm_tex) > 0)
                    {
                        pm_status += "- restart the game to use backgrounds, dialogue and textures.";
                    }
                    if (_pm_voice > 0)
                    {
                        pm_status += "- tap VOICES to give a voice to a lover.";
                    }
                }
            }
        }
        else
        {
            pm_status = "Download failed (" + string(_pm_code) + "). Check the link.";
        }
        if (file_exists(_pm_zip))
        {
            file_delete(_pm_zip);
        }
    }
}
