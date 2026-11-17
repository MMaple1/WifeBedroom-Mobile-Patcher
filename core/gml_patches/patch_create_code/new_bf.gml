function func_get_portrait_boobs(arg0, arg1)
{
    var return_port = sFutaPortrait1;
    switch (arg1)
    {
        case 0:
            if (outfit_toggle == false)
            {
                switch (arg0)
                {
                    case sFutaMatingPress:
                        return_port = sFutaPortrait1;
                        break;
                    case sFutaMatingPressDevil:
                        return_port = sFutaPortraitDevil;
                        break;
                    case sFutaMatingPressSlime:
                        return_port = sFutaPortraitSlime;
                        break;
                    case sFutaMatingPressAndroid:
                        return_port = sFutaPortraitAndroid;
                        break;
                    case sFutaMatingPressAlien:
                        return_port = sFutaPortraitAlien;
                        break;
                    case sFutaMatingPressClown:
                        return_port = sFutaPortraitClown;
                        break;
                    case sFutaMatingBunny:
                        return_port = sFutaPortraitBunny;
                        break;
                    case sFutaMatingFurry:
                        return_port = sFutaPortraitFurry;
                        break;
                    case custom_mating_press:
                        return_port = (sprite_exists(custom_portrait) && custom_portrait != -1) ? custom_portrait : sFutaPortrait1;
                        break;
                    case legacy_custom_mating_press:
                        return_port = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
                        break;
                }
            }