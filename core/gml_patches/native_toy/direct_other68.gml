if (ds_map_find_value(async_load, "id") == tb_sock)
{
    var _tb_type = ds_map_find_value(async_load, "type");
    if (_tb_type == 4)
    {
        if (ds_map_find_value(async_load, "succeeded"))
        {
            tb_state = 2;
            tb_retry_at = current_time + 6000;
            tb_last_rx = current_time;
            buffer_seek(tb_buf, buffer_seek_start, 0);
            buffer_write(tb_buf, buffer_text, "GET / HTTP/1.1\r\nHost: 127.0.0.1:" + string(tb_port) + "\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: V2lmZXNCZWRyb29tVG95IQ==\r\nSec-WebSocket-Version: 13\r\n\r\n");
            network_send_raw(tb_sock, tb_buf, buffer_tell(tb_buf));
        }
        else
        {
            tb_state = 0;
        }
    }
    else if (_tb_type == 2)
    {
        tb_state = 0;
        tb_retry_at = current_time + 3000;
    }
    else if (_tb_type == 3)
    {
        tb_last_rx = current_time;
        var _tb_size = ds_map_find_value(async_load, "size");
        buffer_copy(ds_map_find_value(async_load, "buffer"), 0, _tb_size, tb_rx, tb_rx_len);
        tb_rx_len += _tb_size;
        var _tb_go = true;
        while (_tb_go)
        {
            _tb_go = false;
            var _tb_text = "";
            var _tb_used = 0;
            if (!tb_ws_open)
            {
                for (var _tb_h = 0; (_tb_h + 3) < tb_rx_len; _tb_h++)
                {
                    if (buffer_peek(tb_rx, _tb_h, buffer_u8) == 13 && buffer_peek(tb_rx, _tb_h + 1, buffer_u8) == 10 && buffer_peek(tb_rx, _tb_h + 2, buffer_u8) == 13 && buffer_peek(tb_rx, _tb_h + 3, buffer_u8) == 10)
                    {
                        _tb_used = _tb_h + 4;
                        break;
                    }
                }
                if (_tb_used > 0)
                {
                    if (buffer_peek(tb_rx, 9, buffer_u8) == 49 && buffer_peek(tb_rx, 10, buffer_u8) == 48 && buffer_peek(tb_rx, 11, buffer_u8) == 49)
                    {
                        tb_ws_open = true;
                        var _tb_p = "[{\"RequestServerInfo\":{\"Id\":1,\"ClientName\":\"Wifes Bedroom\",\"MessageVersion\":3}}]";
                        var _tb_n = string_byte_length(_tb_p);
                        buffer_seek(tb_buf, buffer_seek_start, 0);
                        buffer_write(tb_buf, buffer_u8, 129);
                        if (_tb_n < 126)
                        {
                            buffer_write(tb_buf, buffer_u8, 128 + _tb_n);
                        }
                        else
                        {
                            buffer_write(tb_buf, buffer_u8, 254);
                            buffer_write(tb_buf, buffer_u8, (_tb_n >> 8) & 255);
                            buffer_write(tb_buf, buffer_u8, _tb_n & 255);
                        }
                        buffer_write(tb_buf, buffer_u32, 0);
                        buffer_write(tb_buf, buffer_text, _tb_p);
                        if (network_send_raw(tb_sock, tb_buf, buffer_tell(tb_buf)) < 0)
                        {
                            tb_state = 0;
                        }
                    }
                    else
                    {
                        tb_state = 0;
                    }
                }
            }
            else if (tb_rx_len >= 2)
            {
                var _tb_b0 = buffer_peek(tb_rx, 0, buffer_u8);
                var _tb_len = buffer_peek(tb_rx, 1, buffer_u8) & 127;
                var _tb_hdr = 2;
                var _tb_ok = true;
                if (_tb_len == 126)
                {
                    _tb_hdr = 4;
                    _tb_ok = tb_rx_len >= 4;
                    if (_tb_ok)
                    {
                        _tb_len = (buffer_peek(tb_rx, 2, buffer_u8) << 8) | buffer_peek(tb_rx, 3, buffer_u8);
                    }
                }
                else if (_tb_len == 127)
                {
                    _tb_hdr = 10;
                    _tb_ok = tb_rx_len >= 10;
                    if (_tb_ok)
                    {
                        _tb_len = (buffer_peek(tb_rx, 6, buffer_u8) << 24) | (buffer_peek(tb_rx, 7, buffer_u8) << 16) | (buffer_peek(tb_rx, 8, buffer_u8) << 8) | buffer_peek(tb_rx, 9, buffer_u8);
                    }
                }
                if (_tb_ok && tb_rx_len >= (_tb_hdr + _tb_len))
                {
                    _tb_used = _tb_hdr + _tb_len;
                    var _tb_op = _tb_b0 & 15;
                    if (_tb_op == 1 && _tb_len > 0)
                    {
                        var _tb_copy = buffer_create(_tb_len + 1, buffer_fixed, 1);
                        buffer_copy(tb_rx, _tb_hdr, _tb_len, _tb_copy, 0);
                        buffer_poke(_tb_copy, _tb_len, buffer_u8, 0);
                        buffer_seek(_tb_copy, buffer_seek_start, 0);
                        _tb_text = buffer_read(_tb_copy, buffer_string);
                        buffer_delete(_tb_copy);
                    }
                    else if (_tb_op == 9 && _tb_len < 126)
                    {
                        buffer_seek(tb_buf, buffer_seek_start, 0);
                        buffer_write(tb_buf, buffer_u8, 138);
                        buffer_write(tb_buf, buffer_u8, 128 + _tb_len);
                        buffer_write(tb_buf, buffer_u32, 0);
                        for (var _tb_q = 0; _tb_q < _tb_len; _tb_q++)
                        {
                            buffer_write(tb_buf, buffer_u8, buffer_peek(tb_rx, _tb_hdr + _tb_q, buffer_u8));
                        }
                        network_send_raw(tb_sock, tb_buf, buffer_tell(tb_buf));
                    }
                    else if (_tb_op == 8)
                    {
                        tb_state = 0;
                        tb_retry_at = current_time + 3000;
                    }
                }
            }
            if (_tb_used > 0)
            {
                var _tb_rest = tb_rx_len - _tb_used;
                if (_tb_rest > 0)
                {
                    var _tb_tmp = buffer_create(_tb_rest, buffer_fixed, 1);
                    buffer_copy(tb_rx, _tb_used, _tb_rest, _tb_tmp, 0);
                    buffer_copy(_tb_tmp, 0, _tb_rest, tb_rx, 0);
                    buffer_delete(_tb_tmp);
                }
                tb_rx_len = _tb_rest;
                _tb_go = tb_rx_len > 0 && tb_state != 0;
            }
            if (_tb_text != "")
            {
                var _tb_msgs = -1;
                if (string_char_at(_tb_text, 1) == "[")
                {
                    _tb_msgs = json_parse(_tb_text);
                }
                if (is_array(_tb_msgs))
                {
                    for (var _tb_m = 0; _tb_m < array_length(_tb_msgs); _tb_m++)
                    {
                        var _tb_msg = _tb_msgs[_tb_m];
                        if (!is_struct(_tb_msg))
                        {
                            continue;
                        }
                        if (variable_struct_exists(_tb_msg, "ServerInfo"))
                        {
                            tb_last_ping = current_time;
                            var _tb_mp = variable_struct_get(variable_struct_get(_tb_msg, "ServerInfo"), "MaxPingTime");
                            tb_ping_ms = is_real(_tb_mp) ? _tb_mp : 0;
                            tb_ping_every = 4000;
                            if (tb_ping_ms > 0)
                            {
                                tb_ping_every = clamp(tb_ping_ms / 2, 100, 4000);
                            }
                            tb_dev_idx = [];
                            tb_dev_name = [];
                            tb_dev_scalars = [];
                            tb_dev_linears = [];
                            tb_running = false;
                            tb_state = 3;
                            var _tb_p = "[{\"RequestDeviceList\":{\"Id\":2}},{\"StartScanning\":{\"Id\":3}}]";
                            var _tb_n = string_byte_length(_tb_p);
                            buffer_seek(tb_buf, buffer_seek_start, 0);
                            buffer_write(tb_buf, buffer_u8, 129);
                            if (_tb_n < 126)
                            {
                                buffer_write(tb_buf, buffer_u8, 128 + _tb_n);
                            }
                            else
                            {
                                buffer_write(tb_buf, buffer_u8, 254);
                                buffer_write(tb_buf, buffer_u8, (_tb_n >> 8) & 255);
                                buffer_write(tb_buf, buffer_u8, _tb_n & 255);
                            }
                            buffer_write(tb_buf, buffer_u32, 0);
                            buffer_write(tb_buf, buffer_text, _tb_p);
                            if (network_send_raw(tb_sock, tb_buf, buffer_tell(tb_buf)) < 0)
                            {
                                tb_state = 0;
                            }
                        }
                        else if (variable_struct_exists(_tb_msg, "DeviceList"))
                        {
                            var _tb_list = variable_struct_get(variable_struct_get(_tb_msg, "DeviceList"), "Devices");
                            if (is_array(_tb_list))
                            {
                                for (var _tb_d = 0; _tb_d < array_length(_tb_list); _tb_d++)
                                {
                                    var _tb_dev = _tb_list[_tb_d];
                                    var _tb_di = variable_struct_get(_tb_dev, "DeviceIndex");
                                    var _tb_r = array_length(tb_dev_idx) - 1;
                                    while (_tb_r >= 0)
                                    {
                                        if (tb_dev_idx[_tb_r] == _tb_di)
                                        {
                                            array_delete(tb_dev_idx, _tb_r, 1);
                                            array_delete(tb_dev_name, _tb_r, 1);
                                            array_delete(tb_dev_scalars, _tb_r, 1);
                                            array_delete(tb_dev_linears, _tb_r, 1);
                                        }
                                        _tb_r--;
                                    }
                                    var _tb_sc = [];
                                    var _tb_ln = 0;
                                    var _tb_dm = variable_struct_get(_tb_dev, "DeviceMessages");
                                    if (is_struct(_tb_dm))
                                    {
                                        var _tb_s = variable_struct_get(_tb_dm, "ScalarCmd");
                                        if (is_array(_tb_s))
                                        {
                                            for (var _tb_k = 0; _tb_k < array_length(_tb_s); _tb_k++)
                                            {
                                                array_push(_tb_sc, string(variable_struct_get(_tb_s[_tb_k], "ActuatorType")));
                                            }
                                        }
                                        var _tb_l = variable_struct_get(_tb_dm, "LinearCmd");
                                        if (is_array(_tb_l))
                                        {
                                            _tb_ln = array_length(_tb_l);
                                        }
                                    }
                                    array_push(tb_dev_idx, _tb_di);
                                    array_push(tb_dev_name, string(variable_struct_get(_tb_dev, "DeviceName")));
                                    array_push(tb_dev_scalars, _tb_sc);
                                    array_push(tb_dev_linears, _tb_ln);
                                }
                            }
                        }
                        else if (variable_struct_exists(_tb_msg, "DeviceAdded"))
                        {
                            var _tb_new = variable_struct_get(_tb_msg, "DeviceAdded");
                            var _tb_di = variable_struct_get(_tb_new, "DeviceIndex");
                            var _tb_r = array_length(tb_dev_idx) - 1;
                            while (_tb_r >= 0)
                            {
                                if (tb_dev_idx[_tb_r] == _tb_di)
                                {
                                    array_delete(tb_dev_idx, _tb_r, 1);
                                    array_delete(tb_dev_name, _tb_r, 1);
                                    array_delete(tb_dev_scalars, _tb_r, 1);
                                    array_delete(tb_dev_linears, _tb_r, 1);
                                }
                                _tb_r--;
                            }
                            var _tb_sc = [];
                            var _tb_ln = 0;
                            var _tb_dm = variable_struct_get(_tb_new, "DeviceMessages");
                            if (is_struct(_tb_dm))
                            {
                                var _tb_s = variable_struct_get(_tb_dm, "ScalarCmd");
                                if (is_array(_tb_s))
                                {
                                    for (var _tb_k = 0; _tb_k < array_length(_tb_s); _tb_k++)
                                    {
                                        array_push(_tb_sc, string(variable_struct_get(_tb_s[_tb_k], "ActuatorType")));
                                    }
                                }
                                var _tb_l = variable_struct_get(_tb_dm, "LinearCmd");
                                if (is_array(_tb_l))
                                {
                                    _tb_ln = array_length(_tb_l);
                                }
                            }
                            array_push(tb_dev_idx, _tb_di);
                            array_push(tb_dev_name, string(variable_struct_get(_tb_new, "DeviceName")));
                            array_push(tb_dev_scalars, _tb_sc);
                            array_push(tb_dev_linears, _tb_ln);
                        }
                        else if (variable_struct_exists(_tb_msg, "DeviceRemoved"))
                        {
                            var _tb_gone = variable_struct_get(variable_struct_get(_tb_msg, "DeviceRemoved"), "DeviceIndex");
                            var _tb_g = array_length(tb_dev_idx) - 1;
                            while (_tb_g >= 0)
                            {
                                if (tb_dev_idx[_tb_g] == _tb_gone)
                                {
                                    array_delete(tb_dev_idx, _tb_g, 1);
                                    array_delete(tb_dev_name, _tb_g, 1);
                                    array_delete(tb_dev_scalars, _tb_g, 1);
                                    array_delete(tb_dev_linears, _tb_g, 1);
                                }
                                _tb_g--;
                            }
                        }
                    }
                }
            }
        }
    }
}
