from fastapi import APIRouter, HTTPException, Depends, Body
from bson import ObjectId
from datetime import datetime, date
from typing import List, Optional

from app.database import db
from app.schemas.outcome import Outcome
from app.auth.dependencies import nephrologist_or_admin

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
@router.post("/", dependencies=[Depends(nephrologist_or_admin)])
def create_outcome(outcome: Outcome):
    data = convert_dates(outcome.dict())

    try:
        transplantation_id = ObjectId(data["transplantation_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid transplantation_id")

    # Get transplantation to check status
    transplantation = transplantation_collection.find_one({"_id": transplantation_id})
    
    if not transplantation:
        raise HTTPException(status_code=404, detail="Transplantation not found")
    
    # BUSINESS RULE: Only approved transplantations can have outcomes
    if transplantation.get("status") != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Outcomes can only be recorded for APPROVED transplantations"
        )

    data["transplantation_id"] = transplantation_id

    # Check if outcome already exists for this transplantation
    existing = outcome_collection.find_one({"transplantation_id": transplantation_id})
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Outcome already exists for this transplantation. Use update instead."
        )

    result = outcome_collection.insert_one(data)

    return {
        "message": "Outcome recorded successfully",
        "id": str(result.inserted_id)
    }

# Get outcome by transplantation ID
@router.get("/by-transplantation/{transplantation_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_outcome(transplantation_id: str):
    try:
        obj_id = ObjectId(transplantation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    outcome = outcome_collection.find_one({"transplantation_id": obj_id})

    if not outcome:
        return None

    outcome["_id"] = str(outcome["_id"])
    outcome["transplantation_id"] = str(outcome["transplantation_id"])

    return outcome

# Update outcome
@router.patch("/{outcome_id}", dependencies=[Depends(nephrologist_or_admin)])
def update_outcome(outcome_id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(outcome_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    # Get the outcome to check the associated transplantation
    outcome = outcome_collection.find_one({"_id": obj_id})
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")
    
    # Get transplantation to check status
    transplantation = transplantation_collection.find_one({"_id": outcome["transplantation_id"]})
    
    if transplantation and transplantation.get("status") != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Cannot update outcome for non-APPROVED transplantations"
        )

    # Remove protected fields
    updates.pop("_id", None)
    updates.pop("transplantation_id", None)
    
    updates = convert_dates(updates)

    result = outcome_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Outcome not found")

    return {"message": "Outcome updated successfully"}

# Delete outcome
@router.delete("/{outcome_id}", dependencies=[Depends(nephrologist_or_admin)])
def delete_outcome(outcome_id: str):
    try:
        obj_id = ObjectId(outcome_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    # Get the outcome to check the associated transplantation
    outcome = outcome_collection.find_one({"_id": obj_id})
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not found")
    
    # Get transplantation to check status
    transplantation = transplantation_collection.find_one({"_id": outcome["transplantation_id"]})
    
    if transplantation and transplantation.get("status") != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete outcome for non-APPROVED transplantations"
        )

    result = outcome_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Outcome not found")

    return {"message": "Outcome deleted"}