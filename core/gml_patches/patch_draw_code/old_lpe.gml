    face_x += ((face_x_set - face_x) * 0.1);
    face_y += ((face_y_set - face_y) * 0.1);
    comment = "layer 0: hair (back)";
    draw_sprite_ext(func_get_portrait(hair_sprite, 0), 0, portrait_x - face_x, (portrait_y - face_y) + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_hair, 1);
    comment = "layer 1: torso";
    draw_sprite_ext(func_get_portrait(top_sprite, 0), 1, portrait_x, portrait_y + (top_breath * 64), 1 * custom_portrait_scale, 1 * custom_portrait_scale, 0, top_skin, 1);