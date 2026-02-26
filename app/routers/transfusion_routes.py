from fastapi import APIRouter, HTTPException, Body
from bson import ObjectId
from datetime import datetime, date
from typing import List

from app.database import db
from app.schemas.transfusion_event import TransfusionEvent

router = APIRouter(prefix="/transfusions", tags=["Transfusion Events"])

transfusion_collection = db["transfusions"]
patients_collection = db["patients"]
def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)
    return obj

# Create a new transfusion event
@router.post("/")
def create_transfusion(event: TransfusionEvent):
    data = convert_dates(event.dict())

    try:
        patient_id = ObjectId(data["patient_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid patient_id")

    # Check patient exists
    patient = patients_collection.find_one({"_id": patient_id})

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

# BUSINESS RULE: transfusion only for recipients
    if patient.get("patientRole") != "Recipient":
        raise HTTPException(
        status_code=400,
        detail="Transfusion events can only be recorded for Recipient patients"
    )
    data["patient_id"] = patient_id

    result = transfusion_collection.insert_one(data)

    return {
        "message": "Transfusion event recorded",
        "id": str(result.inserted_id)
    }

# Get all transfusion events for a patient
@router.get("/by-patient/{patient_id}", response_model=List[dict])
def get_transfusions(patient_id: str):
    obj_id = ObjectId(patient_id)

    events = list(transfusion_collection.find({"patient_id": obj_id}))

    for e in events:
        e["_id"] = str(e["_id"])
        e["patient_id"] = str(e["patient_id"])

    return events

# Update transfusion event by id
@router.patch("/{event_id}")
def update_transfusion(event_id: str, updates: dict = Body(...)):
    obj_id = ObjectId(event_id)

    updates = convert_dates(updates)

    if "patient_id" in updates:
        updates["patient_id"] = ObjectId(updates["patient_id"])

    result = transfusion_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Transfusion updated"}

#delete transfusion event by id
@router.delete("/{event_id}")
def delete_transfusion(event_id: str):
    result = transfusion_collection.delete_one({"_id": ObjectId(event_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Transfusion deleted"}
