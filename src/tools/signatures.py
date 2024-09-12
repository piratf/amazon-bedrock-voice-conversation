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
    }
]

# Convert the tools list to a JSON string
tools_json = json.dumps(tools, indent=4)

if __name__ == "__main__":
    # Print the JSON string (optional)
    print(tools_json)