var bottom_sprite = sWifeMatingPress;
if (custom_wife_toggle == true && legacy_custom_wife_toggle && sprite_exists(legacy_custom_wife_mating_press) && legacy_custom_wife_mating_press != -1)
{
    bottom_sprite = legacy_custom_wife_mating_press;
}
else if (custom_wife_toggle == true && sprite_exists(custom_wife_mating_press) && custom_wife_mating_press != -1)
{
    bottom_sprite = custom_wife_mating_press;
}