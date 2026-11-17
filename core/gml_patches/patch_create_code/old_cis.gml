function check_custom_image_size(arg0)
{
    var result = -1;
    var test_sprite = sprite_add(arg0 + "/custom_mating_press.png", 1, false, false, 0, 0);
    var w = sprite_get_width(test_sprite);
    var frame_width = 160;
    var frames = w / frame_width;
    if (frames != 19)
    {
        result = true;
    }
    else
    {
        result = false;
    }
    sprite_delete(test_sprite);
    return result;
}