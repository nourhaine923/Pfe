from fastapi import APIRouter, HTTPException, Body, Depends
from bson import ObjectId
from datetime import datetime, date
from typing import List

from app.database import db
from app.schemas.transfusion_event import TransfusionEvent
from app.auth.dependencies import nephrologist_or_admin

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
@router.post("/", dependencies=[Depends(nephrologist_or_admin)])
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
    if patient.get("patientRole") != "recipient":
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
@router.get("/by-patient/{patient_id}", response_model=List[dict], dependencies=[Depends(nephrologist_or_admin)])
def get_transfusions(patient_id: str):
    try:
        obj_id = ObjectId(patient_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    events = list(transfusion_collection.find({"patient_id": obj_id}))

    for e in events:
        e["_id"] = str(e["_id"])
        e["patient_id"] = str(e["patient_id"])

    return events

# Get a single transfusion event by id
@router.get("/{event_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_transfusion(event_id: str):
    try:
        obj_id = ObjectId(event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    
    event = transfusion_collection.find_one({"_id": obj_id})
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event["_id"] = str(event["_id"])
    event["patient_id"] = str(event["patient_id"])
    
    return event

# Update transfusion event by id
@router.patch("/{event_id}", dependencies=[Depends(nephrologist_or_admin)])
def update_transfusion(event_id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")

    # Remove fields that shouldn't be updated
    updates.pop("_id", None)
    updates.pop("patient_id", None)
    
    updates = convert_dates(updates)

    result = transfusion_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Transfusion updated"}

# Delete transfusion event by id
@router.delete("/{event_id}", dependencies=[Depends(nephrologist_or_admin)])
def delete_transfusion(event_id: str):
    try:
        obj_id = ObjectId(event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")
        
    result = transfusion_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Transfusion deleted"}