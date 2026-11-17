                    case custom_wife_mating_press:
                        return_port = (sprite_exists(legacy_custom_wife_portrait) && legacy_custom_wife_portrait != -1) ? legacy_custom_wife_portrait : ((sprite_exists(custom_wife_portrait) && custom_wife_portrait != -1) ? custom_wife_portrait : sFutaPortrait1);
                        break;
                }
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit1)
            {
                return_port = sFutaPortrait2;
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit2)
            {
                return_port = sFutaPortrait4;
            }
            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit3)
            {
                return_port = sFutaPortrait3;
            }
            break;
    }
    return (sprite_exists(return_port) && return_port != -1) ? return_port : sFutaPortrait1;