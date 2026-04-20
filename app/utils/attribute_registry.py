# app/utils/attribute_registry.py

from bson import ObjectId
from app.database import db

# ============================================
# HELPER FUNCTIONS
# ============================================

def calculate_hla_mismatches(recipient_hla, donor_hla):
    """Calculate number of HLA mismatches (0-6) and return category"""
    if not recipient_hla or not donor_hla:
        return None
    
    mismatches = 0
    # Check A locus
    if recipient_hla.get("hlaA1") != donor_hla.get("hlaA1"):
        mismatches += 1
    if recipient_hla.get("hlaA2") != donor_hla.get("hlaA2"):
        mismatches += 1
    # Check B locus
    if recipient_hla.get("hlaB1") != donor_hla.get("hlaB1"):
        mismatches += 1
    if recipient_hla.get("hlaB2") != donor_hla.get("hlaB2"):
        mismatches += 1
    # Check DR locus
    if recipient_hla.get("hlaDR1") != donor_hla.get("hlaDR1"):
        mismatches += 1
    if recipient_hla.get("hlaDR2") != donor_hla.get("hlaDR2"):
        mismatches += 1
    
    # Return category
    if mismatches == 0:
        return "0/6 mismatches"
    elif mismatches <= 2:
        return "1-2/6 mismatches"
    elif mismatches <= 4:
        return "3-4/6 mismatches"
    else:
        return "5-6/6 mismatches"


def get_latest_crossmatch_result(transplantation_id):
    """Get the most recent crossmatch result"""
    crossmatch = db["crossmatch_tests"].find_one(
        {"transplantation_id": ObjectId(transplantation_id)},
        sort=[("testDate", -1)]
    )
    if crossmatch:
        return crossmatch.get("result")
    return None


def get_latest_adherence(followup_id):
    """Get the most recent adherence assessment"""
    adherence = db["adherence"].find_one(
        {"followup_id": ObjectId(followup_id)},
        sort=[("date", -1)]
    )
    if adherence:
        return adherence.get("adherencePercent")
    return None


def classify_infections(adverse_events):
    """Classify infection severity"""
    if not adverse_events:
        return "None"
    
    infections = [e for e in adverse_events if e.get("eventType") == "Infection"]
    if not infections:
        return "None"
    
    severe_count = sum(1 for i in infections if i.get("severity") in ["Severe", "Life-threatening"])
    if severe_count > 0:
        return "Major"
    return "Minor"


def calculate_blood_compatibility(recipient_blood, donor_blood):
    """Calculate blood type compatibility"""
    if not recipient_blood or not donor_blood:
        return None
    
    # Define compatibility rules (ABO system)
    # Universal recipient: AB+ can receive from anyone
    # Universal donor: O- can donate to anyone
    
    compatible_map = {
        ("O-", "O-"): "Identical",
        ("O-", "O+"): "Compatible",
        ("O+", "O+"): "Identical",
        ("O+", "O-"): "Compatible",
        ("A-", "A-"): "Identical",
        ("A-", "O-"): "Compatible",
        ("A+", "A+"): "Identical",
        ("A+", "A-"): "Compatible",
        ("A+", "O+"): "Compatible",
        ("A+", "O-"): "Compatible",
        ("B-", "B-"): "Identical",
        ("B-", "O-"): "Compatible",
        ("B+", "B+"): "Identical",
        ("B+", "B-"): "Compatible",
        ("B+", "O+"): "Compatible",
        ("B+", "O-"): "Compatible",
        ("AB-", "AB-"): "Identical",
        ("AB-", "A-"): "Compatible",
        ("AB-", "B-"): "Compatible",
        ("AB-", "O-"): "Compatible",
        ("AB+", "AB+"): "Identical",
        ("AB+", "AB-"): "Compatible",
        ("AB+", "A+"): "Compatible",
        ("AB+", "A-"): "Compatible",
        ("AB+", "B+"): "Compatible",
        ("AB+", "B-"): "Compatible",
        ("AB+", "O+"): "Compatible",
        ("AB+", "O-"): "Compatible",
    }
    
    key = (recipient_blood, donor_blood)
    return compatible_map.get(key, "Incompatible")


