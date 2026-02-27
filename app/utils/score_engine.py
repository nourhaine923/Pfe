from bson import ObjectId
from app.database import db
from app.utils.attribute_registry import ATTRIBUTE_REGISTRY
from app.utils.attribute_normalizer import normalize_value


transplantations = db["transplantations"]
patients = db["patients"]
barems = db["barems"]


def extract_score1_attributes(transplantation_id: str):

    tx = transplantations.find_one({"_id": ObjectId(transplantation_id)})
    recipient = patients.find_one({"_id": ObjectId(tx["recipient_id"])})
    donor = patients.find_one({"_id": ObjectId(tx["donor_id"])})

    assessment = tx.get("preTransplantAssessment", {})

    # context shared across registry
    ctx = {
        "tx": tx,
        "recipient": recipient,
        "donor": donor,
        "assessment": assessment
    }

    # discover which attributes doctors configured
    keys = barems.distinct("key", {"score": "SCORE_1"})

    attributes = {}

    for key in keys:

        resolver = ATTRIBUTE_REGISTRY.get(key)
        if not resolver:
            continue  # unknown attribute (safe)

        raw_value = resolver(ctx)
        normalized = normalize_value(key, raw_value)

        attributes[key] = normalized

    return attributes