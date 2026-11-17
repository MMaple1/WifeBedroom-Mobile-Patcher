                case "shaft":
                    comment = "layer 1 (base/sheath)";
                    if (penis_type_index == 0)
                    {
                        comment = "human shaft";
                        return 2;
                    }
                    if (penis_type_index == 1)
                    {
                        comment = "horse sheath";
                        return -1;
                    }
                    if (penis_type_index == 2)
                    {
                        comment = "knotted penis";
                        return -1;
                    }
                    if (penis_type_index == 3)
                    {
                        comment = "knotted horse shaft";
                        return -1;
                    }
                    return 2;