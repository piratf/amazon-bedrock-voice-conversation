from src.tools.function_implementations import get_champion_stat, get_champion_spells, get_champion_story, get_champions_background, get_champion_spell_by_slot

def function_dispatcher(function_name: str, **kwargs):
    if function_name == "get_champion_stat":
        return get_champion_stat(kwargs.get("champion_id"))
    elif function_name == "get_champion_spells":
        return get_champion_spells(kwargs.get("champion_name"))
    elif function_name == "get_champion_story":
        return get_champion_story(kwargs.get("champion_name"))
    elif function_name == "get_champions_background":
        return get_champions_background(kwargs.get("name"))
    elif function_name == "get_champion_spell_by_slot":
        return get_champion_spell_by_slot(kwargs.get("champion_name"), kwargs.get("slot"))
    else:
        raise ValueError(f"Unknown function: {function_name}")