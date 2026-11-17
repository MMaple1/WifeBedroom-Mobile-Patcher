            case "shaft":
                comment = "layer 1 (base/sheath) - safe fallback to base shaft if custom spritesheet lacks pill frames";
                var _spr_frames = sprite_get_number(top_sprite);
                if (penis_type_index == 1 && _spr_frames > 11)
                    return 11;
                if (penis_type_index == 2 && _spr_frames > 15)
                    return 15;
                if (penis_type_index == 3 && _spr_frames > 18)
                    return 18;
                return 7;