from src.tools.db_manager import SingletonDatabaseConnection

ALLOWED_SLOTS = {'Q', 'W', 'E', 'R', 'Passive'}

def get_champion_stat(champion_id: str) -> dict:
    db = SingletonDatabaseConnection()
    return db.query_one("SELECT * FROM champion_stat WHERE champion_id = ?", (champion_id,))

def get_champion_spells(champion_name: str) -> list:
    db = SingletonDatabaseConnection()
    return db.query("SELECT * FROM champion_spells WHERE champion_name = ?", (champion_name,))

def get_champion_story(champion_name: str) -> dict:
    db = SingletonDatabaseConnection()
    return db.query_one("SELECT * FROM champion_story WHERE champion_name = ?", (champion_name,))

def get_champions_background(name: str) -> dict:
    db = SingletonDatabaseConnection()
    return db.query_one("SELECT * FROM champions_background WHERE name = ?", (name,))

def get_champion_spell_by_slot(champion_name: str, slot: str) -> dict:
    if slot not in ALLOWED_SLOTS:
        raise ValueError(f"Invalid slot: {slot}. Allowed slots are {ALLOWED_SLOTS}.")
    
    db = SingletonDatabaseConnection()
    result = db.query_one("SELECT * FROM champion_spells WHERE champion_name = ? AND slot = ?", (champion_name, slot))
    
    if not result:
        return {"error": f"No spell found for champion {champion_name} in slot {slot}"}

    if result:
        # Remove empty fields
        result = {k: v for k, v in result.items() if v is not None and v != ""}

        # Add descriptions to specific fields
        if 'cooldown' in result and result['cooldown']:
            result['cooldown_description'] = "This is a split string containing cooldown time at each level."
    
    return result