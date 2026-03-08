from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, date
from typing import List
from fastapi import Body

from app.database import db
from app.schemas.adverse_event import AdverseEvent
from app.auth.dependencies import doctor_or_admin
from fastapi import Depends

router = APIRouter(prefix="/adverse-events", tags=["Adverse Events"])

adverse_collection = db["adverse_events"]
followup_collection = db["followups"]

def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)
    return obj

# Create a new adverse event
@router.post("/", dependencies=[Depends(doctor_or_admin)])
def create_adverse_event(event: AdverseEvent):
    data = convert_dates(event.dict())

    try:
        followup_id = ObjectId(data["followup_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid followup_id")

    # Ensure FollowUp exists
    if not followup_collection.find_one({"_id": followup_id}):
        raise HTTPException(status_code=404, detail="FollowUp not found")

    data["followup_id"] = followup_id

    result = adverse_collection.insert_one(data)

    return {
        "message": "Adverse event recorded",
        "id": str(result.inserted_id)
    }

# Get adverse events by follow-up ID
@router.get("/by-followup/{followup_id}", response_model=List[dict], dependencies=[Depends(doctor_or_admin)])
def get_events_by_followup(followup_id: str):
    try:
        obj_id = ObjectId(followup_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    events = list(adverse_collection.find({"followup_id": obj_id}))

    for e in events:
        e["_id"] = str(e["_id"])
        e["followup_id"] = str(e["followup_id"])

    return events
# Update an adverse event by ID
@router.patch("/{event_id}", dependencies=[Depends(doctor_or_admin)])
def partial_update_event(event_id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    updates = convert_dates(updates)

    if "followup_id" in updates:
        updates["followup_id"] = ObjectId(updates["followup_id"])

    result = adverse_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Adverse event not found")

    return {"message": "Adverse event updated partially"}

# Delete an adverse event by ID
@router.delete("/{event_id}", dependencies=[Depends(doctor_or_admin)])
def delete_event(event_id: str):
    result = adverse_collection.delete_one({"_id": ObjectId(event_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Adverse event not found")

    return {"message": "Adverse event deleted"}


