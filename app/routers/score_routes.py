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
followup_collection = db["followups"]  


def normalize_score(raw_score, min_possible=-40, max_possible=60):
    """
    Normalize score to 0-100 range
    raw_score: calculated points (can be negative)
    min_possible: minimum possible raw score
    max_possible: maximum possible raw score
    """
    # Clamp to possible range
    clamped = max(min_possible, min(max_possible, raw_score))
    # Convert to 0-100 scale
    normalized = ((clamped - min_possible) / (max_possible - min_possible)) * 100
    return int(round(normalized))


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
        except Exception as e:
            print(f"Error resolving {key}: {e}")
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

    # Normalize to 0-100 scale
    normalized_score = normalize_score(total_score, min_possible=-40, max_possible=60)

    # 6️⃣ Store snapshot in Mongo
    score_doc = {
        "transplantation_id": ObjectId(transplantation_id),
        "score_type": "SCORE_1",
        "value": normalized_score,
        "calculated_at": datetime.utcnow(),
        "details": used_attributes
    }

    score_collection.insert_one(score_doc)

    # 7️⃣ Return result
    return {
        "score": normalized_score,
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

    # Normalize to 0-100 scale
    normalized_score = normalize_score(total_score, min_possible=-40, max_possible=60)

    snapshot = {
        "score_type": "SCORE_2",
        "value": normalized_score,
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


# --------------------------------------------------
# CALCULATE SCORE 3 (Success Probability)
# HIGHER score = BETTER outcome (starts at 100, subtracts for problems)
# --------------------------------------------------
@router.post("/calculate-score-3/{transplantation_id}", dependencies=[Depends(nephrologist_or_admin)])
def calculate_score_3(transplantation_id: str):
    try:
        context = build_score3_context(transplantation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    barems = list(barem_collection.find({"score": "SCORE_3"}))

    if not barems:
        raise HTTPException(status_code=404, detail="No SCORE_3 barems defined")

    # Start with MAX score (100) and SUBTRACT for problems
    total_score = 100
    details = []

    for barem in barems:
        key = barem["key"]

        if key not in ATTRIBUTE_REGISTRY:
            print(f"Attribute {key} not found in registry")
            continue

        try:
            value = ATTRIBUTE_REGISTRY[key](context)
            print(f"SCORE_3 - {key}: {value}")
        except Exception as e:
            print(f"Error getting {key}: {e}")
            continue

        if value is None:
            print(f"SCORE_3 - {key} returned None")
            continue

        # Calculate emergency impact (positive = bad)
        impact = compute_attribute_score(value, barem)
        print(f"SCORE_3 - {key} raw impact: {impact}")

        if impact is not None:
            # SUBTRACT the impact from the score
            total_score -= impact
            details.append({
                "attribute": key,
                "value": value,
                "impact": -impact  # Store as negative for display
            })

    # Ensure score stays within 0-100 range
    normalized_score = max(0, min(100, total_score))

    snapshot = {
        "score_type": "SCORE_3",
        "value": normalized_score,
        "details": details,
        "transplantation_id": ObjectId(transplantation_id),
        "calculated_at": datetime.utcnow()
    }

    result = score_collection.insert_one(snapshot)

    snapshot["_id"] = str(result.inserted_id)
    snapshot["transplantation_id"] = str(snapshot["transplantation_id"])
    snapshot["calculated_at"] = snapshot["calculated_at"].isoformat()

    return snapshot


@router.get("/score3-debug/{transplantation_id}", dependencies=[Depends(nephrologist_or_admin)])
def score3_debug(transplantation_id: str):
    """Debug endpoint to check SCORE 3 data availability"""
    try:
        context = build_score3_context(transplantation_id)
    except ValueError as e:
        return {"error": str(e)}
    
    # Check each attribute
    attributes_to_check = [
        "followup_count",
        "adverse_event_rate", 
        "mean_creatinine",
        "max_creatinine",
        "min_gfr",
        "creatinine_trend",
        "graft_loss",
        "patient_survival",
        "urine_output",
        "temperature",
        "blood_pressure",
        "heart_rate",
        "oxygen_saturation",
        "mental_status",
        "graft_ultrasound"
    ]
    
    results = {}
    for attr in attributes_to_check:
        if attr in ATTRIBUTE_REGISTRY:
            try:
                value = ATTRIBUTE_REGISTRY[attr](context)
                results[attr] = value
            except Exception as e:
                results[attr] = f"Error: {str(e)}"
        else:
            results[attr] = "Not in registry"
    
    return {
        "followups_count": len(context.get("followups", [])),
        "biological_count": len(context.get("biological", [])),
        "vitals_count": len(context.get("vitals", [])),
        "adverse_events_count": len(context.get("adverse_events", [])),
        "has_outcome": context.get("outcome") is not None,
        "attribute_values": results
    }