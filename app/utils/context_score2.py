from bson import ObjectId
from app.database import db


def build_score2_context(followup_id: str):

    followups = db["followups"]
    transplantations = db["transplantations"]
    patients = db["patients"]
    biological = db["biological_measurements"]
    adverse = db["adverse_events"]
    regimens = db["immunosuppression_regimens"]
    outcomes = db["outcomes"]

    followup = followups.find_one({"_id": ObjectId(followup_id)})
    if not followup:
        raise ValueError("FollowUp not found")

    tx = transplantations.find_one({"_id": ObjectId(followup["transplantation_id"])})
    if not tx:
        raise ValueError("Transplantation not found")

    recipient = patients.find_one({"_id": ObjectId(tx["recipient_id"])})

    regimen = regimens.find_one({"_id": ObjectId(followup["immunosuppression_regimen_id"])})

    biological_list = list(biological.find({"followup_id": ObjectId(followup_id)}))

    adverse_list = list(adverse.find({"followup_id": ObjectId(followup_id)}))

    outcome = outcomes.find_one({"transplantation_id": ObjectId(tx["_id"])})

    return {
        "followup": followup,
        "tx": tx,
        "recipient": recipient,
        "biological": biological_list,
        "adverse_events": adverse_list,
        "regimen": regimen,
        "outcome": outcome
    }