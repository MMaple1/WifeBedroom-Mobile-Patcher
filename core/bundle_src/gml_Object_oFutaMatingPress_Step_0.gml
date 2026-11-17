// Master Modal Supremacy & Total Input Isolation Shield
if (variable_instance_exists(id, "futa_selector_open") && futa_selector_open)
{
    pill_menu_toggle = false;
    newlover_menu_toggle = false;
    newwife_menu_toggle = false;
    options_toggle = false;
    actions_menu_toggle = false;
    in_action_menu = false;
    radio_toggle = false;
    cs_toggle = false;
    position_menu_toggle = false;
    background_menu_toggle = false;
    radial_menu_open = false;
    radial_sub_menu = "";
    mob_expanded = false;
    penis_grab = false;
    kiss_box = false;
    headpat_press = false;
    futa_boob_press = false;
    wife_boob_press = false;
}
else if (variable_instance_exists(id, "mob_expanded") && mob_expanded)
{
    pill_menu_toggle = false;
    newlover_menu_toggle = false;
    newwife_menu_toggle = false;
    options_toggle = false;
    actions_menu_toggle = false;
    in_action_menu = false;
    radio_toggle = false;
    cs_toggle = false;
    position_menu_toggle = false;
    background_menu_toggle = false;
    radial_menu_open = false;
    radial_sub_menu = "";
    penis_grab = false;
    kiss_box = false;
    headpat_press = false;
    futa_boob_press = false;
    wife_boob_press = false;
}

