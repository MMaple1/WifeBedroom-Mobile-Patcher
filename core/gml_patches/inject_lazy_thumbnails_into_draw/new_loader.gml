                    else if (file_exists(_pb))
                    {
                        _spr = sprite_add(_pb, 10, false, false, (selector_mode == 0) ? 54 : 32, (selector_mode == 0) ? 82 : 48);
                        if (_spr <= 0 || !sprite_exists(_spr))
                        {
                            var _test_p = sprite_add(_pb, 1, false, false, 0, 0);
                            if (_test_p > 0 && sprite_exists(_test_p))
                            {
                                var _pw = sprite_get_width(_test_p);
                                var _ph = sprite_get_height(_test_p);
                                sprite_delete(_test_p);
                                var _p_frames = max(1, round(_pw / _ph));
                                _spr = sprite_add(_pb, _p_frames, false, false, (selector_mode == 0) ? 54 : 32, (selector_mode == 0) ? 82 : 48);
                            }
                        }
                    }