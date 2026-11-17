
function tc_safe_sprite_ext(_spr, _sub, _x, _y, _xs, _ys, _rot, _col, _alpha)
{
    if (_spr != -1 && sprite_exists(_spr))
    {
        draw_sprite_ext(_spr, _sub, _x, _y, _xs, _ys, _rot, _col, _alpha);
    }
}

function tc_safe_sprite_part_ext(_spr, _sub, _left, _top, _w, _h, _x, _y, _xs, _ys, _col, _alpha)
{
    if (_spr != -1 && sprite_exists(_spr))
    {
        draw_sprite_part_ext(_spr, _sub, _left, _top, _w, _h, _x, _y, _xs, _ys, _col, _alpha);
    }
}
