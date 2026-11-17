if (tb_enabled)
{
    var _tb_now = current_time;
    if (title == true && mouse_check_button_pressed(mb_left) && point_in_rectangle(mouse_x, mouse_y, room_width - 124, 0, room_width, 44))
    {
        tb_profile = (tb_profile + 1) % array_length(tb_profile_names);
        ini_open(game_save_id + "toy_direct.ini");
        ini_write_real("toy", "profile", tb_profile);
        ini_close();
        mouse_clear(mb_left);
    }
    if (tb_state == 0 && _tb_now >= tb_retry_at)
    {
        if (tb_sock >= 0)
        {
            network_destroy(tb_sock);
        }
        tb_running = false;
        tb_ws_open = false;
        tb_rx_len = 0;
        tb_sock = network_create_socket(network_socket_tcp);
        network_connect_raw_async(tb_sock, "127.0.0.1", tb_port);
        tb_state = 1;
        tb_retry_at = _tb_now + 6000;
    }
    else if ((tb_state == 1 || tb_state == 2) && _tb_now >= tb_retry_at)
    {
        tb_state = 0;
    }
    if (tb_state == 3)
    {
        if ((_tb_now - tb_last_rx) >= 12000)
        {
            tb_state = 0;
            tb_retry_at = _tb_now;
        }
        var _tb_wall = date_current_datetime() * 86400000;
        var _tb_frozen = tb_frame_at > 0 && (_tb_wall - tb_frame_at) >= 1500;
        tb_frame_at = _tb_wall;
        if (_tb_frozen && tb_running)
        {
            tb_running = false;
            tb_sent = -1;
            tb_smooth = 0;
            tb_have_last = false;
            var _tb_p = "[{\"StopAllDevices\":{\"Id\":" + string(tb_msg_id++) + "}}]";
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
        if ((_tb_now - tb_last_ping) >= tb_ping_every)
        {
            tb_last_ping = _tb_now;
            var _tb_p = "[{\"Ping\":{\"Id\":" + string(tb_msg_id++) + "}}]";
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
        var _tb_scene = (_tb_now - tb_scene_at) < 500;
        if (!_tb_scene || !insert || title == true || os_is_paused())
        {
            tb_have_last = false;
            tb_pos_at = 0;
            tb_smooth = 0;
            if (tb_running)
            {
                tb_running = false;
                tb_sent = -1;
                var _tb_p = "[{\"StopAllDevices\":{\"Id\":" + string(tb_msg_id++) + "}}]";
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
        }
        else
        {
            if ((_tb_now - tb_sample_at) >= 33)
            {
                tb_sample_at = _tb_now;
                var _tb_delta = 0;
                if (tb_have_last)
                {
                    _tb_delta = abs(thrust - tb_last_thrust);
                }
                tb_last_thrust = thrust;
                tb_have_last = true;
                var _tb_target = clamp(_tb_delta * 7, 0, 1);
                if (orgasm)
                {
                    tb_pulse += 0.6283;
                    _tb_target = max(_tb_target, 0.45 + (0.25 * (0.5 + (0.5 * sin(tb_pulse)))));
                }
                else
                {
                    tb_pulse = 0;
                }
                tb_smooth += ((clamp(_tb_target, 0, 1) - tb_smooth) * 0.35);
            }
            var _tb_lo = tb_profile_min[tb_profile];
            var _tb_hi = tb_profile_max[tb_profile];
            var _tb_want = _tb_lo + (clamp(tb_smooth, 0, 1) * (_tb_hi - _tb_lo));
            if ((_tb_now - tb_send_at) >= 66)
            {
                tb_send_at = _tb_now;
                var _tb_changed = !tb_running || abs(_tb_want - tb_sent) >= 0.01;
                var _tb_dur = round(clamp(((360 / max(thrust_speed, 0.5)) * 16.666666666666668) / 2, 100, 1800));
                var _tb_pos_src = clamp(thrust, 0, 1);
                if (tb_lead > 0)
                {
                    var _tb_dt = _tb_now - tb_pos_at;
                    if (tb_pos_at > 0 && _tb_dt > 0 && _tb_dt < 400)
                    {
                        var _tb_ext = min(tb_lead, _tb_dur * 0.5);
                        _tb_pos_src = clamp(_tb_pos_src + (((_tb_pos_src - tb_pos_prev) / _tb_dt) * _tb_ext), 0, 1);
                    }
                }
                tb_pos_prev = clamp(thrust, 0, 1);
                tb_pos_at = _tb_now;
                var _tb_pos = _tb_lo + (_tb_pos_src * (_tb_hi - _tb_lo));
                var _tb_json = "";
                for (var _tb_i = 0; _tb_i < array_length(tb_dev_idx); _tb_i++)
                {
                    var _tb_types = tb_dev_scalars[_tb_i];
                    var _tb_part = "";
                    if (_tb_changed)
                    {
                        for (var _tb_k = 0; _tb_k < array_length(_tb_types); _tb_k++)
                        {
                            if (_tb_types[_tb_k] == "Vibrate" || _tb_types[_tb_k] == "Oscillate")
                            {
                                if (_tb_part != "")
                                {
                                    _tb_part += ",";
                                }
                                _tb_part += ("{\"Index\":" + string(_tb_k) + ",\"Scalar\":" + string(_tb_want) + ",\"ActuatorType\":\"" + _tb_types[_tb_k] + "\"}");
                            }
                        }
                    }
                    if (_tb_part != "")
                    {
                        if (_tb_json != "")
                        {
                            _tb_json += ",";
                        }
                        _tb_json += ("{\"ScalarCmd\":{\"Id\":" + string(tb_msg_id++) + ",\"DeviceIndex\":" + string(tb_dev_idx[_tb_i]) + ",\"Scalars\":[" + _tb_part + "]}}");
                    }
                    if (tb_dev_linears[_tb_i] > 0)
                    {
                        var _tb_vec = "";
                        for (var _tb_v = 0; _tb_v < tb_dev_linears[_tb_i]; _tb_v++)
                        {
                            if (_tb_vec != "")
                            {
                                _tb_vec += ",";
                            }
                            _tb_vec += ("{\"Index\":" + string(_tb_v) + ",\"Duration\":" + string(_tb_dur) + ",\"Position\":" + string(_tb_pos) + "}");
                        }
                        if (_tb_json != "")
                        {
                            _tb_json += ",";
                        }
                        _tb_json += ("{\"LinearCmd\":{\"Id\":" + string(tb_msg_id++) + ",\"DeviceIndex\":" + string(tb_dev_idx[_tb_i]) + ",\"Vectors\":[" + _tb_vec + "]}}");
                    }
                }
                if (_tb_json != "")
                {
                    tb_running = true;
                    tb_sent = _tb_want;
                    var _tb_p = "[" + _tb_json + "]";
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
            }
        }
    }
}
