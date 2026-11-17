if (ds_map_find_value(async_load, "type") == 3 && ds_map_find_value(async_load, "id") == hmv_socket)
{
    var _buf = ds_map_find_value(async_load, "buffer");
    if (buffer_get_size(_buf) >= 16)
    {
        hmv_thrust_speed = buffer_read(_buf, buffer_f32);
        hmv_thrust_strength = buffer_read(_buf, buffer_f32);
        hmv_thrust_middle = buffer_read(_buf, buffer_f32);
        hmv_background_color = buffer_read(_buf, buffer_u32);
        hmv_active = true;
        hmv_last_packet_time = current_time;
    }
}
