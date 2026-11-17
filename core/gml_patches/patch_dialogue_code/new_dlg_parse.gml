    try
    {
        var _data = json_parse(_json_string);
        dialogue_json = _data;
        return true;
    }
    catch (_err)
    {
        show_debug_message("Dialogue JSON parse error bypassed safely");
        return false;
    }