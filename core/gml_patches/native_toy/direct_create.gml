tb_enabled = os_type == os_android || os_type == os_ios;
var _tb_wd = working_directory;
if (string_char_at(_tb_wd, string_length(_tb_wd)) == "/")
{
    _tb_wd = string_copy(_tb_wd, 1, string_length(_tb_wd) - 1);
}
if (file_exists(_tb_wd + "/toy_direct.txt"))
{
    tb_enabled = true;
}
tb_sock = -1;
tb_state = 0;
tb_ws_open = false;
tb_retry_at = 0;
tb_msg_id = 10;
tb_last_ping = 0;
tb_ping_ms = 0;
tb_ping_every = 4000;
tb_frame_at = 0;
tb_last_rx = 0;
tb_dev_idx = [];
tb_dev_name = [];
tb_dev_scalars = [];
tb_dev_linears = [];
tb_buf = buffer_create(1024, buffer_grow, 1);
tb_rx = buffer_create(4096, buffer_grow, 1);
tb_rx_len = 0;
tb_scene_at = -100000;
tb_sample_at = 0;
tb_send_at = 0;
tb_last_thrust = 0;
tb_have_last = false;
tb_smooth = 0;
tb_sent = -1;
tb_running = false;
tb_pulse = 0;
tb_profile_names = ["DEFAULT 0-100", "EASY 0-30", "MID 30-60", "HARD 60-100", "MIDEASY 0-50", "MIDHARD 50-100"];
tb_profile_min = [0, 0, 0.3, 0.6, 0, 0.5];
tb_profile_max = [1, 0.3, 0.6, 1, 0.5, 1];
tb_profile = 0;
tb_port = 12345;
tb_lead = 0;
tb_pos_prev = 0;
tb_pos_at = 0;
if (tb_enabled)
{
    var _tb_pkg = working_directory + "toy_direct.ini";
    if (file_exists(_tb_pkg))
    {
        ini_open(_tb_pkg);
        tb_profile = clamp(floor(ini_read_real("toy", "profile", 0)), 0, 5);
        tb_port = floor(ini_read_real("toy", "port", 12345));
        tb_lead = clamp(floor(ini_read_real("toy", "lead", 0)), 0, 500);
        ini_close();
    }
    ini_open(game_save_id + "toy_direct.ini");
    tb_profile = clamp(floor(ini_read_real("toy", "profile", tb_profile)), 0, 5);
    tb_port = floor(ini_read_real("toy", "port", tb_port));
    tb_lead = clamp(floor(ini_read_real("toy", "lead", tb_lead)), 0, 500);
    ini_close();
}
