def evaluate_condition(raw_value, condition):

    operator = condition.get("operator")
    expected = condition.get("value")

    # CONDITIONAL NUMERIC RULES 
    if operator == "between":
        low, high = expected
        return low <= raw_value <= high

    if operator == "greater_than":
        return raw_value > expected

    if operator == "less_than":
        return raw_value < expected

    if operator == "equal":
        return raw_value == expected

    # BOOLEAN RULE 
    if operator is None and isinstance(expected, bool):
        return raw_value == expected

    # CATEGORICAL RULE 
    if operator is None and isinstance(expected, str):
        return str(raw_value) == expected

    return False
    # Applies a value rule block (conditional/boolean/categorical) and returns the matching impact.
def apply_rule(attribute_value, value_block):


    for condition in value_block.get("conditions", []):
        if evaluate_condition(attribute_value, condition):
            return condition.get("impact", 0)

    return 0
# Computes total score impact for a given attribute based on its raw value and the Barem definition.
def compute_attribute_score(raw_value, barem_definition):


    total_impact = 0

    for value_block in barem_definition.get("values", []):
        total_impact += apply_rule(raw_value, value_block)

    return total_impact