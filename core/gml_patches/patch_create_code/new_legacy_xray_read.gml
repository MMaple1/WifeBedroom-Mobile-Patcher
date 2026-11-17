        var _def_xo = ini_read_real("sprite", "xray_x", ini_read_real("xray", "origin_x", 80));
        var _def_yo = ini_read_real("sprite", "xray_y", ini_read_real("xray", "origin_y", 84));
        if (_def_xo > 120 || _def_xo < 40) _def_xo = 80;
        if (_def_yo > 120 || _def_yo < 40) _def_yo = 84;
        xray_origin_x = _def_xo;
        xray_origin_y = _def_yo;