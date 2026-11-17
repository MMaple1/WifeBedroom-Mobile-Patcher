var bottom_sprite;
if (custom_wife_toggle == true && legacy_custom_wife_toggle)
{
    bottom_sprite = legacy_custom_wife_mating_press;
}
else if (_spr_custom_wife_mp)
{
    bottom_sprite = custom_wife_mating_press;
}