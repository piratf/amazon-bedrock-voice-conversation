import json

# Define the JSON signatures for each tool
tools = [
    {
        "name": "get_champion_stat",
        "description": "Retrieves the statistics for a given champion by their ID. This includes attributes like hp, mp, armor, and attack damage.",
        "input_schema": {
            "type": "object",
            "properties": {
                "champion_id": {
                    "type": "string",
                    "description": "The unique identifier for the champion."
                }
            },
            "required": ["champion_id"]
        }
    },
    {
        "name": "get_champion_spells",
        "description": "Retrieves the spells for a given champion by their name. This includes details like spell name, description, cooldown, and cost.",
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
        "description": "Retrieves the background information for a given champion by their name. This includes details like title, quote, biography, role, and region.",
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
        "description": "Retrieves the spell for a given champion by their name and slot. The slot can be Q, W, E, R, or Passive.",
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