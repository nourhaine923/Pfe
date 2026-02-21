from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, date
from typing import List
from fastapi import Body

from app.database import db
from app.schemas.therapeutic_treatment import TherapeuticTreatment

router = APIRouter(prefix="/treatments", tags=["Therapeutic Treatments"])

treatment_collection = db["treatments"]
followup_collection = db["followups"]

def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date):
        return datetime(obj.year, obj.month, obj.day)
    return obj

# Create a new therapeutic treatment
@router.post("/")
def create_treatment(treatment: TherapeuticTreatment):
    data = convert_dates(treatment.dict())

    try:
        followup_id = ObjectId(data["followup_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid followup_id")

    if not followup_collection.find_one({"_id": followup_id}):
        raise HTTPException(status_code=404, detail="FollowUp not found")

    data["followup_id"] = followup_id

    result = treatment_collection.insert_one(data)

    return {"id": str(result.inserted_id)}

# Get treatments by follow-up ID
@router.get("/by-followup/{followup_id}", response_model=List[dict])
def get_treatments(followup_id: str):
    obj_id = ObjectId(followup_id)

    treatments = list(treatment_collection.find({"followup_id": obj_id}))

    for t in treatments:
        t["_id"] = str(t["_id"])
        t["followup_id"] = str(t["followup_id"])

    return treatments

#update treatment by ID
@router.patch("/{treatment_id}")
def partial_update_treatment(treatment_id: str, updates: dict = Body(...)):
    obj_id = ObjectId(treatment_id)

    updates = convert_dates(updates)

    if "followup_id" in updates:
        updates["followup_id"] = ObjectId(updates["followup_id"])

    result = treatment_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Treatment not found")

    return {"message": "Treatment updated partially"}


#Delete treatment by ID
@router.delete("/{treatment_id}")
def delete_treatment(treatment_id: str):
    result = treatment_collection.delete_one({"_id": ObjectId(treatment_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Treatment not found")

    return {"message": "Treatment deleted"}

