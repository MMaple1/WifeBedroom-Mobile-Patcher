function tc_ff_next()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type == os_android || os_type == os_ios)
        {
            return "";
        }
        return file_find_next();
    }
    if (tc_ff_pos >= array_length(tc_ff_items))
    {
        return "";
    }
    tc_ff_pos++;
    return tc_ff_items[tc_ff_pos - 1];
}

function tc_ff_close()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type != os_android && os_type != os_ios)
        {
            file_find_close();
        }
    }
    tc_ff_items = -1;
    tc_ff_pos = 0;
}