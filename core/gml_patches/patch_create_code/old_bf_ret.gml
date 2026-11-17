                    case custom_wife_mating_press:
                        return_port = custom_wife_portrait;
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
    return return_port;