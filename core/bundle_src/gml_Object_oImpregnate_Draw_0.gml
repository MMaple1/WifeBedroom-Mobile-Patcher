impregnation_scale += (((impregnation_timer > 0) - impregnation_scale) * 0.1);
if (impregnation_timer > 0)
{
    impregnation_timer -= 1;
}
draw_sprite_ext(sImpregnation, 0, (x - 64) + xDeviation, (y - 16) + yDeviation, impregnation_size, impregnation_size, 0, c_white, impregnation_scale);
if (egg_flag == false)
{
    draw_sprite_ext(sImpregnation, 1, (x - 64) + xDeviation, (y - 16) + yDeviation, impregnation_size + condom_jiggle, impregnation_size - condom_jiggle, 0, c_white, impregnation_scale);
}
else
{
    draw_sprite_ext(sImpregnation, 2, (x - 64) + xDeviation, (y - 16) + yDeviation, impregnation_size + condom_jiggle, impregnation_size - condom_jiggle, 0, c_white, impregnation_scale);
}
draw_set_halign(fa_center);
for (var i = 0; i < 12; i++)
{
    var sperm_squish = 0;
    if (sperm[i] < 1)
    {
        sperm_squish = condom_jiggle * 4;
    }
    var sperm_sprite = sImpregnationSperm;
    if (instance_exists(oFutaMatingPress))
    {
        if (oFutaMatingPress.top_sprite == sFutaMatingPressAndroid)
        {
            sperm_sprite = sImpregnationSpermAndroid;
        }
        else if (oFutaMatingPress.top_sprite == sFutaMatingPressAlien)
        {
            sperm_sprite = sImpregnationSpermAlien;
        }
        if (oFutaMatingPress.hyper_breeding_pill == true || oFutaMatingPress.mega_sperm_pill == true)
        {
            if (oFutaMatingPress.top_sprite == sFutaMatingPressAndroid)
            {
                sperm_sprite = sImpregnationSpermAndroidBig;
            }
            else if (oFutaMatingPress.top_sprite == sFutaMatingPressAlien)
            {
                sperm_sprite = sImpregnationSpermAlien;
            }
            else
            {
                sperm_sprite = sImpregnationSpermBig;
            }
        }
        if (oFutaMatingPress.hyper_breeding_pill == true || oFutaMatingPress.mega_sperm_pill == true)
        {
            if (variable_instance_exists(oFutaMatingPress, "custom_sperm_big_sprite") && sprite_exists(oFutaMatingPress.custom_sperm_big_sprite))
            {
                sperm_sprite = oFutaMatingPress.custom_sperm_big_sprite;
            }
        }
        else if (variable_instance_exists(oFutaMatingPress, "custom_sperm_sprite") && sprite_exists(oFutaMatingPress.custom_sperm_sprite))
        {
            sperm_sprite = oFutaMatingPress.custom_sperm_sprite;
        }
    }
    draw_sprite_ext(sperm_sprite, (current_time / 100) + i, (x - 64) + xDeviation + (dcos((30 * i) - 45) * (sperm[i] + sperm_squish)), (y + yDeviation) - 16 - (dsin((30 * i) - 45) * (sperm[i] + sperm_squish)), impregnation_size, impregnation_size, 30 * i, cum_color, impregnation_scale * (1 - (sperm[i] / 30)));
    if (sperm[i] > 0)
    {
        if (sperm[i] < 1)
        {
            if (sperm_speed[i] > 0)
            {
                condom_jiggle += 0.2;
                if (global.pop_sound_toggle)
                {
                    oAudioManager.play_sfx(sndPop, 0, random_range(0.4, 0.6), 0.15);
                }
            }
            sperm_speed[i] = 0;
        }
        else
        {
            sperm[i] -= sperm_speed[i];
            sperm_speed[i] += 0.02;
        }
    }
    if (sperm_choice == i)
    {
        sperm[i] += (-8 - sperm[i]) * 0.1;
        egg_flag = true;
    }
}
if (impregnation_timer < 90 && impregnation_timer > 60 && sperm_choice == -1)
{
    sperm_choice = irandom(11);
    condom_jiggle += 0.2;
    if (instance_exists(oFutaMatingPress) && oFutaMatingPress.top_sprite == sFutaMatingPressClown)
    {
        oAudioManager.play_sfx(sndHonk1, 0, 1, 0.8);
    }
    else if (global.pop_sound_toggle)
    {
        oAudioManager.play_sfx(sndPop, 0, 0.8, 0.25);
    }
}
condom_jiggle_move += ((((0 - condom_jiggle) * 0.75) - condom_jiggle_move) * 0.05);
condom_jiggle += condom_jiggle_move;
if (impregnation_scale <= 0)
{
    instance_destroy();
}
