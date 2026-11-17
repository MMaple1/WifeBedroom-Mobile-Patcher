function tc_dir_exists(arg0)
{
    arg0 = tc_norm_path(arg0);
    if (string_char_at(arg0, string_length(arg0)) == "/")
    {
        arg0 = string_copy(arg0, 1, string_length(arg0) - 1);
    }
    return directory_exists(arg0) || file_exists(arg0 + "/_manifest.txt");
}