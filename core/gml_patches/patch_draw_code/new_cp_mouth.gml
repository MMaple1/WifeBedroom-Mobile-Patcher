if (top_sprite == custom_mating_press && sprite_exists(custom_portrait) && custom_portrait != -1)
    {
        draw_sprite_ext(custom_portrait, custom_mouth_id, portrait_x + face_x, portrait_y + (top_breath * 64) + face_y, 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);
    }