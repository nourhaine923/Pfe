def map_age(value):
    if value < 40:
        return "18-40"
    elif value <= 60:
        return "41-60"
    return ">60"


def map_donor_age(value):
    if 18 <= value <= 35:
        return "18-35"
    elif value <= 50:
        return "36-50"
    elif value <= 65:
        return "51-65"
    return "<18_or_>65"


def map_boolean(value):
    return "True" if value else "False"


def map_cold_ischemia(hours):
    if hours < 12:
        return "<12 hours"
    elif hours <= 18:
        return "12-18 hours"
    elif hours <= 24:
        return "18-24 hours"
    return ">24 hours"