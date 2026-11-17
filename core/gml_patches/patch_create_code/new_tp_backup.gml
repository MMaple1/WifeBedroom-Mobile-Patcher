function func_texture_pack_backup_vanilla()
{
    global.sprite_backup = [];
    for (var i = 0; i < array_length(sprite_list); i += 1)
    {
        var _spr_item = sprite_list[i];
        var _entry = {
            sprite: _spr_item,
            frames: sprite_get_number(_spr_item),
            xorig: sprite_get_xoffset(_spr_item),
            yorig: sprite_get_yoffset(_spr_item)
        };
        array_push(global.sprite_backup, _entry);
    }
}