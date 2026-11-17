function tc_norm_path(arg0)
{
    arg0 = string(arg0);
    while (string_pos("//", arg0) > 0)
    {
        arg0 = string_replace_all(arg0, "//", "/");
    }
    if (os_type == os_android || os_type == os_ios)
    {
        while (string_char_at(arg0, 1) == "/")
        {
            arg0 = string_delete(arg0, 1, 1);
        }
    }
    return arg0;
}

function tc_dir_exists(arg0)
{
    arg0 = tc_norm_path(arg0);
    if (string_char_at(arg0, string_length(arg0)) == "/")
    {
        arg0 = string_copy(arg0, 1, string_length(arg0) - 1);
    }
    return directory_exists(arg0) || file_exists(arg0 + "/_manifest.txt") || file_exists(arg0);
}

function tc_ff_first(arg0, arg1)
{
    tc_ff_items = -1;
    var _m = tc_norm_path(arg0);
    var _cut = string_last_pos("/", _m);
    var _mf = (_cut > 0) ? (string_copy(_m, 1, _cut) + "_manifest.txt") : "_manifest.txt";
    if (!file_exists(_mf))
    {
        if (os_type == os_android || os_type == os_ios)
        {
            return "";
        }
        return file_find_first(arg0, arg1);
    }
    var _pat = string_lower(string_delete(_m, 1, _cut));
    var _suf = (string_char_at(_pat, 1) == "*") ? string_delete(_pat, 1, 1) : "";
    tc_ff_items = [];
    var _f = file_text_open_read(_mf);
    if (_f != -1)
    {
        while (!file_text_eof(_f))
        {
            var _ln = string_replace_all(string_replace_all(file_text_readln(_f), "\r", ""), "\n", "");
            var _lo = string_lower(_ln);
            var _ok = _ln != "" && _lo != "_manifest.txt";
            if (_ok && string_char_at(_pat, 1) == "*")
            {
                _ok = _suf == "" || (string_length(_lo) >= string_length(_suf) && string_copy(_lo, (string_length(_lo) - string_length(_suf)) + 1, string_length(_suf)) == _suf);
            }
            else if (_ok)
            {
                _ok = _lo == _pat;
            }
            if (_ok)
            {
                array_push(tc_ff_items, _ln);
            }
        }
        file_text_close(_f);
    }
    if (os_type != os_android && os_type != os_ios)
    {
        var _real = file_find_first(arg0, arg1);
        while (_real != "")
        {
            if (!array_contains(tc_ff_items, _real))
            {
                array_push(tc_ff_items, _real);
            }
            _real = file_find_next();
        }
        file_find_close();
    }
    tc_ff_pos = 0;
    return tc_ff_next();
}

function tc_ff_next()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type == os_android || os_type == os_ios)
        {
            return "";
        }
        return file_find_next();
    }
    if (tc_ff_pos >= array_length(tc_ff_items))
    {
        return "";
    }
    tc_ff_pos++;
    return tc_ff_items[tc_ff_pos - 1];
}

function tc_ff_close()
{
    if (!is_array(tc_ff_items))
    {
        if (os_type != os_android && os_type != os_ios)
        {
            file_find_close();
        }
    }
    tc_ff_items = -1;
    tc_ff_pos = 0;
}

tc_ff_items = -1;
tc_ff_pos = 0;
tc_wd = working_directory;
if (string_char_at(tc_wd, string_length(tc_wd)) == "/")
{
    tc_wd = string_copy(tc_wd, 1, string_length(tc_wd) - 1);
}
if (instance_number(oDialogueManager) > 1)
{
    instance_destroy();
    exit;
}
dialogue_files = [];
var _dlg_pack_dir = (file_exists("custom_stuff/dialogue_packs/_manifest.txt") || file_exists("assets/custom_stuff/dialogue_packs/_manifest.txt")) ? "custom_stuff/dialogue_packs" : "dialogue_packs";
var file_name = tc_ff_first(_dlg_pack_dir + "/*.json", 0);
while (file_name != "")
{
    array_push(dialogue_files, file_name);
    file_name = tc_ff_next();
}
tc_ff_close();

var _dlg_cust_dir = (file_exists("custom_stuff/dialogue/_manifest.txt") || file_exists("assets/custom_stuff/dialogue/_manifest.txt")) ? "custom_stuff/dialogue" : "dialogue";
var file_name2 = tc_ff_first(_dlg_cust_dir + "/*.json", 0);
while (file_name2 != "")
{
    if (!array_contains(dialogue_files, file_name2))
    {
        array_push(dialogue_files, file_name2);
    }
    file_name2 = tc_ff_next();
}
tc_ff_close();

