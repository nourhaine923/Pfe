ATTRIBUTE_REGISTRY = {

    #SCORE 1 ATTRIBUTES

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

# ---------------SCORE 2 ATTRIBUTES----------


# FOLLOW UP

"visit_date": lambda ctx: ctx["followup"].get("visitDate"),

"post_transplant_day": lambda ctx:
    ctx["followup"].get("postTransplantDay"),

"post_transplant_month": lambda ctx:
    ctx["followup"].get("postTransplantMonth"),

"visit_type": lambda ctx:
    ctx["followup"].get("visitType"),

"clinical_status": lambda ctx:
    ctx["followup"].get("clinicalStatus"),



#  BIOLOGICAL 

"bio_date": lambda ctx:
    ctx["biological"][0].get("date") if ctx["biological"] else None,

"creatinine": lambda ctx:
    ctx["biological"][0].get("creatinine") if ctx["biological"] else None,

"urea": lambda ctx:
    ctx["biological"][0].get("urea") if ctx["biological"] else None,

"gfr": lambda ctx:
    ctx["biological"][0].get("gfr") if ctx["biological"] else None,

"hemoglobin": lambda ctx:
    ctx["biological"][0].get("hemoglobin") if ctx["biological"] else None,

"crp": lambda ctx:
    ctx["biological"][0].get("crp") if ctx["biological"] else None,

"tsh": lambda ctx:
    ctx["biological"][0].get("tsh") if ctx["biological"] else None,

"other_biomarker_1": lambda ctx:
    ctx["biological"][0].get("otherBioMarker1") if ctx["biological"] else None,

"other_biomarker_2": lambda ctx:
    ctx["biological"][0].get("otherBioMarker2") if ctx["biological"] else None,


#  ADVERSE EVENTS 

"has_adverse_event": lambda ctx:
    len(ctx["adverse_events"]) > 0,

"adverse_event_count": lambda ctx:
    len(ctx["adverse_events"]),

"adverse_event_types": lambda ctx:
    [e.get("eventType") for e in ctx["adverse_events"]],

"max_severity": lambda ctx:
    max([e.get("severity", 0) for e in ctx["adverse_events"]], default=None),


"immun_marker_types": lambda ctx:
    [m.get("markerType") for m in ctx.get("immunological", [])],

"immun_marker_values": lambda ctx:
    [m.get("value") for m in ctx.get("immunological", [])],

    # OUTCOME

"alive_with_graft": lambda ctx:
    ctx["outcome"].get("aliveWithFunctioningGraft") if ctx["outcome"] else None,

"return_to_dialysis": lambda ctx:
    ctx["outcome"].get("returnToDialysis") if ctx["outcome"] else None,

"death_with_graft": lambda ctx:
    ctx["outcome"].get("deathWithFunctioningGraft") if ctx["outcome"] else None,

"lost_to_followup": lambda ctx:
    ctx["outcome"].get("lostToFollowUp") if ctx["outcome"] else None,

# ---------------- SCORE 3 DERIVED ----------------

"followup_count": lambda ctx: len(ctx["followups"]),

"adverse_event_rate": lambda ctx:
    len(ctx["adverse_events"]) / len(ctx["followups"])
    if ctx["followups"] else 0,

"mean_creatinine": lambda ctx:
    sum(b["creatinine"] for b in ctx["biological"]) / len(ctx["biological"])
    if ctx["biological"] else None,

"max_creatinine": lambda ctx:
    max(b["creatinine"] for b in ctx["biological"])
    if ctx["biological"] else None,

"min_gfr": lambda ctx:
    min(b["gfr"] for b in ctx["biological"])
    if ctx["biological"] else None,

"graft_loss": lambda ctx:
    ctx["outcome"].get("returnToDialysis") if ctx["outcome"] else False,
}