global.rg_active = false;
global.rg_chosen_pill = "";
global.rg_locked = false;
if (ambience_pending && instance_exists(oBackground))
{
    ambience_pending = false;
    if (oBackground.bedroom_rain_enabled)
    {
        var _amb_inst = audio_play_sound(BedroomAmbienceRain, 0, true);
        audio_sound_gain(_amb_inst, global.vol_ambient * global.vol_master, 0);
    }
    else
    {
        var _amb_inst = audio_play_sound(BedroomAmbience, 0, true);
        audio_sound_gain(_amb_inst, global.vol_ambient * global.vol_master, 0);
    }
}
comment = "derive edge_boost from float edge_charge";
edge_boost = 1 + floor(edge_charge * (edge_boost_max - 1));
comment = "top and bottom breathing animation";
top_breath = (dcos(current_time / 10) * 0.02) + body_jiggle + top_body_jiggle;
bottom_breath = (dcos((current_time + 200) / 10) * 0.02) - body_jiggle;
comment = "cursor hand graphic variable for later";
cursor_id = 0;
comment = "insert and thrust starter";
if (radio_advance_cooldown > 0)
{
    radio_advance_cooldown -= 1;
}
if (radio_is_playing && !global.rg_locked && radio_advance_cooldown <= 0)
{
    if (!audio_exists(radio_instance) || !audio_is_playing(radio_instance))
    {
        radio_is_playing = false;
        radio_advance_cooldown = 10;
        if (radio_shuffle && ds_list_size(radio_track_list) > 1)
        {
            var _count = ds_list_size(radio_track_list);
            var _next = irandom(_count - 1);
            if (_next == radio_track_index)
            {
                _next = (_next + 1) % _count;
            }
            func_radio_play(_next);
        }
        else
        {
            func_radio_play(radio_track_index + 1);
        }
    }
}
if (insert == true && insert_prev == false)
{
    alarm[0] = 1;
    thrust_time = 0;
}
insert_prev = insert;
comment = "hovers";
if (title == false && start_timer < 1 && futa_selector_open == false)
{
    hover_portrait = point_in_rectangle(mouse_x, mouse_y, 10, room_height - 128, 87, room_height - 64);
    kiss_box = point_in_rectangle(mouse_x, mouse_y, (portrait_x - 6) + custom_kiss_x_offset, ((portrait_y + (top_breath * 64)) - 3) + custom_kiss_y_offset, portrait_x + 6 + custom_kiss_x_offset, portrait_y + (top_breath * 64) + 3 + custom_kiss_y_offset);
    boob_box = point_in_rectangle(mouse_x, mouse_y, 10 + custom_boob_x_offset, (room_height - 58) + custom_boob_y_offset, 87 + custom_boob_x_offset, (room_height - 25) + custom_boob_y_offset);
    headpat_press = point_in_rectangle(mouse_x, mouse_y, (portrait_x - 32) + custom_headpat_x_offset, (portrait_y - 56) + custom_headpat_y_offset, portrait_x + 32 + custom_headpat_x_offset, (portrait_y - 24) + custom_headpat_y_offset);
}
else if (futa_selector_open == true)
{
    hover_portrait = false;
    kiss_box = false;
    boob_box = false;
    headpat_press = false;
}
comment = "change portrait";
if (title == false && start_timer < 1 && futa_selector_open == false)
{
    if ((!custom_wife_has_portrait && bottom_sprite == custom_wife_mating_press) || bottom_sprite == sHusbandMatingPress)
    {
        portrait_number = 0;
    }
    if (hover_portrait)
    {
        if (!custom_wife_has_portrait && bottom_sprite == custom_wife_mating_press)
        {
            exit;
        }
        if (bottom_sprite == sHusbandMatingPress)
        {
            exit;
        }
        if (headpat_press == true)
        {
            cursor_id = 13;
        }
        else if (kiss_box == false)
        {
            cursor_id = 9;
        }
        if ((mouse_check_button_pressed(mb_right) || touch_long_press_synthetic) && cursor_id == 9 && manual_mode == 0)
        {
            if ((custom_wife_has_portrait && bottom_sprite == custom_wife_mating_press) || (bottom_sprite != custom_wife_mating_press && bottom_sprite != sHusbandMatingPress))
            {
                portrait_number = (portrait_number == 0) ? 1 : 0;
                if (portrait_number == 0)
                {
                    custom_kiss_x_offset = futa_saved_kiss_x_offset;
                    custom_kiss_y_offset = futa_saved_kiss_y_offset;
                    custom_boob_x_offset = futa_saved_boob_x_offset;
                    custom_boob_y_offset = futa_saved_boob_y_offset;
                    custom_headpat_x_offset = futa_saved_headpat_x_offset;
                    custom_headpat_y_offset = futa_saved_headpat_y_offset;
                }
                else
                {
                    custom_kiss_x_offset = wife_saved_kiss_x_offset;
                    custom_kiss_y_offset = wife_saved_kiss_y_offset;
                    custom_boob_x_offset = wife_saved_boob_x_offset;
                    custom_boob_y_offset = wife_saved_boob_y_offset;
                    custom_headpat_x_offset = wife_saved_headpat_x_offset;
                    custom_headpat_y_offset = wife_saved_headpat_y_offset;
                }
            }
        }
    }
    if (headpat_press == true)
    {
        if (headpat_delay > 0)
        {
            headpat_delay -= 1;
        }
        if (point_distance(mouse_x, mouse_y, xprevious, yprevious) > 12 && headpat_delay < 1)
        {
            if (headpat < 20)
            {
                headpat += 1;
            }
            else
            {
                func_bottom_speak("headpat");
                func_top_speak("headpat");
                headpat = 0;
            }
            headpat_delay = 3;
        }
    }
    else if (headpat > 0)
    {
        headpat -= 1;
    }
    if (boob_box)
    {
        if (top_sprite != legacy_custom_mating_press && top_sprite != sFutaMatingBunny)
        {
            if (mouse_check_button_pressed(mb_right) || touch_long_press_synthetic)
            {
                if (portrait_number == 0)
                {
                    outfit_toggle = !outfit_toggle;
                    oAudioManager.play_sfx(sndCloth, 0, random_range(0.8, 1.2), 0.6);
                }
                if (portrait_number == 1)
                {
                    wife_outfit_toggle = !wife_outfit_toggle;
                    oAudioManager.play_sfx(sndCloth, 0, random_range(0.8, 1.2), 0.6);
                }
            }
        }
    }
}
comment = "Virility Clench — periodic clench when virility is high, outside orgasm";
if (orgasm == false && custom_clench_toggle >= 1 && edge_boost < 5 && (custom_bc_loaded == true || legacy_bc_loaded == true || (top_sprite != custom_mating_press && top_sprite != legacy_custom_mating_press)))
{
    var _vc_in_range = false;
    var _vc_t_min = 0;
    var _vc_t_max = 0;
    var _vc_virility = min(virility_modifier, 10);
    if (_vc_virility > 3 && _vc_virility <= 5)
    {
        var _f = clamp((_vc_virility - 3) / 2, 0, 1);
        _vc_t_min = lerp(7, 2, _f);
        _vc_t_max = lerp(21, 8, _f);
        _vc_in_range = true;
    }
    else if (_vc_virility > 5)
    {
        var _f = clamp((_vc_virility - 5) / 5, 0, 1);
        _vc_t_min = lerp(2, 0.7, _f);
        _vc_t_max = lerp(8, 3, _f);
        _vc_in_range = true;
    }
    if (_vc_in_range)
    {
        vc_timer -= (1 / room_speed);
        if (vc_timer <= 0 && vc_active == false)
        {
            comment = "fire a virility clench sequence";
            oAudioManager.play_sfx(choose(sndCumInside1, sndCumInside2, sndCumInside3, sndCumInside4), 0, random_range(0.8, 1.1), 0.9);
            vc_active = true;
            vc_frame = 0;
            vc_dir = 1;
            vc_clench_timer = 0;
            vc_timer = irandom_range(_vc_t_min, _vc_t_max);
        }
    }
    else
    {
        comment = "virility out of range — reset timer, don't fire";
        vc_timer = irandom_range(10, 30);
        vc_active = false;
        vc_frame = 0;
    }
    comment = "Virility Clench — advance frame sequence while active";
    if (vc_active == true)
    {
        var _vc_speed_in = 0.9;
        var _vc_speed_out = 0.085;
        vc_clench_timer += ((vc_dir == 1) ? _vc_speed_in : _vc_speed_out);
        if (vc_dir == 1 && vc_clench_timer >= 1)
        {
            vc_clench_timer = 0;
            vc_frame += 1;
            if (vc_frame >= 2)
            {
                vc_frame = 2;
                vc_dir = 0;
                vc_hold_timer = 15;
                comment = "Virility Clench — leaky pill drip sync at frame 2";
                if (leaky_pill == true)
                {
                    var _vc_drip_volume = random_range(0.02, 0.06) * ball_size * edge_boost * cum_volume_modifier;
                    stat_liters += _vc_drip_volume;
                    stat_sperm_cell += (15 * _vc_drip_volume * 1000 * (0.1 + (0.9 * virility_modifier)));
                    drip_pump_scale = 1;
                    array_push(womb_spurts, [1, true, 120]);
                    if (insert == false)
                    {
                        if (condom == true)
                        {
                            condom_volume += _vc_drip_volume;
                            condom_size = min(4, 3.25 * power((3 * (condom_volume / 100)) / (4 * pi), 1/3));
                            condom_jiggle = -0.2;
                        }
                        if (condom == true && condom_break_toggle == true && condom_strain_played == false && condom_volume >= (condom_break_threshold * 0.8))
                        {
                            condom_strain_played = true;
                            oAudioManager.play_sfx(CondomSTRAIN, 0, 1, 1);
                        }
                        else
                        {
                            var _vc_cum_amount = median(1, round(cum_splash * _vc_drip_volume), 4);
                            repeat (_vc_cum_amount)
                            {
                                var _vc_cum_offset = (80 * top_penis_length) + custom_cum_y_offset;
                                if (sex_position == 3)
                                {
                                    _vc_cum_offset = (120 * top_penis_length) + custom_cum_y_offset;
                                }
                                else if (sex_position > 0)
                                {
                                    _vc_cum_offset = -(30 * top_penis_length) + custom_cum_y_offset;
                                }
                                var _vc_tip = func_mp_next_tip();
                                _vc_cum_offset = func_mp_cum_tip_offset(_vc_tip);
                                var _vc_cum = instance_create_depth(x + func_mp_cum_tip_x(_vc_tip), y + _vc_cum_offset, depth, oCum);
                                _vc_cum.hsp = random_range(-0.1, 0.1);
                                _vc_cum.vsp = random_range(-0.1, 0.1);
                                _vc_cum.cum_color = cum_color;
                            }
                            oAudioManager.play_sfx(choose(sndCumInside1, sndCumInside2, sndCumInside4), 0, random_range(0.9, 1.1), 0.6);
                        }
                    }
                    else
                    {
                        if (condom == true)
                        {
                            condom_volume += _vc_drip_volume;
                            condom_lerp = condom_volume + (0.06 * fill_max);
                            condom_size = min(4, 2 * power((3 * (condom_volume / 100)) / (4 * pi), 1/3));
                            condom_jiggle = -0.2;
                        }
                        if (condom == true && condom_break_toggle == true && condom_strain_played == false && condom_volume >= (condom_break_threshold * 0.8))
                        {
                            condom_strain_played = true;
                            oAudioManager.play_sfx(CondomSTRAIN, 0, 1, 1);
                        }
                        else
                        {
                            fill_amount += _vc_drip_volume;
                            fill_lerp = fill_amount + (0.06 * fill_max);
                            cum_fill_color = merge_colour(cum_fill_color, cum_color, 0.1);
                        }
                        oAudioManager.play_sfx(choose(sndCumInside1, sndCumInside2, sndCumInside4), 0, random_range(0.9, 1.1), 0.6);
                    }
                }
            }
        }
        else if (vc_dir == 0)
        {
            vc_hold_timer -= 1;
            if (vc_hold_timer <= 0)
            {
                vc_dir = -1;
            }
        }
        else if (vc_dir == -1 && vc_clench_timer >= 1)
        {
            vc_clench_timer = 0;
            vc_frame -= 1;
            if (vc_frame <= 0)
            {
                vc_frame = 0;
                vc_active = false;
            }
        }
    }
}
else if (orgasm == true)
{
    comment = "orgasm is running — reset vc so it doesn't interfere";
    vc_active = false;
    vc_frame = 0;
    vc_clench_timer = 0;
    vc_hold_timer = 0;
}
comment = "Edge Clench — tweakable values";
var _ec_min_boost = 5;
var _ec_chance_base = 0.35;
var _ec_chance_per_level = 0.08;
var _ec_chance = _ec_chance_base + ((edge_boost - _ec_min_boost) * _ec_chance_per_level);
var _ec_speed_in = 0.9;
var _ec_speed_out = 0.085;
var _ec_hold_frames = 15;
var _ec_pitch = 0.75;
var _ec_timer_min = 8;
var _ec_timer_max = 20;
comment = "Edge Clench — only fires outside orgasm when edge_boost is in range";
if (orgasm == false && custom_clench_toggle >= 1 && edge_boost >= _ec_min_boost && (custom_bc_loaded == true || legacy_bc_loaded == true || (top_sprite != custom_mating_press && top_sprite != legacy_custom_mating_press)))
{
    if (ec_active == false)
    {
        ec_timer -= (1 / room_speed);
        if (ec_timer <= 0)
        {
            if (random(1) < _ec_chance)
            {
                ec_active = true;
                ec_frame = 0;
                ec_dir = 1;
                ec_clench_timer = 0;
                oAudioManager.play_sfx(sndCumInside2, 0, _ec_pitch, 1);
                ec_timer = irandom_range(_ec_timer_min, _ec_timer_max);
            }
            else
            {
                ec_timer = 3;
            }
        }
    }
    if (ec_active == true)
    {
        ec_clench_timer += ((ec_dir == 1) ? _ec_speed_in : _ec_speed_out);
        if (ec_dir == 1 && ec_clench_timer >= 1)
        {
            ec_clench_timer = 0;
            ec_frame += 1;
            if (ec_frame >= 4)
            {
                ec_frame = 4;
                ec_dir = 0;
                ec_hold_timer = _ec_hold_frames;
            }
        }
        else if (ec_dir == 0)
        {
            ec_hold_timer -= 1;
            if (ec_hold_timer <= 0)
            {
                ec_dir = -1;
            }
        }
        else if (ec_dir == -1 && ec_clench_timer >= 1)
        {
            ec_clench_timer = 0;
            ec_frame -= 1;
            if (ec_frame <= 0)
            {
                ec_frame = 0;
                ec_active = false;
            }
        }
    }
}
else if (orgasm == false && ec_active == false)
{
    ec_frame = 0;
    ec_clench_timer = 0;
}
else if (orgasm == true)
{
    comment = "orgasm running — reset ec so it doesn't interfere";
    ec_active = false;
    ec_frame = 0;
    ec_clench_timer = 0;
    ec_hold_timer = 0;
}
if (background_menu_toggle)
{
    menu_scroll_update(bg_menu, total_background_amount, 11);
}
if (global.rg_active && audio_exists(global.rg_instance))
{
    audio_sound_gain(global.rg_instance, 1, 0);
}
