ATTRIBUTE_REGISTRY = {

    # DEMOGRAPHICS 

    "recipient_age": lambda ctx: ctx["recipient"]["clinicalData"]["age_at_transplant"],
    "donor_age": lambda ctx: ctx["donor"]["ageAtDonation"],
    "sex": lambda ctx: ctx["recipient"].get("sex"),
    "foreign_patient": lambda ctx: ctx["recipient"].get("foreignPatient"),

    # MORPHOLOGY 

    "height_cm": lambda ctx: ctx["recipient"].get("heightCm"),
    "weight_kg": lambda ctx: ctx["recipient"].get("weightKg"),

    "bmi": lambda ctx: (
        ctx["recipient"]["weightKg"] /
        ((ctx["recipient"]["heightCm"] / 100) ** 2)
    ),

    # CLINICAL HISTORY 

    "nephropathy": lambda ctx:
        ctx["recipient"]["clinicalData"].get("primary_nephropathy"),

    "dialysis_type": lambda ctx:
        ctx["recipient"]["clinicalData"].get("dialysis_type"),

    "dialysis_duration": lambda ctx:
        ctx["recipient"]["clinicalData"].get("dialysis_duration"),

    "comorbidities": lambda ctx:
        ctx["recipient"]["clinicalData"].get("comorbidities"),

    "transplant_rank": lambda ctx:
        ctx["recipient"]["clinicalData"].get("transplant_rank"),

    #  PRE-TRANSPLANT 

    "diabetes": lambda ctx: ctx["assessment"].get("diabetes"),
    "hypertension": lambda ctx: ctx["assessment"].get("hypertension"),
    "acc": lambda ctx: ctx["assessment"].get("acc"),
    "hbsag": lambda ctx: ctx["assessment"].get("hbsAg"),
    "anti_hcv": lambda ctx: ctx["assessment"].get("antiHCV"),
    "transfusion_history": lambda ctx: ctx["assessment"].get("transfusion"),
    "eer_modality": lambda ctx: ctx["assessment"].get("eerModality"),
    "previous_transplants": lambda ctx:
        ctx["assessment"].get("numberOfPreviousTransplants"),

    "etiology_irc": lambda ctx: ctx["assessment"].get("etiologyIRC"),
    "transplant_delay": lambda ctx: ctx["assessment"].get("trDelayMonths"),
    "serum_creatinine": lambda ctx: ctx["assessment"].get("serumCreatinine"),

    #  TRANSPLANT CONDITIONS

    "donor_type": lambda ctx: ctx["donor"].get("donorType"),
    "cold_ischemia": lambda ctx: ctx["tx"].get("coldIschemiaHours"),
    "warm_ischemia": lambda ctx: ctx["tx"].get("warmIschemiaMinutes"),
    "transplant_location": lambda ctx: ctx["tx"].get("transplantLocation"),
    "service_origin": lambda ctx: ctx["tx"].get("serviceOrigin"),

    # IMMUNOLOGY 

    "blood_compatibility": lambda ctx: (
        ctx["recipient"]["bloodGroup"],
        ctx["donor"]["bloodGroup"]
    ),

    "hla_matching": lambda ctx: (
        ctx["recipient"]["hlaTyping"],
        ctx["donor"]["hlaTyping"]
    ),
}