function func_load_dialogue(arg0)
{
    var found_dialogue_index = "";
    for (i = 0; i < array_length(dialogue_files); i++)
    {
        if (dialogue_files[i] == arg0)
        {
            found_dialogue_index = i;
            break;
        }
    }
    chosen_dialogue = (found_dialogue_index == "") ? ((array_length(dialogue_files) > 0) ? dialogue_files[0] : "") : dialogue_files[found_dialogue_index];
    dialogue_number = (found_dialogue_index == "") ? 0 : found_dialogue_index;
}

dialogue_number = 0;
chosen_dialogue = "";
dialogue_available = (array_length(dialogue_files) > 0) ? load_dialogue_file() : false;
dialogue_toggle = (array_length(dialogue_files) > 0) ? true : false;
dialogue_menu_toggle = (array_length(dialogue_files) > 0) ? true : false;
top_dialogue = "";
top_dialogue_timer = 0;
top_dialogue_color = 12976127;
wife_dialogue = "";
wife_dialogue_timer = 0;
wife_dialogue_color = 13408767;
current_top_color = top_dialogue_color;
current_wife_color = wife_dialogue_color;
current_top_dialogue_priority = -1;
current_wife_dialogue_priority = -1;
last_alternating_speaker = 1;
dialogue_cooldown = 30;
var dialogue_json = 0;
global.dialogue_additional_duration = 0;

function load_dialogue_file()
{
    func_load_dialogue(chosen_dialogue);
    if (chosen_dialogue == "")
    {
        return false;
    }
    var _file_name = "dialogue_packs/" + chosen_dialogue;
    if (!file_exists(_file_name))
    {
        if (file_exists("custom_stuff/dialogue_packs/" + chosen_dialogue))
        {
            _file_name = "custom_stuff/dialogue_packs/" + chosen_dialogue;
        }
        else if (file_exists("custom_stuff/dialogue/" + chosen_dialogue))
        {
            _file_name = "custom_stuff/dialogue/" + chosen_dialogue;
        }
        else if (file_exists("custom_dialogues/" + chosen_dialogue))
        {
            _file_name = "custom_dialogues/" + chosen_dialogue;
        }
        else if (file_exists("dialogue/" + chosen_dialogue))
        {
            _file_name = "dialogue/" + chosen_dialogue;
        }
        else if (file_exists(chosen_dialogue))
        {
            _file_name = chosen_dialogue;
        }
        else
        {
            return false;
        }
    }
    var _buffer = buffer_load(_file_name);
    if (_buffer == -1)
    {
        return false;
    }
    var _json_string = buffer_read(_buffer, buffer_string);
    buffer_delete(_buffer);
    try
    {
        var _data = json_parse(_json_string);
        dialogue_json = _data;
        return true;
    }
    catch (_err)
    {
        show_debug_message("Dialogue JSON parse error bypassed safely");
        return false;
    }
}

