from fastapi import APIRouter, HTTPException, Body
from bson import ObjectId
from datetime import datetime, date
from typing import List

from app.database import db
from app.schemas.rejection_episode import RejectionEpisode

router = APIRouter(prefix="/rejections", tags=["Rejection Episodes"])

rejection_collection = db["rejections"]
followup_collection = db["followups"]
def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)
    return obj
# Create a new rejection episode
@router.post("/")
def create_rejection(rejection: RejectionEpisode):
    data = convert_dates(rejection.dict())

    try:
        followup_id = ObjectId(data["followup_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid followup_id")

    followup = followup_collection.find_one({"_id": followup_id})

    if not followup:
        raise HTTPException(status_code=404, detail="FollowUp not found")

    data["followup_id"] = followup_id

    result = rejection_collection.insert_one(data)

    return {
        "message": "Rejection episode recorded",
        "id": str(result.inserted_id)
    }

# Get all rejection episodes for a follow-up
@router.get("/by-followup/{followup_id}", response_model=List[dict])
def get_rejections(followup_id: str):
    obj_id = ObjectId(followup_id)

    episodes = list(rejection_collection.find({"followup_id": obj_id}))

    for e in episodes:
        e["_id"] = str(e["_id"])
        e["followup_id"] = str(e["followup_id"])

    return episodes

#update a rejection episode
@router.patch("/{rejection_id}")
def update_rejection(rejection_id: str, updates: dict = Body(...)):
    obj_id = ObjectId(rejection_id)

    updates = convert_dates(updates)

    if "followup_id" in updates:
        updates["followup_id"] = ObjectId(updates["followup_id"])

    result = rejection_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Rejection not found")

    return {"message": "Rejection updated"}

#delete a rejection episode
@router.delete("/{rejection_id}")
def delete_rejection(rejection_id: str):
    result = rejection_collection.delete_one({"_id": ObjectId(rejection_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rejection not found")

    return {"message": "Rejection deleted"}