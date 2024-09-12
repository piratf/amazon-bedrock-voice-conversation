from function_dispatcher import function_dispatcher

def test_function(function_name, **kwargs):
    result = function_dispatcher(function_name, **kwargs)
    print(f"Result of {function_name}:")
    print(result)
    print("\n" + "="*50 + "\n")

# Test existing functions
test_function("get_champion_spell_by_slot", champion_name="Aatrox", slot="Passive")

# Test new rune functions
test_function("get_rune_path", path_identifier="Precision")
test_function("get_runes_by_path", path_identifier="Domination")
test_function("get_rune_details", rune_identifier="Electrocute")
test_function("get_keystone_runes")
test_function("get_runes_by_slot", path_identifier="Sorcery", slot_number=2)
test_function("get_all_runes_structured")

# Test new get_all_items_brief function
test_function("get_all_items_brief")