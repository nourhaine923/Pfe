from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, date
from typing import List
from fastapi import Body

from app.database import db
from app.schemas.biological_measurement import BiologicalMeasurement

router = APIRouter(prefix="/biological", tags=["Biological Measurements"])

bio_collection = db["biological_measurements"]
followup_collection = db["followups"]
# Helper function to convert date objects to datetime for MongoDB
def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)
    return obj
# Create a new biological measurement
@router.post("/")
def create_measurement(measurement: BiologicalMeasurement):
    data = convert_dates(measurement.dict())

    try:
        followup_id = ObjectId(data["followup_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid followup_id")

    if not followup_collection.find_one({"_id": followup_id}):
        raise HTTPException(status_code=404, detail="FollowUp not found")

    data["followup_id"] = followup_id

    result = bio_collection.insert_one(data)

    return {"id": str(result.inserted_id)}

# Get measurements by follow-up ID
@router.get("/by-followup/{followup_id}", response_model=List[dict])
def get_measurements(followup_id: str):
    obj_id = ObjectId(followup_id)

    measurements = list(bio_collection.find({"followup_id": obj_id}))

    for m in measurements:
        m["_id"] = str(m["_id"])
        m["followup_id"] = str(m["followup_id"])

    return measurements

# Update a measurement by ID
@router.patch("/{measurement_id}")
def partial_update_measurement(measurement_id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(measurement_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    updates = convert_dates(updates)

    if "followup_id" in updates:
        updates["followup_id"] = ObjectId(updates["followup_id"])

    result = bio_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Measurement not found")

    return {"message": "Measurement updated partially"}

#Delete a measurement by ID
@router.delete("/{measurement_id}")
def delete_measurement(measurement_id: str):
    result = bio_collection.delete_one({"_id": ObjectId(measurement_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Measurement not found")

    return {"message": "Measurement deleted"}
