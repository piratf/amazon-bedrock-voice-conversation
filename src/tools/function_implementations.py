import sqlite3
import os

DB_PATH = os.getenv('DB_PATH', '/Users/span/Projects/ScrapyProjects/LoLFandomWiki/db/service.db')

def execute_query(query: str, params: tuple = (), fetch_one: bool = False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        if fetch_one:
            result = cursor.fetchone()
            return dict(zip(columns, result)) if result else {}
        else:
            results = cursor.fetchall()
            return [dict(zip(columns, row)) for row in results]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {} if fetch_one else []
    finally:
        cursor.close()
        conn.close()

ALLOWED_SLOTS = {'Q', 'W', 'E', 'R', 'Passive'}

def get_champion_stat(champion_name: str) -> dict:
    return execute_query("SELECT * FROM champion_stat WHERE champion_name = ?", (champion_name,), fetch_one=True)

def get_champion_spells(champion_name: str) -> list:
    return execute_query("SELECT * FROM champion_spells WHERE champion_name = ?", (champion_name,))

def get_champion_story(champion_name: str) -> dict:
    return execute_query("SELECT * FROM champion_story WHERE champion_name = ?", (champion_name,), fetch_one=True)

def get_champions_background(name: str) -> dict:
    return execute_query("SELECT * FROM champions_background WHERE name = ?", (name,), fetch_one=True)

def get_champion_spell_by_slot(champion_name: str, slot: str) -> dict:
    if slot not in ALLOWED_SLOTS:
        raise ValueError(f"Invalid slot: {slot}. Allowed slots are {ALLOWED_SLOTS}.")

    result = execute_query("SELECT * FROM champion_spells WHERE champion_name = ? AND slot = ?", (champion_name, slot), fetch_one=True)

    if not result:
        return {"error": f"No spell found for champion {champion_name} in slot {slot}"}

    result = {k: v for k, v in result.items() if v is not None and v != ""}

    if 'cooldown' in result and result['cooldown']:
        result['cooldown_description'] = "This is a split string containing cooldown time at each level."

    return result

def get_rune_path(path_identifier: str) -> dict:
    query = "SELECT * FROM rune_paths WHERE name = ? OR key = ?"
    return execute_query(query, (path_identifier, path_identifier), fetch_one=True)

def get_runes_by_path(path_identifier: str) -> dict:
    path = get_rune_path(path_identifier)
    if not path:
        return {"error": f"No rune path found for identifier: {path_identifier}"}

    query = """
    SELECT r.*, rs.id as slot_id
    FROM runes r
    JOIN rune_slots rs ON r.slot_id = rs.id
    WHERE rs.rune_path_id = ?
    ORDER BY rs.id, r.id
    """
    runes = execute_query(query, (path['id'],))

    result = {**path, "slots": {}}
    for rune in runes:
        slot_id = rune.pop('slot_id')
        if slot_id not in result["slots"]:
            result["slots"][slot_id] = []
        result["slots"][slot_id].append(rune)

    return result

def get_rune_details(rune_identifier: str) -> dict:
    query = """
    SELECT r.*, rp.name as path_name, rp.key as path_key
    FROM runes r
    JOIN rune_slots rs ON r.slot_id = rs.id
    JOIN rune_paths rp ON rs.rune_path_id = rp.id
    WHERE r.name = ? OR r.key = ?
    """
    return execute_query(query, (rune_identifier, rune_identifier), fetch_one=True)

def get_keystone_runes() -> list:
    query = """
    SELECT r.*, rp.name as path_name, rp.key as path_key
    FROM runes r
    JOIN rune_slots rs ON r.slot_id = rs.id
    JOIN rune_paths rp ON rs.rune_path_id = rp.id
    WHERE r.is_key_stone_rune = 1
    """
    return execute_query(query)

def get_runes_by_slot(path_identifier: str, slot_number: int) -> list:
    path = get_rune_path(path_identifier)
    if not path:
        return {"error": f"No rune path found for identifier: {path_identifier}"}

    query = """
    SELECT r.*
    FROM runes r
    JOIN rune_slots rs ON r.slot_id = rs.id
    WHERE rs.rune_path_id = ? AND rs.id = ?
    """
    return execute_query(query, (path['id'], slot_number))

def get_all_runes_structured() -> dict:
    query = """
    SELECT rp.*, rs.id as slot_id, r.*
    FROM rune_paths rp
    JOIN rune_slots rs ON rp.id = rs.rune_path_id
    JOIN runes r ON rs.id = r.slot_id
    ORDER BY rp.id, rs.id, r.id
    """
    results = execute_query(query)

    structured_runes = {"rune_paths": []}
    current_path = None
    current_slot = None

    for row in results:
        path_id = row['id']
        slot_id = row['slot_id']

        if current_path is None or current_path['id'] != path_id:
            current_path = {
                'id': path_id,
                'key': row['key'],
                'icon': row['icon'],
                'name': row['name'],
                'slots': []
            }
            structured_runes['rune_paths'].append(current_path)
            current_slot = None

        if current_slot is None or current_slot['slot_number'] != slot_id:
            current_slot = {
                'slot_number': slot_id,
                'runes': []
            }
            current_path['slots'].append(current_slot)

        rune = {
            'id': row['id'],
            'key': row['key'],
            'icon': row['icon'],
            'name': row['name'],
            'short_desc': row['short_desc'],
            'long_desc': row['long_desc'],
            'is_keystone_rune': bool(row['is_key_stone_rune'])
        }
        current_slot['runes'].append(rune)

    return structured_runes