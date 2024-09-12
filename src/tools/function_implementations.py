import sqlite3
import os

DB_PATH = os.getenv('DB_PATH', '/Users/span/Projects/ScrapyProjects/LoLFandomWiki/db/service.db')

def execute_query(query: str, params: tuple, fetch_one: bool = False):
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