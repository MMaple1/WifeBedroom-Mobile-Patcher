    comment = "layer 6: side bangs";
    if (sprite_exists(bangs_sprite) && bangs_sprite != -1)
    {
        draw_sprite_ext(bangs_sprite, 6, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);
    }