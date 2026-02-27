from pymongo.pool_shared import key


def normalize_value(key, value):

    # AGE 
    if key == "recipient_age":
        if value < 40:
            return "18-40"
        elif value <= 60:
            return "41-60"
        return ">60"
    
        # weight_kg
    if key == "weight_kg":
        if value < 60:
            return "<60"
        elif value <= 100:
            return "60-100"
        return ">100"

    if key == "donor_age":
        if 18 <= value <= 35:
            return "18-35"
        elif value <= 50:
            return "36-50"
        elif value <= 65:
            return "51-65"
        return "<18 or >65"

    # BMI 
    if key == "bmi":
        if 18.5 <= value <= 25:
            return "18.5-25"
        elif value <= 30:
            return "25-30"
        return ">30 or <18.5"

    # BOOLEAN 
    if key in ["diabetes", "hypertension", "acc"]:
        return "True" if value else "False"

    if key in ["hbsag", "anti_hcv"]:
        return "Positive" if value else "Negative"

    if key == "transfusion_history":
        return "Yes" if value else "None"

    # ISCHEMIA
    if key == "cold_ischemia":
        if value < 12:
            return "<12 hours"
        elif value <= 18:
            return "12-18 hours"
        elif value <= 24:
            return "18-24 hours"
        return ">24 hours"

    if key == "warm_ischemia":
        if value < 30:
            return "<30 minutes"
        elif value <= 45:
            return "30-45 minutes"
        elif value <= 60:
            return "45-60 minutes"
        return ">60 minutes"

    # PREVIOUS TRANSPLANTS 
    if key == "previous_transplants":
        if value == 0:
            return "0"
        elif value == 1:
            return "1"
        return "≥2"

    # BLOOD COMPATIBILITY
    if key == "blood_compatibility":
        recipient_bg, donor_bg = value

        if recipient_bg == donor_bg:
            return "Identical"

        compatible = {
            "A+": ["A+", "O+"],
            "B+": ["B+", "O+"],
            "AB+": ["A+", "B+", "AB+", "O+"],
            "O+": ["O+"]
        }

        if donor_bg in compatible.get(recipient_bg, []):
            return "Compatible"

        return "Incompatible"

    # HLA 
    if key == "hla_matching":
        recipient_hla, donor_hla = value

        mismatches = 0
        for locus in ["hlaA1","hlaA2","hlaB1","hlaB2","hlaDR1","hlaDR2"]:
            if recipient_hla.get(locus) != donor_hla.get(locus):
                mismatches += 1

        if mismatches == 0:
            return "0/6 mismatches"
        elif mismatches <= 2:
            return "1-2/6 mismatches"
        elif mismatches <= 4:
            return "3-4/6 mismatches"
        return "5-6/6 mismatches"

    return value

