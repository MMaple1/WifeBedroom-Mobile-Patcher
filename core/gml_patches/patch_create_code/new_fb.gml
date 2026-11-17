function func_wife_portrait_body(arg0)
{
    var return_port = sFutaPortrait1;
    switch (arg0)
    {
        case sWifeMatingPress:
            return_port = sFutaPortrait1;
            break;
        case sWifeMatingPressDevil:
            return_port = sFutaPortraitDevil;
            break;
        case sWifeMatingPressSlime:
            return_port = sFutaPortraitSlime;
            break;
        case sWifeMatingPressAndroid:
            return_port = sFutaPortraitAndroid;
            break;
        case sWifeMatingPressFurry:
            return_port = sFutaPortraitFurry;
            break;
        case custom_wife_mating_press:
            return_port = (sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1) ? custom_wife_portrait : sFutaPortrait1;
            break;
        case legacy_custom_wife_mating_press:
            return_port = (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1) ? legacy_custom_wife_portrait : sFutaPortrait1;
            break;
    }
    return (sprite_exists(return_port) && return_port != -1) ? return_port : sFutaPortrait1;
}