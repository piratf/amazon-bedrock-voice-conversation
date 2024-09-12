function_signatures = {
    "get_champion_stats": {
        "name": "get_champion_stats",
        "description": "get the stats of a champion, including their abilities, stats, and other relevant information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "champion_name": {
                    "type": "string",
                    "description": "The text to analyze."
                }
            },
            "required": ["champion_name"]
        }
    },
    "get_champion_background": {
        "name": "get_champion_background",
        "description": "get the background of a champion, including where they are from and their role in the game, and their lore, story, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "champion_name": {
                    "type": "string",
                    "description": "The name of the champion to get the background for."
                }
            },
            "required": ["champion_name"]
        }
    },
    "get_champion_build": {
        "name": "get_champion_build",
        "description": """get the build for a champion, includeing a list of items to buy and the order to buy them in. 
        the items should be a list of numbers that represent the item ids, and the list order is the order to buy them in.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "champion_name": {
                    "type": "string",
                    "description": "The name of the champion to get the build for."
                }
            },
            "required": ["champion_name"]
        }
    },
    "get_summoner_spells": {
        "name": "get_summoner_spells",
        "description": "get the summoner spells description and cooldowns.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summoner_spells": {
                    "type": "array",
                    "description": "The list of summoner spells to get the description and cooldowns for."
                },
                "context": {
                    "type": "string",
                    "description": "The context for generating the response."
                }
            },
            "required": ["text", "context"]
        }
    },
    "complete_question_for_kb": {
        "name": "complete_question_for_kb",
        "description": "Complete the question with context from the conversation history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question to complete."
                }
            },
            "required": ["question"]
        }
    },
    "get_runes": {
        "name": "get_runes",
        "description": "Retrieve rune information based on optional filters such as path ID or key. If no filters are provided, all runes are returned. The function joins the `runes`, `rune_slots`, and `rune_paths` tables to provide comprehensive rune details, including the rune path name. The fields returned are: rune ID, rune key, rune icon, rune name, short description, long description, and rune path name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "rune_path_name": {
                    "type": "integer",
                    "description": "The ID of the rune path to filter runes by."
                },
                "rune_name": {
                    "type": "string",
                    "description": "The key of the rune to filter runes by."
                }
            },
            "required": []
        }
    }
}