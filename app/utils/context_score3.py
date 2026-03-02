from bson import ObjectId
from app.database import db


def build_score3_context(transplantation_id: str):

    tx = db["transplantations"].find_one({"_id": ObjectId(transplantation_id)})
    if not tx:
        raise ValueError("Transplantation not found")

    followups = list(db["followups"].find({
        "transplantation_id": ObjectId(transplantation_id)
    }))

    biological = []
    adverse = []

    for f in followups:
        fid = f["_id"]

        biological += list(db["biological_measurements"].find({"followup_id": fid}))
        adverse += list(db["adverse_events"].find({"followup_id": fid}))

    outcome = db["outcomes"].find_one({"transplantation_id": ObjectId(transplantation_id)})

    return {
        "tx": tx,
        "followups": followups,
        "biological": biological,
        "adverse_events": adverse,
        "outcome": outcome
    }