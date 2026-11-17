var _hmv_mx = mouse_x;
var _hmv_my = mouse_y;
hmv_speaker_l_hover = _hmv_mx >= hmv_speaker_l_x && _hmv_mx <= (hmv_speaker_l_x + hmv_speaker_size) && _hmv_my >= hmv_speaker_l_y && _hmv_my <= (hmv_speaker_l_y + hmv_speaker_size);
hmv_speaker_r_hover = _hmv_mx >= hmv_speaker_r_x && _hmv_mx <= (hmv_speaker_r_x + hmv_speaker_size) && _hmv_my >= hmv_speaker_r_y && _hmv_my <= (hmv_speaker_r_y + hmv_speaker_size);
if (hmv_speaker_pulse > 0)
{
    hmv_speaker_pulse -= 0.05;
    if (hmv_speaker_pulse < 0)
    {
        hmv_speaker_pulse = 0;
    }
}
if (mouse_check_button_pressed(mb_left) && (hmv_speaker_l_hover || hmv_speaker_r_hover))
{
    hmv_speaker_pulse = 1;
    buffer_seek(hmv_ping_buffer, buffer_seek_start, 0);
    buffer_write(hmv_ping_buffer, buffer_u8, 165);
    network_send_udp_raw(hmv_socket, "127.0.0.1", hmv_ping_port, hmv_ping_buffer, 1);
}
if (hmv_active)
{
    if ((current_time - hmv_last_packet_time) > 500)
    {
        hmv_active = false;
        hmv_background_color = 16777215;
    }
    else
    {
        thrust_speed = hmv_thrust_speed;
        thrust_strength = hmv_thrust_strength;
        thrust_middle = hmv_thrust_middle;
    }
}
