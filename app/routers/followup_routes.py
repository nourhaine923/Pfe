from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from datetime import datetime, date
from fastapi import Body

from app.database import db
from app.schemas.followup import FollowUp
from app.auth.dependencies import doctor_or_admin
from fastapi import Depends

router = APIRouter(prefix="/followups", tags=["FollowUps"])

followup_collection = db["followups"]
transplantation_collection = db["transplantations"]
def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(item) for item in obj]

    if isinstance(obj, dict):
        return {key: convert_dates(value) for key, value in obj.items()}

    if isinstance(obj, datetime):
        return obj

    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)

    return obj

# Create a new follow-up
@router.post("/", dependencies=[Depends(doctor_or_admin)])
def create_followup(followup: FollowUp):
    data = convert_dates(followup.dict())

    try:
        transplantation_id = ObjectId(data["transplantation_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid transplantation_id")

    # Verify transplantation exists
    if not transplantation_collection.find_one({"_id": transplantation_id}):
        raise HTTPException(status_code=404, detail="Transplantation not found")

    data["transplantation_id"] = transplantation_id

    result = followup_collection.insert_one(data)

    return {
        "message": "FollowUp created successfully",
        "id": str(result.inserted_id)
    }

# Get all follow-ups
@router.get("/", response_model=List[dict], dependencies=[Depends(doctor_or_admin)])
def get_followups():
    followups = list(followup_collection.find())

    for f in followups:
        f["_id"] = str(f["_id"])
        f["transplantation_id"] = str(f["transplantation_id"])

    return followups
# Get a follow-up by transplantation ID
@router.get("/by-transplantation/{transplantation_id}", dependencies=[Depends(doctor_or_admin)])
def get_followups_by_transplantation(transplantation_id: str):
    try:
        obj_id = ObjectId(transplantation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    followups = list(followup_collection.find({"transplantation_id": obj_id}))

    for f in followups:
        f["_id"] = str(f["_id"])
        f["transplantation_id"] = str(f["transplantation_id"])

    return followups

# Update a follow-up by ID
@router.patch("/{followup_id}", dependencies=[Depends(doctor_or_admin)])
def partial_update_followup(followup_id: str, updates: dict = Body(...)):
    obj_id = ObjectId(followup_id)

    updates = convert_dates(updates)

    if "transplantation_id" in updates:
        updates["transplantation_id"] = ObjectId(updates["transplantation_id"])

    result = followup_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="FollowUp not found")

    return {"message": "FollowUp updated partially"}



@router.delete("/{followup_id}", dependencies=[Depends(doctor_or_admin)])
def delete_followup(followup_id: str):
    result = followup_collection.delete_one({"_id": ObjectId(followup_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Treatment not found")

    return {"message": "Treatment deleted"}


