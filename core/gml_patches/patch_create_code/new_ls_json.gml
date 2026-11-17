    file_text_close(_ls_file);
    try
    {
        livestream_dialogue = json_parse(_ls_json_string);
    }
    catch (_err)
    {
        show_debug_message("Livestream JSON parse error bypassed safely");
    }