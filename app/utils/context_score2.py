# app/utils/context_score2.py
from bson import ObjectId
from app.database import db


def build_score2_context(followup_id: str):
    """
    Build context dictionary for SCORE 2 calculation
    Includes follow-up, transplantation, recipient, biological data,
    adverse events, immunosuppression regimen, outcome, immunological markers,
    and vital signs
    """
    followups = db["followups"]
    transplantations = db["transplantations"]
    patients = db["patients"]
    biological = db["biological_measurements"]
    adverse = db["adverse_events"]
    regimens = db["immunosuppression_regimens"]
    outcomes = db["outcomes"]
    immunological = db["immunological_markers"]
    vitals = db["vitals"]

    # Get follow-up
    followup = followups.find_one({"_id": ObjectId(followup_id)})
    if not followup:
        raise ValueError("FollowUp not found")

    # Get transplantation
    tx = transplantations.find_one({"_id": ObjectId(followup["transplantation_id"])})
    if not tx:
        raise ValueError("Transplantation not found")

    # Get recipient
    recipient = patients.find_one({"_id": ObjectId(tx["recipient_id"])})

    # Get immunosuppression regimen - SAFELY handle missing field
    regimen = None
    # First try to get from followup's direct reference
    if followup.get("immunosuppression_regimen_id"):
        try:
            regimen = regimens.find_one({"_id": ObjectId(followup["immunosuppression_regimen_id"])})
        except:
            regimen = None
    
    # If not found, try to find by followup_id in regimens collection
    if not regimen:
        regimen = regimens.find_one({"followup_id": ObjectId(followup_id)})

    # Get biological measurements
    biological_list = list(biological.find({"followup_id": ObjectId(followup_id)}))

    # Get adverse events
    adverse_list = list(adverse.find({"followup_id": ObjectId(followup_id)}))

    # Get immunological markers
    immunological_list = list(immunological.find({"followup_id": ObjectId(followup_id)}))

    # Get vital signs
    vital_signs = vitals.find_one({"followup_id": ObjectId(followup_id)})

    # Get outcome
    outcome = outcomes.find_one({"transplantation_id": ObjectId(tx["_id"])})

    return {
        "followup": followup,
        "tx": tx,
        "recipient": recipient,
        "biological": biological_list,
        "adverse_events": adverse_list,
        "regimen": regimen,
        "outcome": outcome,
        "immunological": immunological_list,
        "vital_signs": vital_signs
    }