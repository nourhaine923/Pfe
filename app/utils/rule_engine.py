# app/utils/rule_engine.py

def evaluate_condition(raw_value, condition):
    """
    Evaluate a condition against a raw value.
    Handles None values safely.
    """
    # If raw_value is None, return False (can't evaluate)
    if raw_value is None:
        return False

    operator = condition.get("operator")
    expected = condition.get("value")

    # CONDITIONAL NUMERIC RULES 
    if operator == "between":
        # Handle both list and tuple safely
        if isinstance(expected, (list, tuple)) and len(expected) >= 2:
            low, high = expected[0], expected[1]
            # Ensure low and high are numbers
            try:
                return float(low) <= float(raw_value) <= float(high)
            except (ValueError, TypeError):
                return False
        return False

    if operator == "greater_than":
        try:
            return float(raw_value) > float(expected)
        except (ValueError, TypeError):
            return False

    if operator == "less_than":
        try:
            return float(raw_value) < float(expected)
        except (ValueError, TypeError):
            return False

    if operator == "equal":
        return raw_value == expected

    # BOOLEAN RULE 
    if operator is None and isinstance(expected, bool):
        return raw_value == expected

    # CATEGORICAL RULE 
    if operator is None and isinstance(expected, str):
        return str(raw_value) == expected

    return False


def apply_rule(attribute_value, value_block):
    """
    Applies a value rule block (conditional/boolean/categorical) 
    and returns the matching impact.
    """
    # If attribute_value is None, skip
    if attribute_value is None:
        return 0

    for condition in value_block.get("conditions", []):
        if evaluate_condition(attribute_value, condition):
            return condition.get("impact", 0)

    return 0


def compute_attribute_score(raw_value, barem_definition):
    """
    Computes total score impact for a given attribute 
    based on its raw value and the Barem definition.
    """
    # If raw_value is None, return 0
    if raw_value is None:
        return 0

    total_impact = 0

    for value_block in barem_definition.get("values", []):
        total_impact += apply_rule(raw_value, value_block)

    return total_impact