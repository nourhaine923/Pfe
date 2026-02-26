from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime

from app.database import db
from app.utils.score_engine import extract_score1_attributes


# Router definition (must be before endpoints)
router = APIRouter(prefix="/scores", tags=["Scores"])


# Collections
score_collection = db["scores"]
barem_collection = db["barems"]
transplantation_collection = db["transplantations"]


@router.post("/calculate-score-1/{transplantation_id}")
def calculate_score_1(transplantation_id: str):
    """
    Calculate SCORE_1 using:
    - Clinical data already stored in MongoDB
    - Barem rules (editable by doctors)

    This endpoint DOES NOT create an attributes collection.
    Attributes are computed dynamically as required by the UML.
    """

    # -----------------------------
    # 1️⃣ Validate transplantation exists
    # -----------------------------
    transplantation = transplantation_collection.find_one(
        {"_id": ObjectId(transplantation_id)}
    )

    if not transplantation:
        raise HTTPException(status_code=404, detail="Transplantation not found")

    # -----------------------------
    # 2️⃣ Extract ALL attributes dynamically
    # -----------------------------
    try:
        attributes = extract_score1_attributes(transplantation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # -----------------------------
    # 3️⃣ Apply Barem rules
    # -----------------------------
    total_score = 0
    matched_rules = []

    for attr_key, attr_value in attributes.items():

        rule = barem_collection.find_one({
            "score": "SCORE_1",
            "key": attr_key,
            "value": attr_value
        })

        if rule:
            total_score += rule["impact"]

            matched_rules.append({
                "attribute": attr_key,
                "value": attr_value,
                "impact": rule["impact"]
            })

    # -----------------------------
    # 4️⃣ Store computed score
    # -----------------------------
    score_document = {
        "scoreType": "SCORE_1",
        "value": total_score,
        "transplantation_id": ObjectId(transplantation_id),
        "calculatedAt": datetime.utcnow()
    }

    score_collection.insert_one(score_document)

    # -----------------------------
    # 5️⃣ Return result (without storing attributes)
    # -----------------------------
    return {
        "score": total_score,
        "used_attributes": matched_rules
    }