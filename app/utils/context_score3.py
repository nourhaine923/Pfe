from bson import ObjectId
from app.database import db


def build_score3_context(transplantation_id: str):
    """
    Build context dictionary for SCORE 3 calculation
    Includes transplantation, all follow-ups, biological data across time,
    adverse events, immunological markers, vitals, and outcome
    """
    tx = db["transplantations"].find_one({"_id": ObjectId(transplantation_id)})
    if not tx:
        raise ValueError("Transplantation not found")

    # Get all follow-ups for this transplantation
    followups = list(db["followups"].find({
        "transplantation_id": ObjectId(transplantation_id)
    }).sort("visitDate", 1))  # Sort by date ascending

    biological = []
    adverse = []
    immunological = []
    vitals = []

    # Collect data from all follow-ups
    for f in followups:
        fid = f["_id"]
        
        biological.extend(list(db["biological_measurements"].find({"followup_id": fid})))
        adverse.extend(list(db["adverse_events"].find({"followup_id": fid})))
        immunological.extend(list(db["immunological_markers"].find({"followup_id": fid})))
        
        vital = db["vitals"].find_one({"followup_id": fid})
        if vital:
            vitals.append(vital)

    # Get outcome
    outcome = db["outcomes"].find_one({"transplantation_id": ObjectId(transplantation_id)})

    # Get recipient
    recipient = db["patients"].find_one({"_id": ObjectId(tx["recipient_id"])})

    return {
        "tx": tx,
        "followups": followups,
        "biological": biological,
        "adverse_events": adverse,
        "immunological": immunological,
        "vitals": vitals,
        "outcome": outcome,
        "recipient": recipient
    }