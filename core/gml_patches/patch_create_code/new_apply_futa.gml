function func_apply_custom_futa_stats()
{
    if (is_legacy_custom)
    {
        top_sprite = (sprite_exists(legacy_custom_mating_press) && legacy_custom_mating_press != -1) ? legacy_custom_mating_press : sFutaMatingPress;
        penis_sprite = top_sprite;
        hair_sprite = top_sprite;
        face_sprite = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
        bangs_sprite = face_sprite;
        condom_offset_mpress = custom_condom_offset_mpress;
        condom_offset_cowgirls = custom_condom_offset_cowgirls;
    }
    else
    {
        top_sprite = (sprite_exists(custom_mating_press) && custom_mating_press != -1) ? custom_mating_press : sFutaMatingPress;
        penis_sprite = top_sprite;
        hair_sprite = top_sprite;
        face_sprite = (sprite_exists(custom_portrait) && custom_portrait != -1) ? custom_portrait : sFutaPortrait1;
        bangs_sprite = face_sprite;
        condom_offset_mpress = custom_condom_offset_mpress;
        condom_offset_cowgirls = custom_condom_offset_cowgirls;
    }