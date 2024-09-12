from function_dispatcher import function_dispatcher

# Example of calling the dispatcher for the new function
result = function_dispatcher("get_champion_spell_by_slot", champion_name="Aatrox", slot="Passive")
print(result)