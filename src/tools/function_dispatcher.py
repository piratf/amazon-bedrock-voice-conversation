from src.tools.function_implementations import (
    get_champion_stat, get_champion_spells, get_champion_story, get_champions_background, 
    get_champion_spell_by_slot, get_rune_path, get_runes_by_path, get_rune_details, 
    get_keystone_runes, get_runes_by_slot, get_all_runes_structured, get_all_items_brief
)

def function_dispatcher(function_name: str, **kwargs):
    function_map = {
        "get_champion_stat": lambda: get_champion_stat(kwargs.get("champion_name")),
        "get_champion_spells": lambda: get_champion_spells(kwargs.get("champion_name")),
        "get_champion_story": lambda: get_champion_story(kwargs.get("champion_name")),
        "get_champions_background": lambda: get_champions_background(kwargs.get("name")),
        "get_champion_spell_by_slot": lambda: get_champion_spell_by_slot(kwargs.get("champion_name"), kwargs.get("slot")),
        "get_rune_path": lambda: get_rune_path(kwargs.get("path_identifier")),
        "get_runes_by_path": lambda: get_runes_by_path(kwargs.get("path_identifier")),
        "get_rune_details": lambda: get_rune_details(kwargs.get("rune_identifier")),
        "get_keystone_runes": get_keystone_runes,
        "get_runes_by_slot": lambda: get_runes_by_slot(kwargs.get("path_identifier"), kwargs.get("slot_number")),
        "get_all_runes_structured": get_all_runes_structured,
        "get_all_items_brief": get_all_items_brief
    }

    if function_name in function_map:
        return function_map[function_name]()
    else:
        raise ValueError(f"Unknown function: {function_name}")