function func_texture_pack_backup_vanilla()
{
    global.sprite_backup = [];
    
    function backup_sprite(arg0)
    {
        array_push(global.sprite_backup, 
        {
            sprite: arg0,
            frames: sprite_get_number(arg0),
            xorig: sprite_get_xoffset(arg0),
            yorig: sprite_get_yoffset(arg0)
        });
    }
    
    for (var i = 0; i < array_length(sprite_list); i += 1)
    {
        backup_sprite(sprite_list[i]);
    }
}