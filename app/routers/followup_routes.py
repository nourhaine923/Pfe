# followup_routes.py

import datetime
from fastapi import APIRouter, HTTPException, Depends, Body, Query
from bson import ObjectId
from typing import List, Optional
from app.database import db
from app.auth.dependencies import nephrologist_or_admin

router = APIRouter(prefix="/followups", tags=["FollowUps"])

collection = db["followups"]
tx_collection = db["transplantations"]
patients_collection = db["patients"]


def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, datetime.date) and not isinstance(obj, datetime.datetime):
        return datetime.datetime.combine(obj, datetime.time.min)
    return obj


def convert_objectid(obj):
    """Convert ObjectId to string recursively"""
    if isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj


def populate_transplantation(doc):
    if not doc:
        return None
    
    # Make a copy to avoid modifying original
    result = dict(doc)
    
    transplantation_id = result.get("transplantation_id")
    if transplantation_id:
        # Convert ObjectId to string for query if needed
        if isinstance(transplantation_id, ObjectId):
            tx_id = transplantation_id
        else:
            tx_id = ObjectId(transplantation_id) if isinstance(transplantation_id, str) else transplantation_id
        
        transplantation = tx_collection.find_one({"_id": tx_id})
        if transplantation:
            # Convert transplantation ObjectIds to strings
            transplantation["_id"] = str(transplantation["_id"])
            transplantation["recipient_id"] = str(transplantation.get("recipient_id"))
            transplantation["donor_id"] = str(transplantation.get("donor_id"))
            
            # Get recipient details
            recipient_id = transplantation.get("recipient_id")
            if recipient_id:
                recipient_obj_id = ObjectId(recipient_id)
                recipient = patients_collection.find_one({"_id": recipient_obj_id})
                if recipient:
                    transplantation["recipient"] = {
                        "_id": str(recipient["_id"]),
                        "firstName": recipient.get("firstName"),
                        "lastName": recipient.get("lastName"),
                        "bloodGroup": recipient.get("bloodGroup"),
                        "medicalRecordNumber": recipient.get("medicalRecordNumber"),
                    }
            
            result["transplantation"] = transplantation
    
    return result


def serialize(doc):
    if not doc:
        return None
    
    # Convert ObjectIds to strings
    result = convert_objectid(doc)
    
    # Ensure top-level fields are strings
    if "_id" in result:
        result["_id"] = str(result["_id"])
    if "transplantation_id" in result:
        result["transplantation_id"] = str(result["transplantation_id"])
    
    return result


@router.post("/", dependencies=[Depends(nephrologist_or_admin)])
def create_followup(data: dict):
    try:
        tx_id = ObjectId(data["transplantation_id"])
    except:
        raise HTTPException(400, "Invalid ObjectId for transplantation_id")

    if not tx_collection.find_one({"_id": tx_id}):
        raise HTTPException(404, "Transplantation not found")

    data["transplantation_id"] = tx_id
    data = convert_dates(data)

    result = collection.insert_one(data)

    created_doc = collection.find_one({"_id": result.inserted_id})
    created_doc = populate_transplantation(created_doc)
    
    return {
        "id": str(result.inserted_id), 
        "message": "Created successfully",
        "data": serialize(created_doc) if created_doc else None
    }


@router.get("/", dependencies=[Depends(nephrologist_or_admin)])
def get_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    query = {}
    
    if search and search.strip():
        matching_patients = list(patients_collection.find({
            "$or": [
                {"firstName": {"$regex": search, "$options": "i"}},
                {"lastName": {"$regex": search, "$options": "i"}},
            ],
            "patientRole": "recipient"
        }, {"_id": 1}))
        
        matching_patient_ids = [p["_id"] for p in matching_patients]
        
        matching_transplantations = list(tx_collection.find({
            "$or": [
                {"transplantNumber": {"$regex": search, "$options": "i"}},
                {"recipient_id": {"$in": matching_patient_ids}} if matching_patient_ids else None
            ]
        }, {"_id": 1}))
        
        matching_transplantations = [tx for tx in matching_transplantations if tx is not None]
        matching_tx_ids = [tx["_id"] for tx in matching_transplantations]
        
        if matching_tx_ids:
            query["transplantation_id"] = {"$in": matching_tx_ids}
        else:
            query["_id"] = None
    
    total = collection.count_documents(query)
    skip = (page - 1) * limit
    docs = list(collection.find(query).skip(skip).limit(limit))
    
    populated_docs = []
    for doc in docs:
        populated_doc = populate_transplantation(doc)
        populated_docs.append(serialize(populated_doc))
    
    return {
        "data": populated_docs,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit if total > 0 else 1
    }


@router.get("/{id}", dependencies=[Depends(nephrologist_or_admin)])
def get_one(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID")
    
    doc = collection.find_one({"_id": obj_id})
    
    if not doc:
        raise HTTPException(404, "Not found")
    
    doc = populate_transplantation(doc)
    
    return serialize(doc)


@router.patch("/{id}", dependencies=[Depends(nephrologist_or_admin)])
def update(id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID")

    updates.pop("_id", None)
    updates.pop("transplantation", None)

    if "transplantation_id" in updates:
        try:
            updates["transplantation_id"] = ObjectId(updates["transplantation_id"])
        except:
            raise HTTPException(400, "Invalid transplantation_id")

    updates = convert_dates(updates)

    result = collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(404, "Not found")

    updated = collection.find_one({"_id": obj_id})
    updated = populate_transplantation(updated)

    return serialize(updated)


@router.delete("/{id}", dependencies=[Depends(nephrologist_or_admin)])
def delete(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID")
        
    # Delete related data
    db["vitals"].delete_many({"followup_id": obj_id})
    db["biological_measurements"].delete_many({"followup_id": obj_id})
    db["immunological_markers"].delete_many({"followup_id": obj_id})
    db["rejections"].delete_many({"followup_id": obj_id})
    db["adverse_events"].delete_many({"followup_id": obj_id})
    db["adherence"].delete_many({"followup_id": obj_id})
    db["treatments"].delete_many({"followup_id": obj_id})
    db["immunosuppression_regimens"].delete_many({"followup_id": obj_id})
    
    result = collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(404, "Not found")

    return {"message": "Deleted successfully"}


@router.get("/by-transplantation/{transplantation_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_by_transplantation(transplantation_id: str):
    try:
        tx_obj_id = ObjectId(transplantation_id)
    except:
        raise HTTPException(400, "Invalid transplantation ID")
    
    docs = list(collection.find({"transplantation_id": tx_obj_id}))
    
    populated_docs = []
    for doc in docs:
        populated_doc = populate_transplantation(doc)
        populated_docs.append(serialize(populated_doc))
    
    return populated_docs