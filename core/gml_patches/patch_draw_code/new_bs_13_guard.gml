    comment = "layer 13: fore bangs (mapped to vanilla index 9)";
    if (sprite_exists(bangs_sprite) && bangs_sprite != -1)
    {
        draw_sprite_ext(bangs_sprite, (top_sprite == custom_mating_press && top_sprite != legacy_custom_mating_press) ? 13 : 9, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);
    }