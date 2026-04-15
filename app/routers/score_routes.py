from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime

from app.database import db
from app.utils.attribute_registry import ATTRIBUTE_REGISTRY
from app.utils.rule_engine import compute_attribute_score
from app.utils.context_score2 import build_score2_context
from app.utils.context_score3 import build_score3_context
from app.auth.dependencies import nephrologist_or_admin
from fastapi import Depends


router = APIRouter(prefix="/scores", tags=["Scores"])

barem_collection = db["barems"]
transplant_collection = db["transplantations"]
patient_collection = db["patients"]
score_collection = db["scores"]
followup_collection = db["followups"]  # <-- ADDED THIS LINE


# --------------------------------------------------
# Calculate and STORE SCORE_1
# --------------------------------------------------
@router.post("/calculate-score-1/{transplantation_id}", dependencies=[Depends(nephrologist_or_admin)])
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


# score history for a transplantation
@router.get("/history/{transplantation_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_score_history(transplantation_id: str):
    """Get all scores for a transplantation"""
    try:
        tx_id = ObjectId(transplantation_id)
    except Exception as e:
        print(f"Invalid ObjectId: {transplantation_id}, Error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid transplantation_id format: {transplantation_id}")
    
    scores = []
    
    # Get SCORE_1 and SCORE_3 scores directly linked to transplantation
    try:
        score_scores = list(score_collection.find({
            "transplantation_id": tx_id
        }).sort("calculated_at", -1))
        scores.extend(score_scores)
        print(f"Found {len(score_scores)} scores for transplantation {transplantation_id}")
    except Exception as e:
        print(f"Error fetching transplantation scores: {e}")
    
    # Also get SCORE_2 scores for this transplantation (from follow-ups)
    try:
        followups = list(followup_collection.find({"transplantation_id": tx_id}))
        followup_ids = [f["_id"] for f in followups]
        
        if followup_ids:
            score2_scores = list(score_collection.find({
                "followup_id": {"$in": followup_ids}
            }).sort("calculated_at", -1))
            scores.extend(score2_scores)
            print(f"Found {len(score2_scores)} SCORE_2 scores from follow-ups")
    except Exception as e:
        print(f"Error fetching SCORE_2 scores: {e}")

    # Serialize for JSON response
    serialized_scores = []
    for score in scores:
        try:
            serialized = {
                "_id": str(score["_id"]),
                "score_type": score.get("score_type"),
                "value": score.get("value", 0),
                "calculated_at": score.get("calculated_at").isoformat() if score.get("calculated_at") else None,
                "details": score.get("details", [])
            }
            if score.get("transplantation_id"):
                serialized["transplantation_id"] = str(score["transplantation_id"])
            if score.get("followup_id"):
                serialized["followup_id"] = str(score["followup_id"])
            serialized_scores.append(serialized)
        except Exception as e:
            print(f"Error serializing score: {e}")
            continue

    return serialized_scores


# Get Latest Score for a Transplantation
@router.get("/latest/{transplantation_id}", dependencies=[Depends(nephrologist_or_admin)])
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
@router.post("/calculate-score-2/{followup_id}", dependencies=[Depends(nephrologist_or_admin)])
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


# -----------------------------------------------
# SCORE 3
# -----------------------------------------------
@router.post("/calculate-score-3/{transplantation_id}", dependencies=[Depends(nephrologist_or_admin)])
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