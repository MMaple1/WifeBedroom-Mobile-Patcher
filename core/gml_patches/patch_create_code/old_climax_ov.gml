    if (sex_position != 3)
    {
        for (var i = 0; i < wife_climax_stage; i++)
        {
            if (i == 0)
            {
                func_ovulate();
            }
            else
            {
                var total_chance = 0.2 + (count_normal * 0.3) + stat_bonus;
                var drop_chance = total_chance / i;
                if (random(1) <= drop_chance)
                {
                    func_ovulate();
                }
            }
        }
    }