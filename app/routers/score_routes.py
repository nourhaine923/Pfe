from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime

from app.database import db
from app.utils.attribute_registry import ATTRIBUTE_REGISTRY
from app.utils.rule_engine import compute_attribute_score
from app.utils.context_score2 import build_score2_context
from app.utils.context_score3 import build_score3_context


router = APIRouter(prefix="/scores", tags=["Scores"])

barem_collection = db["barems"]
transplant_collection = db["transplantations"]
patient_collection = db["patients"]
score_collection = db["scores"]


# --------------------------------------------------
# Calculate and STORE SCORE_1
# --------------------------------------------------
@router.post("/calculate-score-1/{transplantation_id}")
def calculate_score_1(transplantation_id: str):

    # 1️⃣ Load transplantation
    tx = transplant_collection.find_one({"_id": ObjectId(transplantation_id)})
    if not tx:
        raise HTTPException(status_code=404, detail="Transplantation not found")

    # 2️⃣ Load recipient & donor
    recipient = patient_collection.find_one(
        {"_id": ObjectId(tx["recipient_id"])}
    )

    donor = patient_collection.find_one(
        {"_id": ObjectId(tx["donor_id"])}
    )

    if not recipient or not donor:
        raise HTTPException(status_code=404, detail="Recipient or Donor not found")

    # 3️⃣ Build context
    context = {
        "tx": tx,
        "recipient": recipient,
        "donor": donor,
        "assessment": tx.get("preTransplantAssessment", {})
    }

    # 4️⃣ Load SCORE_1 rules
    barems = list(barem_collection.find({"score": "SCORE_1"}))

    if not barems:
        raise HTTPException(status_code=400, detail="No SCORE_1 rules defined")

    total_score = 0
    used_attributes = []

    # 5️⃣ Evaluate dynamically
    for barem in barems:

        key = barem["key"]
        resolver = ATTRIBUTE_REGISTRY.get(key)

        if not resolver:
            continue

        try:
            raw_value = resolver(context)
        except Exception:
            continue

        if raw_value is None:
            continue

        impact = compute_attribute_score(raw_value, barem)

        total_score += impact

        used_attributes.append({
            "attribute": key,
            "value": raw_value,
            "impact": impact
        })

    # 6️⃣ Store snapshot in Mongo
    score_doc = {
        "transplantation_id": ObjectId(transplantation_id),
        "score_type": "SCORE_1",
        "value": total_score,
        "calculated_at": datetime.utcnow(),
        "details": used_attributes
    }

    score_collection.insert_one(score_doc)

    # 7️⃣ Return result
    return {
        "score": total_score,
        "used_attributes": used_attributes
    }

# Get Score History for a Transplantation
@router.get("/history/{transplantation_id}")
def get_score_history(transplantation_id: str):

    scores = list(score_collection.find({
        "transplantation_id": ObjectId(transplantation_id)
    }).sort("calculated_at", -1))  # newest first

    if not scores:
        return []

    # Serialize ObjectId + datetime
    for score in scores:
        score["_id"] = str(score["_id"])
        score["transplantation_id"] = str(score["transplantation_id"])
        score["calculated_at"] = score["calculated_at"].isoformat()

    return scores

# Get Latest Score for a Transplantation
@router.get("/latest/{transplantation_id}")
def get_latest_score(transplantation_id: str):

    latest = score_collection.find_one(
        {"transplantation_id": ObjectId(transplantation_id)},
        sort=[("calculated_at", -1)]
    )

    if not latest:
        raise HTTPException(status_code=404, detail="No score found")

    # Serialize fields
    latest["_id"] = str(latest["_id"])
    latest["transplantation_id"] = str(latest["transplantation_id"])
    latest["calculated_at"] = latest["calculated_at"].isoformat()

    return latest



# --------------------------------------------------
# CALCULATE SCORE 2 (Per FollowUp)
# --------------------------------------------------
@router.post("/calculate-score-2/{followup_id}")
def calculate_score_2(followup_id: str):

    try:
        context = build_score2_context(followup_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    barems = list(barem_collection.find({"score": "SCORE_2"}))

    if not barems:
        raise HTTPException(status_code=404, detail="No SCORE_2 barems defined")

    total_score = 0
    details = []

    for barem in barems:

        key = barem["key"]

        # Skip if attribute not in registry
        if key not in ATTRIBUTE_REGISTRY:
            continue

        # Extract attribute value
        value = ATTRIBUTE_REGISTRY[key](context)

        if value is None:
            continue

        # Compute score for that attribute
        impact = compute_attribute_score(value, barem)

        if impact is not None:
            total_score += impact

            details.append({
                "attribute": key,
                "value": value,
                "impact": impact
            })

    snapshot = {
        "score_type": "SCORE_2",
        "value": total_score,
        "details": details,
        "followup_id": ObjectId(followup_id),
        "transplantation_id": ObjectId(context["tx"]["_id"]),
        "calculated_at": datetime.utcnow()
    }

    result = score_collection.insert_one(snapshot)

    # Serialize
    snapshot["_id"] = str(result.inserted_id)
    snapshot["followup_id"] = str(snapshot["followup_id"])
    snapshot["transplantation_id"] = str(snapshot["transplantation_id"])
    snapshot["calculated_at"] = snapshot["calculated_at"].isoformat()

    return snapshot
#-----------------------------------------------
#score 3
#-----------------------------------------------
@router.post("/calculate-score-3/{transplantation_id}")
def calculate_score_3(transplantation_id: str):

    context = build_score3_context(transplantation_id)

    barems = list(barem_collection.find({"score": "SCORE_3"}))

    total_score = 0
    details = []

    for barem in barems:
        key = barem["key"]

        if key not in ATTRIBUTE_REGISTRY:
            continue

        value = ATTRIBUTE_REGISTRY[key](context)

        impact = compute_attribute_score(value, barem)

        if impact is not None:
            total_score += impact
            details.append({
                "attribute": key,
                "value": value,
                "impact": impact
            })

    snapshot = {
        "score_type": "SCORE_3",
        "value": total_score,
        "details": details,
        "transplantation_id": ObjectId(transplantation_id),
        "calculated_at": datetime.utcnow()
    }

    result = score_collection.insert_one(snapshot)

    # SERIALIZE BEFORE RETURNING
    snapshot["_id"] = str(result.inserted_id)
    snapshot["transplantation_id"] = str(snapshot["transplantation_id"])
    snapshot["calculated_at"] = snapshot["calculated_at"].isoformat()

    return snapshot