function trigger_dialogue(arg0, arg1, arg2, arg3, arg4)
{
    var inject = is_undefined(arg4) ? "" : string(arg4);
    var duration = is_undefined(arg2) ? 120 : (arg2 + global.dialogue_additional_duration);
    var priority = is_undefined(arg3) ? 0 : arg3;
    var _char_dlg_on = variable_instance_exists(oFutaMatingPress.id, "char_dialogue_toggle") && oFutaMatingPress.char_dialogue_toggle == true;
    var _has_custom_top = _char_dlg_on && variable_instance_exists(oFutaMatingPress.id, "custom_dialogue_set_top") && oFutaMatingPress.custom_dialogue_set_top != -1;
    var _has_custom_bottom = _char_dlg_on && variable_instance_exists(oFutaMatingPress.id, "custom_dialogue_set_bottom") && oFutaMatingPress.custom_dialogue_set_bottom != -1;
    var lover_text = "";
    if (arg0 != "")
    {
        if (string_char_at(arg0, 1) == "?")
        {
            var raw = string_delete(arg0, 1, 1);
            raw = string_replace_all(raw, "{0}", inject);
            lover_text = raw;
        }
        else
        {
            if (dialogue_available && dialogue_toggle && chosen_dialogue != "")
            {
                lover_text = pick_from_dialogue_json(arg0, inject);
            }
            if (lover_text == "" && _has_custom_top)
            {
                var _dlg_key = arg0;
                if (_dlg_key == "top_close_to_orgasm")
                {
                    _dlg_key = "sex_halfway";
                }
                else if (_dlg_key == "condom_broke")
                {
                    _dlg_key = "condom_broken";
                }
                else if (_dlg_key == "remove_full_condom")
                {
                    _dlg_key = "condom_off";
                }
                else if (_dlg_key == "sex_after_with_condom")
                {
                    _dlg_key = "sex_after";
                }
                else if (_dlg_key == "impregnate")
                {
                    _dlg_key = "sex_orgasm";
                }
                else if (_dlg_key == "impregnate_after")
                {
                    _dlg_key = "sex_after";
                }
                var _set = oFutaMatingPress.custom_dialogue_set_top;
                if (variable_struct_exists(_set, _dlg_key))
                {
                    var _arr = variable_struct_get(_set, _dlg_key);
                    if (is_array(_arr) && array_length(_arr) > 0)
                    {
                        var _picked = _arr[irandom(array_length(_arr) - 1)];
                        if (_picked != "")
                        {
                            _picked = string_replace_all(_picked, "{0}", inject);
                            _picked = oFutaMatingPress.func_replace_tags(_picked);
                            lover_text = _picked;
                        }
                    }
                }
            }
            if (lover_text == "")
            {
                lover_text = pick_from_dialogue_json(arg0, inject);
            }
        }
    }
    var wife_text = "";
    if (arg1 != "")
    {
        if (string_char_at(arg1, 1) == "?")
        {
            var raw = string_delete(arg1, 1, 1);
            raw = string_replace_all(raw, "{0}", inject);
            wife_text = raw;
        }
        else if (!_has_custom_bottom)
        {
            wife_text = pick_from_dialogue_json(arg1, inject);
        }
    }
    var can_lover_talk = lover_text != "" && global.speaker_type_index != 4;
    var can_wife_talk = wife_text != "" && global.speaker_type_index != 3;
    if (global.speaker_type_index == 1 && can_lover_talk && can_wife_talk)
    {
        if (irandom(1) == 0)
        {
            can_wife_talk = false;
        }
        else
        {
            can_lover_talk = false;
        }
    }
    if (global.speaker_type_index == 2 && can_lover_talk && can_wife_talk)
    {
        if (last_alternating_speaker == 1)
        {
            can_wife_talk = false;
            last_alternating_speaker = 0;
        }
        else
        {
            can_lover_talk = false;
            last_alternating_speaker = 1;
        }
    }
    var show_lover = can_lover_talk && global.dialogue_display_index != 2;
    var show_wife = can_wife_talk && global.dialogue_display_index != 1;
    var new_lover_txt_color = top_dialogue_color;
    var new_wife_txt_color = wife_dialogue_color;
    if (can_lover_talk && !show_lover && global.dialogue_display_index == 2)
    {
        wife_text = lover_text;
        show_wife = true;
        new_wife_txt_color = top_dialogue_color;
    }
    else if (can_wife_talk && !show_wife && global.dialogue_display_index == 1)
    {
        lover_text = wife_text;
        show_lover = true;
        new_lover_txt_color = wife_dialogue_color;
    }
    if (show_lover)
    {
        if (priority > current_top_dialogue_priority || top_dialogue_timer <= -60)
        {
            top_full_text = lover_text;
            top_dialogue = "";
            top_scroll_index = 0;
            top_scroll_timer = 0;
            top_dialogue_timer = duration;
            current_top_dialogue_priority = priority;
            current_top_color = new_lover_txt_color;
        }
    }
    if (show_wife)
    {
        if (priority > current_wife_dialogue_priority || wife_dialogue_timer <= -60)
        {
            wife_full_text = wife_text;
            wife_dialogue = "";
            wife_scroll_index = 0;
            wife_scroll_timer = 0;
            wife_dialogue_timer = duration;
            current_wife_dialogue_priority = priority;
            current_wife_color = new_wife_txt_color;
        }
    }
}

function pick_from_dialogue_json(arg0, arg1)
{
    if (dialogue_available == true)
    {
        var _value = variable_struct_get(dialogue_json, arg0);
        if (is_array(_value) && dialogue_toggle == true)
        {
            array_shuffle_ext(_value);
            var _final_string = string(_value[0]);
            return string_replace_all(_final_string, "{0}", string(arg1));
        }
    }
    return "";
}

top_scroll_index = 0;
top_scroll_timer = 0;
top_full_text = "";
wife_scroll_index = 0;
wife_scroll_timer = 0;
wife_full_text = "";
scroll_speed = 2;
scroll_comma_pause = 8;
scroll_period_pause = 16;
scroll_finish_hold = 90;
