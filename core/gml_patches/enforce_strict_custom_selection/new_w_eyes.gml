    else if (!legacy_custom_wife_toggle)
    {
        var _w_iris = func_get_portrait_iris(wife_eye_sprite);
        if (_w_iris != -1 && sprite_exists(_w_iris))
            draw_sprite_ext(_w_iris, eye_id, eye_x, eye_y, 1, 1, 0, wife_eye_color, 1);
        if (wife_eye_sprite != -1 && sprite_exists(wife_eye_sprite))
            draw_sprite(wife_eye_sprite, eye_id, eye_x, eye_y);
    }