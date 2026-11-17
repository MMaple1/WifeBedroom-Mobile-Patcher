if (buttplug_socket >= 0)
{
    var _bp_now = current_time;
    if ((_bp_now - buttplug_last_send) >= 33)
    {
        buttplug_last_send = _bp_now;
        var _bp_insert = 0;
        if (insert)
        {
            _bp_insert = 1;
        }
        var _bp_orgasm = 0;
        if (orgasm)
        {
            _bp_orgasm = 1;
        }
        var _bp_msg = string(thrust) + "," + string(thrust_prev) + "," + string(thrust_speed) + "," + string(thrust_strength) + "," + string(_bp_insert) + "," + string(_bp_orgasm);
        buffer_seek(buttplug_buffer, buffer_seek_start, 0);
        buffer_write(buttplug_buffer, buffer_text, _bp_msg);
        network_send_udp_raw(buttplug_socket, "127.0.0.1", buttplug_port, buttplug_buffer, buffer_tell(buttplug_buffer));
    }
}
