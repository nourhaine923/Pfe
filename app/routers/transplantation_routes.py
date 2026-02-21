from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from datetime import datetime
from fastapi import Body

from app.database import db
from app.schemas.transplantation import Transplantation

router = APIRouter(prefix="/transplantations", tags=["Transplantations"])

transplantation_collection = db["transplantations"]
patients_collection = db["patients"]

# Helper function to convert date objects to datetime for MongoDB
def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(item) for item in obj]

    if isinstance(obj, dict):
        return {key: convert_dates(value) for key, value in obj.items()}

    if isinstance(obj, datetime):
        return obj

    # Convert date → datetime
    try:
        from datetime import date
        if isinstance(obj, date):
            return datetime(obj.year, obj.month, obj.day)
    except:
        pass

    return obj


# Create a new transplantation
@router.post("/")
def create_transplantation(transplantation: Transplantation):
    data = convert_dates(transplantation.dict())

    # Convert string IDs → ObjectId
    recipient_id = ObjectId(data["recipient_id"])
    donor_id = ObjectId(data["donor_id"])

    # Verify referenced patients exist
    if not patients_collection.find_one({"_id": recipient_id}):
        raise HTTPException(status_code=404, detail="Recipient not found")

    if not patients_collection.find_one({"_id": donor_id}):
        raise HTTPException(status_code=404, detail="Donor not found")

    # Replace string IDs with ObjectId before saving
    data["recipient_id"] = recipient_id
    data["donor_id"] = donor_id

    result = transplantation_collection.insert_one(data)

    return {
        "message": "Transplantation created successfully",
        "id": str(result.inserted_id)
    }
# Get all transplantations
@router.get("/", response_model=List[dict])
def get_transplantations():
    transplants = list(transplantation_collection.find())

    for t in transplants:
        t["_id"] = str(t["_id"])
        t["recipient_id"] = str(t["recipient_id"])
        t["donor_id"] = str(t["donor_id"])

    return transplants
# Get a transplantation by ID
@router.get("/{transplantation_id}")
def get_transplantation(transplantation_id: str):
    transplant = transplantation_collection.find_one(
        {"_id": ObjectId(transplantation_id)}
    )

    if not transplant:
        raise HTTPException(status_code=404, detail="Transplantation not found")

    transplant["_id"] = str(transplant["_id"])
    transplant["recipient_id"] = str(transplant["recipient_id"])
    transplant["donor_id"] = str(transplant["donor_id"])

    return transplant

# Update a transplantation by ID
@router.patch("/{transplantation_id}")
def partial_update_transplantation(transplantation_id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(transplantation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    updates = convert_dates(updates)

    # Convert relationship fields only if present
    if "recipient_id" in updates:
        updates["recipient_id"] = ObjectId(updates["recipient_id"])

    if "donor_id" in updates:
        updates["donor_id"] = ObjectId(updates["donor_id"])

    result = transplantation_collection.update_one(
        {"_id": obj_id},
        {"$set": updates}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Transplantation not found")

    return {"message": "Transplantation updated partially"}

# Delete a transplantation by ID

@router.delete("/{transplantation_id}")
def delete_transplantation(transplantation_id: str):
    obj_id = ObjectId(transplantation_id)

    result = transplantation_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")

    return {"message": "Transplantation deleted"}
