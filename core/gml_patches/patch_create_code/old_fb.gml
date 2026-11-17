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
            return_port = custom_wife_portrait;
            break;
    }
    return return_port;
}