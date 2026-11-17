                var _sp_ini = string(arg0) + "/custom_data.spouse";
                if (!file_exists(_sp_ini)) _sp_ini = string(arg0) + "/custom_data.wife";
                ini_open(_sp_ini);