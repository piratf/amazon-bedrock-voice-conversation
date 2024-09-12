import json

# Define the JSON signatures for each tool
tools = [
    {
        "name": "get_champion_stat",
        "description": "Retrieves the statistics for a given champion by their name. This includes attributes like hp, hp per level, mp, mp per level, move speed, armor, armor per level, spell block, spell block per level, attack range, hp regen, hp regen per level, mp regen, mp regen per level, crit, crit per level, attack damage, attack damage per level, attack speed per level, and attack speed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "champion_name": {
                    "type": "string",
                    "description": "The name of the champion."
                }
            },
            "required": ["champion_name"]
        }
    },
    {
        "name": "get_champion_spells",
        "description": "Retrieves the spells for a given champion by their name. This includes details like spell name, description, tooltip, cooldown in each level, label, max rank, and cost type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "champion_name": {
                    "type": "string",
                    "description": "The name of the champion."
                }
            },
            "required": ["champion_name"]
        }
    },
    {
        "name": "get_champion_story",
        "description": "Retrieves the story for a given champion by their name. This includes the title and content of the story.",
        "input_schema": {
            "type": "object",
            "properties": {
                "champion_name": {
                    "type": "string",
                    "description": "The name of the champion."
                }
            },
            "required": ["champion_name"]
        }
    },
    {
        "name": "get_champions_background",
        "description": "Retrieves the background information for a given champion by their name. This includes details like title, quote, biography, role, related champions, region, tags, ally tips, and enemy tips.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the champion."
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_champion_spell_by_slot",
        "description": "Retrieves the spell for a given champion by their name and slot. The slot can be Q, W, E, R, or Passive. This includes details like spell id, name, description, tooltip, cooldown, label, max rank, and cost type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "champion_name": {
                    "type": "string",
                    "description": "The name of the champion."
                },
                "slot": {
                    "type": "string",
                    "description": "The slot of the spell (Q, W, E, R, or Passive)."
                }
            },
            "required": ["champion_name", "slot"]
        }
    },
    {
        "name": "get_rune_path",
        "description": "Retrieves information about a rune path by its name or key. This includes details like the path's id, key, icon, and name. Rune paths are the main categories of runes, such as Precision, Domination, Sorcery, Resolve, and Inspiration.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path_identifier": {
                    "type": "string",
                    "description": "The name or key of the rune path."
                }
            },
            "required": ["path_identifier"]
        }
    },
    {
        "name": "get_runes_by_path",
        "description": "Retrieves all runes associated with a specific rune path. This includes keystone runes and regular runes. For each rune, it provides details such as id, key, icon, name, short description, long description, slot information, and whether it's a keystone rune. The runes are organized by their slots within the path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path_identifier": {
                    "type": "string",
                    "description": "The name or key of the rune path."
                }
            },
            "required": ["path_identifier"]
        }
    },
    {
        "name": "get_rune_details",
        "description": "Retrieves detailed information about a specific rune by its name or key. This includes the rune's id, key, icon, name, short description, long description, associated slot and path information, and whether it's a keystone rune.",
        "input_schema": {
            "type": "object",
            "properties": {
                "rune_identifier": {
                    "type": "string",
                    "description": "The name or key of the rune."
                }
            },
            "required": ["rune_identifier"]
        }
    },
    {
        "name": "get_keystone_runes",
        "description": "Retrieves all keystone runes across all rune paths. Keystone runes are the most powerful runes that define a player's playstyle. For each keystone rune, it provides details such as id, key, icon, name, short description, long description, and associated path information.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_runes_by_slot",
        "description": "Retrieves all runes associated with a specific slot within a rune path. Slots represent different tiers or rows within a rune path. This function provides details for each rune in the specified slot, including id, key, icon, name, short description, long description, and whether it's a keystone rune.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path_identifier": {
                    "type": "string",
                    "description": "The name or key of the rune path."
                },
                "slot_number": {
                    "type": "integer",
                    "description": "The slot number within the rune path (usually 1-4, where 1 is typically for keystone runes)."
                }
            },
            "required": ["path_identifier", "slot_number"]
        }
    },
    {
        "name": "get_all_runes_structured",
        "description": "Retrieves a structured representation of all runes in the game, organized by rune paths and slots. This function provides a comprehensive overview of the entire rune system. The returned data structure is as follows:\n\n{\n  'rune_paths': [\n    {\n      'id': int,\n      'key': string,\n      'icon': string,\n      'name': string,\n      'slots': [\n        {\n          'slot_number': int,\n          'runes': [\n            {\n              'id': int,\n              'key': string,\n              'icon': string,\n              'name': string,\n              'short_desc': string,\n              'long_desc': string,\n              'is_keystone_rune': boolean\n            },\n            ...\n          ]\n        },\n        ...\n      ]\n    },\n    ...\n  ]\n}\n\nThis structure allows for easy navigation through all rune paths, their slots, and the runes within each slot. It's particularly useful for getting a complete picture of the rune system or for comparing runes across different paths and slots.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_all_items_brief",
        "description": "Retrieves a brief overview of all items, including their name, base price, total price including price of all required pre-items, short description, tags, and available map names. This function provides a comprehensive summary of all items in the game.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },

]

# Convert the tools list to a JSON string
tools_json = json.dumps(tools, indent=4)

if __name__ == "__main__":
    # Print the JSON string (optional)
    print(tools_json)