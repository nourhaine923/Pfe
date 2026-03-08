from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, date
from typing import List
from fastapi import Body

from app.database import db
from app.schemas.immunological_marker import ImmunologicalMarker
from app.auth.dependencies import doctor_or_admin
from fastapi import Depends

router = APIRouter(prefix="/immunological", tags=["Immunological Markers"])

marker_collection = db["immunological_markers"]
followup_collection = db["followups"]

def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)
    return obj

# Create a new immunological marker
@router.post("/", dependencies=[Depends(doctor_or_admin)])
def create_marker(marker: ImmunologicalMarker):
    data = convert_dates(marker.dict())

    try:
        followup_id = ObjectId(data["followup_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid followup_id")

    if not followup_collection.find_one({"_id": followup_id}):
        raise HTTPException(status_code=404, detail="FollowUp not found")

    data["followup_id"] = followup_id

    result = marker_collection.insert_one(data)

    return {
        "message": "Marker recorded successfully",
        "id": str(result.inserted_id)
    }
# Get immunological markers by follow-up ID
@router.get("/by-followup/{followup_id}", response_model=List[dict], dependencies=[Depends(doctor_or_admin)])
def get_markers(followup_id: str):
    try:
        obj_id = ObjectId(followup_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    markers = list(marker_collection.find({"followup_id": obj_id}))

    for m in markers:
        m["_id"] = str(m["_id"])
        m["followup_id"] = str(m["followup_id"])

    return markers

# Update a marker by ID
@router.patch("/{marker_id}", dependencies=[Depends(doctor_or_admin)])
def partial_update_marker(marker_id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(marker_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    updates = convert_dates(updates)

    if "followup_id" in updates:
        updates["followup_id"] = ObjectId(updates["followup_id"])

    result = marker_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Marker not found")

    return {"message": "Marker updated partially"}

# Delete a marker by ID
@router.delete("/{marker_id}", dependencies=[Depends(doctor_or_admin)])
def delete_marker(marker_id: str):
    result = marker_collection.delete_one({"_id": ObjectId(marker_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Marker not found")

    return {"message": "Marker deleted"}
