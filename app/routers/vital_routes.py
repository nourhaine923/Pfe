from fastapi import APIRouter, HTTPException, Body
from bson import ObjectId
from datetime import datetime, date
from typing import List

from app.database import db
from app.schemas.vital_signs import VitalSigns

router = APIRouter(prefix="/vitals", tags=["Vital Signs"])

vital_collection = db["vitals"]
followup_collection = db["followups"]
def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)
    return obj
# Create a new vital signs record
@router.post("/")
def create_vital_signs(vital: VitalSigns):
    data = convert_dates(vital.dict())

    try:
        followup_id = ObjectId(data["followup_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid followup_id")

    if not followup_collection.find_one({"_id": followup_id}):
        raise HTTPException(status_code=404, detail="FollowUp not found")

    data["followup_id"] = followup_id

    result = vital_collection.insert_one(data)

    return {
        "message": "Vital signs recorded",
        "id": str(result.inserted_id)
    }

# Get all vital signs records for a follow-up
@router.get("/by-followup/{followup_id}", response_model=List[dict])
def get_vitals(followup_id: str):
    obj_id = ObjectId(followup_id)

    vitals = list(vital_collection.find({"followup_id": obj_id}))

    for v in vitals:
        v["_id"] = str(v["_id"])
        v["followup_id"] = str(v["followup_id"])

    return vitals

# Update a vital signs record
@router.patch("/{vital_id}")
def update_vitals(vital_id: str, updates: dict = Body(...)):
    obj_id = ObjectId(vital_id)

    updates = convert_dates(updates)

    if "followup_id" in updates:
        updates["followup_id"] = ObjectId(updates["followup_id"])

    result = vital_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Vital record not found")

    return {"message": "Vital signs updated"}

#delete a vital signs record
@router.delete("/{vital_id}")
def delete_vitals(vital_id: str):
    result = vital_collection.delete_one({"_id": ObjectId(vital_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vital record not found")

    return {"message": "Vital signs deleted"}

