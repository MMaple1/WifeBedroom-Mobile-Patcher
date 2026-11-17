            else if (wife_outfit_sprite == sWifeNormalCowgirlOutfit3)
            {
                return_port = sFutaPortrait3;
            }
            break;
    }
    if (!sprite_exists(return_port) || return_port <= 0)
    {
        return_port = sFutaPortrait1;
    }
    return return_port;
}