            case "shaft":
                comment = "layer 1 (base/sheath)";
                if (penis_type_index == 0)
                {
                    comment = "human shaft";
                    return 7;
                }
                if (penis_type_index == 1)
                {
                    comment = "horse sheath";
                    return 11;
                }
                if (penis_type_index == 2)
                {
                    comment = "knotted penis full";
                    return 15;
                }
                if (penis_type_index == 3)
                {
                    comment = "knotted horse full";
                    return 18;
                }
                return 7;