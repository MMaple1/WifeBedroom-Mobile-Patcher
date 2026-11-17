
if (variable_instance_exists(id, "buttplug_socket") && buttplug_socket >= 0)
{
    var _bp_now = current_time;
    if (_bp_now - buttplug_last_send >= 33)
    {
        buttplug_last_send = _bp_now;
        buffer_seek(buttplug_buffer, buffer_seek_start, 0);
        buffer_write(buttplug_buffer, buffer_string, string(thrust) + "," + string(thrust_prev) + "," + string(thrust_speed) + "," + string(thrust_strength) + "," + string(insert) + "," + string(orgasm));
        network_send_udp_raw(buttplug_socket, "127.0.0.1", buttplug_port, buttplug_buffer, buffer_tell(buttplug_buffer));
    }
}
