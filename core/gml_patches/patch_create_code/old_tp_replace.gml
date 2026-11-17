function func_texture_pack_replace(arg0)
{
    for (var i = 0; i < array_length(sprite_list); i++)
    {
        var _filename = "texture_packs/" + arg0 + "/" + sprite_get_name(sprite_list[i]) + ".png";
        if (file_exists(_filename))
        {
            sprite_replace(sprite_list[i], _filename, global.sprite_backup[i].frames, false, false, global.sprite_backup[i].xorig, global.sprite_backup[i].yorig);
        }
    }
}