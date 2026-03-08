from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, date
from typing import List
from fastapi import Body

from app.database import db
from app.schemas.outcome import Outcome
from app.auth.dependencies import doctor_or_admin
from fastapi import Depends

router = APIRouter(prefix="/outcomes", tags=["Outcomes"])

outcome_collection = db["outcomes"]
transplantation_collection = db["transplantations"]

def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)
    return obj

# Create a new outcome
@router.post("/", dependencies=[Depends(doctor_or_admin)])
def create_outcome(outcome: Outcome):
    data = convert_dates(outcome.dict())

    try:
        transplantation_id = ObjectId(data["transplantation_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid transplantation_id")

    # Ensure transplantation exists
    if not transplantation_collection.find_one({"_id": transplantation_id}):
        raise HTTPException(status_code=404, detail="Transplantation not found")

    data["transplantation_id"] = transplantation_id

    result = outcome_collection.insert_one(data)

    return {
        "message": "Outcome recorded successfully",
        "id": str(result.inserted_id)
    }

# Get outcomes by transplantation ID
@router.get("/by-transplantation/{transplantation_id}", dependencies=[Depends(doctor_or_admin)])
def get_outcome(transplantation_id: str):
    try:
        obj_id = ObjectId(transplantation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    outcome = outcome_collection.find_one({"transplantation_id": obj_id})

    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")

    outcome["_id"] = str(outcome["_id"])
    outcome["transplantation_id"] = str(outcome["transplantation_id"])

    return outcome

# Update an outcome by ID
@router.patch("/{outcome_id}", dependencies=[Depends(doctor_or_admin)])
def partial_update_outcome(outcome_id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(outcome_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    updates = convert_dates(updates)

    # If transplantation_id is being changed, convert it
    if "transplantation_id" in updates:
        try:
            updates["transplantation_id"] = ObjectId(updates["transplantation_id"])
        except:
            raise HTTPException(status_code=400, detail="Invalid transplantation_id")

    result = outcome_collection.update_one(
        {"_id": obj_id},
        {"$set": updates}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Outcome not found")

    return {"message": "Outcome updated partially"}

# Delete an outcome by ID
@router.delete("/{outcome_id}", dependencies=[Depends(doctor_or_admin)])
def delete_outcome(outcome_id: str):
    try:
        obj_id = ObjectId(outcome_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = outcome_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Outcome not found")

    return {"message": "Outcome deleted"}

