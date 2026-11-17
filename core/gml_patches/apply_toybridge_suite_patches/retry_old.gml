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