# ============================================
# ATTRIBUTE REGISTRY
# ============================================

ATTRIBUTE_REGISTRY = {

    # ============== SCORE 1 ATTRIBUTES ==============

    # DEMOGRAPHICS 
    "recipient_age": lambda ctx: ctx["recipient"]["clinicalData"]["age_at_transplant"] if ctx["recipient"].get("clinicalData") else None,
    "donor_age": lambda ctx: ctx["donor"].get("ageAtDonation"),
    "sex": lambda ctx: ctx["recipient"].get("sex"),
    "foreign_patient": lambda ctx: ctx["recipient"].get("foreignPatient"),

    # MORPHOLOGY 
    "height_cm": lambda ctx: ctx["recipient"].get("heightCm"),
    "weight_kg": lambda ctx: ctx["recipient"].get("weightKg"),
    "bmi": lambda ctx: (
        ctx["recipient"]["weightKg"] /
        ((ctx["recipient"]["heightCm"] / 100) ** 2)
    ) if ctx["recipient"].get("heightCm") and ctx["recipient"].get("weightKg") else None,

    # CLINICAL HISTORY 
    "nephropathy": lambda ctx: ctx["recipient"]["clinicalData"].get("primary_nephropathy") if ctx["recipient"].get("clinicalData") else None,
    "dialysis_type": lambda ctx: ctx["recipient"]["clinicalData"].get("dialysis_type") if ctx["recipient"].get("clinicalData") else None,
    "dialysis_duration": lambda ctx: ctx["recipient"]["clinicalData"].get("dialysis_duration") if ctx["recipient"].get("clinicalData") else None,
    "comorbidities": lambda ctx: ctx["recipient"]["clinicalData"].get("comorbidities") if ctx["recipient"].get("clinicalData") else None,
    "transplant_rank": lambda ctx: ctx["recipient"]["clinicalData"].get("transplant_rank") if ctx["recipient"].get("clinicalData") else None,

    # PRE-TRANSPLANT ASSESSMENT
    "diabetes": lambda ctx: ctx["assessment"].get("diabetes"),
    "hypertension": lambda ctx: ctx["assessment"].get("hypertension"),
    "acc": lambda ctx: ctx["assessment"].get("acc"),
    "hbsag": lambda ctx: ctx["assessment"].get("hbsAg"),
    "anti_hcv": lambda ctx: ctx["assessment"].get("antiHCV"),
    "transfusion_history": lambda ctx: ctx["assessment"].get("transfusion"),
    "eer_modality": lambda ctx: ctx["assessment"].get("eerModality"),
    "previous_transplants": lambda ctx: ctx["assessment"].get("numberOfPreviousTransplants"),
    "etiology_irc": lambda ctx: ctx["assessment"].get("etiologyIRC"),
    "transplant_delay": lambda ctx: ctx["assessment"].get("trDelayMonths"),
    "serum_creatinine": lambda ctx: ctx["assessment"].get("serumCreatinine"),

    # TRANSPLANT CONDITIONS
    "donor_type": lambda ctx: ctx["donor"].get("donorType"),
    "cold_ischemia": lambda ctx: ctx["tx"].get("coldIschemiaHours"),
    "warm_ischemia": lambda ctx: ctx["tx"].get("warmIschemiaMinutes"),
    "transplant_location": lambda ctx: ctx["tx"].get("transplantLocation"),
    "service_origin": lambda ctx: ctx["tx"].get("serviceOrigin"),

    # IMMUNOLOGY
    "blood_compatibility": lambda ctx: calculate_blood_compatibility(
        ctx["recipient"].get("bloodGroup"),
        ctx["donor"].get("bloodGroup")
    ),
    "hla_matching": lambda ctx: calculate_hla_mismatches(
        ctx["recipient"].get("hlaTyping"),
        ctx["donor"].get("hlaTyping")
    ),
    "crossmatch_result": lambda ctx: get_latest_crossmatch_result(ctx["tx"]["_id"]),


    # ============== SCORE 2 ATTRIBUTES ==============

    # FOLLOW UP
    "visit_date": lambda ctx: ctx["followup"].get("visitDate"),
    "post_transplant_day": lambda ctx: ctx["followup"].get("postTransplantDay"),
    "post_transplant_month": lambda ctx: ctx["followup"].get("postTransplantMonth"),
    "visit_type": lambda ctx: ctx["followup"].get("visitType"),
    "clinical_status": lambda ctx: ctx["followup"].get("clinicalStatus"),
    "nephropathy_recurrence": lambda ctx: ctx["followup"].get("nephropathyRecurrence"),
    "followup_comment": lambda ctx: ctx["followup"].get("comment"),

    # BIOLOGICAL MEASUREMENTS
    "bio_date": lambda ctx: ctx["biological"][0].get("date") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,
    "creatinine": lambda ctx: ctx["biological"][0].get("creatinine") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,
    "urea": lambda ctx: ctx["biological"][0].get("urea") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,
    "gfr": lambda ctx: ctx["biological"][0].get("gfr") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,
    "hemoglobin": lambda ctx: ctx["biological"][0].get("hemoglobin") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,
    "crp": lambda ctx: ctx["biological"][0].get("crp") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,
    "tsh": lambda ctx: ctx["biological"][0].get("tsh") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,
    "proteinuria": lambda ctx: ctx["biological"][0].get("proteinuria") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,
    "other_biomarker_1": lambda ctx: ctx["biological"][0].get("otherBioMarker1") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,
    "other_biomarker_2": lambda ctx: ctx["biological"][0].get("otherBioMarker2") if ctx.get("biological") and len(ctx["biological"]) > 0 else None,

    # ADVERSE EVENTS
    "has_adverse_event": lambda ctx: len(ctx.get("adverse_events", [])) > 0,
    "adverse_event_count": lambda ctx: len(ctx.get("adverse_events", [])),
    "adverse_event_types": lambda ctx: [e.get("eventType") for e in ctx.get("adverse_events", [])],
    "max_severity": lambda ctx: max([e.get("severity", 0) for e in ctx.get("adverse_events", [])], default=None) if ctx.get("adverse_events") else None,
    
    # INFECTIONS (for SCORE 2)
    "infections": lambda ctx: classify_infections(ctx.get("adverse_events", [])),

    # IMMUNOLOGICAL MARKERS
    "immun_marker_types": lambda ctx: [m.get("markerType") for m in ctx.get("immunological", [])],
    "immun_marker_values": lambda ctx: [m.get("value") for m in ctx.get("immunological", [])],

    # IMMUNOSUPPRESSION REGIMEN
    "tacrolimus": lambda ctx: ctx.get("regimen", {}).get("tacrolimus") if ctx.get("regimen") else None,
    "ciclosporine": lambda ctx: ctx.get("regimen", {}).get("ciclosporine") if ctx.get("regimen") else None,
    "mmf": lambda ctx: ctx.get("regimen", {}).get("mmf") if ctx.get("regimen") else None,
    "azathioprine": lambda ctx: ctx.get("regimen", {}).get("azathioprine") if ctx.get("regimen") else None,
    "sirolimus": lambda ctx: ctx.get("regimen", {}).get("sirolimus") if ctx.get("regimen") else None,
    "corticosteroids": lambda ctx: ctx.get("regimen", {}).get("corticosteroids") if ctx.get("regimen") else None,

    # ADHERENCE
    "adherence_percentage": lambda ctx: get_latest_adherence(ctx["followup"]["_id"]),

    # REJECTION EPISODES
    "rejection_episodes": lambda ctx: len(ctx.get("rejection_episodes", [])) if ctx.get("rejection_episodes") else 0,

    # OUTCOME
    "alive_with_graft": lambda ctx: ctx["outcome"].get("aliveWithFunctioningGraft") if ctx.get("outcome") else None,
    "return_to_dialysis": lambda ctx: ctx["outcome"].get("returnToDialysis") if ctx.get("outcome") else None,
    "death_with_graft": lambda ctx: ctx["outcome"].get("deathWithFunctioningGraft") if ctx.get("outcome") else None,
    "lost_to_followup": lambda ctx: ctx["outcome"].get("lostToFollowUp") if ctx.get("outcome") else None,
    "delayed_graft_function": lambda ctx: ctx["outcome"].get("delayedGraftFunction") if ctx.get("outcome") else None,


    # ============== SCORE 3 ATTRIBUTES ==============

    # FOLLOW-UP SUMMARY
    "followup_count": lambda ctx: len(ctx.get("followups", [])),
    "adverse_event_rate": lambda ctx: len(ctx.get("adverse_events", [])) / len(ctx.get("followups", [])) if ctx.get("followups") and len(ctx["followups"]) > 0 else 0,

    # BIOLOGICAL TRENDS
    "mean_creatinine": lambda ctx: sum(b.get("creatinine", 0) for b in ctx.get("biological", []) if b.get("creatinine")) / len([b for b in ctx.get("biological", []) if b.get("creatinine")]) if ctx.get("biological") and any(b.get("creatinine") for b in ctx["biological"]) else None,
    "max_creatinine": lambda ctx: max(b.get("creatinine", 0) for b in ctx.get("biological", [])) if ctx.get("biological") and any(b.get("creatinine") for b in ctx["biological"]) else None,
    "min_gfr": lambda ctx: min(b.get("gfr", 999) for b in ctx.get("biological", []) if b.get("gfr")) if ctx.get("biological") and any(b.get("gfr") for b in ctx["biological"]) else None,
    "creatinine_trend": lambda ctx: "improving" if len(ctx.get("biological", [])) > 1 and ctx["biological"][-1].get("creatinine", 0) < ctx["biological"][0].get("creatinine", 0) else "stable",
    
    # GRAFT STATUS
    "graft_loss": lambda ctx: ctx.get("outcome", {}).get("returnToDialysis", False) if ctx.get("outcome") else False,
    "patient_survival": lambda ctx: not ctx.get("outcome", {}).get("deathWithFunctioningGraft", False) if ctx.get("outcome") else True,

    # VITAL SIGNS
    "urine_output": lambda ctx: ctx.get("vitals", [{}])[-1].get("urineOutputMl") if ctx.get("vitals") and len(ctx.get("vitals", [])) > 0 else None,
    "temperature": lambda ctx: ctx.get("vitals", [{}])[-1].get("temperature") if ctx.get("vitals") and len(ctx.get("vitals", [])) > 0 else None,
    "blood_pressure": lambda ctx: ctx.get("vitals", [{}])[-1].get("bloodPressure") if ctx.get("vitals") and len(ctx.get("vitals", [])) > 0 else None,
    "heart_rate": lambda ctx: ctx.get("vitals", [{}])[-1].get("heartRate") if ctx.get("vitals") and len(ctx.get("vitals", [])) > 0 else None,
    "oxygen_saturation": lambda ctx: ctx.get("vitals", [{}])[-1].get("oxygenSaturation") if ctx.get("vitals") and len(ctx.get("vitals", [])) > 0 else None,
    "mental_status": lambda ctx: ctx.get("vitals", [{}])[-1].get("mentalStatus") if ctx.get("vitals") and len(ctx.get("vitals", [])) > 0 else None,
    "graft_ultrasound": lambda ctx: ctx.get("vitals", [{}])[-1].get("graftUltraSound") if ctx.get("vitals") and len(ctx.get("vitals", [])) > 0 else None,
}