                    case custom_mating_press:
                        return_port = (sprite_exists(custom_portrait) && custom_portrait != -1) ? custom_portrait : sFutaPortrait1;
                        break;
                    case legacy_custom_mating_press:
                        return_port = (sprite_exists(legacy_custom_portrait) && legacy_custom_portrait != -1) ? legacy_custom_portrait : sFutaPortrait1;
                        break;