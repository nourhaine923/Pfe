from fastapi import APIRouter, HTTPException, Body
from bson import ObjectId
from datetime import datetime, date
from typing import List

from app.database import db
from app.schemas.adherence_assessment import AdherenceAssessment

router = APIRouter(prefix="/adherence", tags=["Adherence Assessments"])

adherence_collection = db["adherence"]
followup_collection = db["followups"]
def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)
    return obj
# Create a new adherence assessment
@router.post("/")
def create_adherence(assessment: AdherenceAssessment):
    data = convert_dates(assessment.dict())

    try:
        followup_id = ObjectId(data["followup_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid followup_id")

    if not followup_collection.find_one({"_id": followup_id}):
        raise HTTPException(status_code=404, detail="FollowUp not found")

    data["followup_id"] = followup_id

    result = adherence_collection.insert_one(data)

    return {
        "message": "Adherence assessment recorded",
        "id": str(result.inserted_id)
    }

# Get all adherence assessments for a follow-up
@router.get("/by-followup/{followup_id}", response_model=List[dict])
def get_adherence(followup_id: str):
    obj_id = ObjectId(followup_id)

    assessments = list(adherence_collection.find({"followup_id": obj_id}))

    for a in assessments:
        a["_id"] = str(a["_id"])
        a["followup_id"] = str(a["followup_id"])

    return assessments

# Update an adherence assessment
@router.patch("/{assessment_id}")
def update_adherence(assessment_id: str, updates: dict = Body(...)):
    obj_id = ObjectId(assessment_id)

    updates = convert_dates(updates)

    if "followup_id" in updates:
        updates["followup_id"] = ObjectId(updates["followup_id"])

    result = adherence_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {"message": "Adherence updated"}

# Delete an adherence assessment
@router.delete("/{assessment_id}")
def delete_adherence(assessment_id: str):
    result = adherence_collection.delete_one({"_id": ObjectId(assessment_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {"message": "Adherence deleted"}
