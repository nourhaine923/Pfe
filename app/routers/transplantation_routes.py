# transplantation_routes.py
import datetime
from fastapi import APIRouter, HTTPException, Depends, Body, Query
from bson import ObjectId
from typing import List, Optional

from app.database import db
from app.auth.dependencies import nephrologist_or_admin

router = APIRouter(prefix="/transplantations", tags=["Transplantations"])

collection = db["transplantations"]
patients_collection = db["patients"]


# ---------------------------------------
# Helpers
# ---------------------------------------
def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, datetime.date) and not isinstance(obj, datetime.datetime):
        return datetime.datetime.combine(obj, datetime.time.min)
    return obj


def serialize(doc):
    """Convert MongoDB document to JSON serializable format with populated references"""
    doc["_id"] = str(doc["_id"])
    doc["recipient_id"] = str(doc["recipient_id"])
    doc["donor_id"] = str(doc["donor_id"])
    
    # Populate donor data
    if "donor" in doc and doc["donor"]:
        doc["donor"]["_id"] = str(doc["donor"]["_id"])
    
    # Populate recipient data
    if "recipient" in doc and doc["recipient"]:
        doc["recipient"]["_id"] = str(doc["recipient"]["_id"])
    
    return doc


def populate_donor_recipient(doc):
    """Add donor and recipient details to the transplantation document"""
    if not doc:
        return None
    
    # Get donor details
    donor_id = doc.get("donor_id")
    if donor_id:
        donor = patients_collection.find_one({"_id": donor_id})
        if donor:
            doc["donor"] = {
                "_id": donor["_id"],
                "firstName": donor.get("firstName"),
                "lastName": donor.get("lastName"),
                "bloodGroup": donor.get("bloodGroup"),
                "medicalRecordNumber": donor.get("medicalRecordNumber"),
                "patientRole": donor.get("patientRole")
            }
    
    # Get recipient details
    recipient_id = doc.get("recipient_id")
    if recipient_id:
        recipient = patients_collection.find_one({"_id": recipient_id})
        if recipient:
            doc["recipient"] = {
                "_id": recipient["_id"],
                "firstName": recipient.get("firstName"),
                "lastName": recipient.get("lastName"),
                "bloodGroup": recipient.get("bloodGroup"),
                "medicalRecordNumber": recipient.get("medicalRecordNumber"),
                "birthDate": recipient.get("birthDate"),
                "patientRole": recipient.get("patientRole")
            }
    
    return doc


# ---------------------------------------
# CREATE
# ---------------------------------------
@router.post("/", dependencies=[Depends(nephrologist_or_admin)])
def create_transplantation(data: dict):
    try:
        recipient_id = ObjectId(data["recipient_id"])
        donor_id = ObjectId(data["donor_id"])
    except:
        raise HTTPException(400, "Invalid ObjectId")

    # Validate existence
    if not patients_collection.find_one({"_id": recipient_id}):
        raise HTTPException(404, "Recipient not found")

    if not patients_collection.find_one({"_id": donor_id}):
        raise HTTPException(404, "Donor not found")

    data["recipient_id"] = recipient_id
    data["donor_id"] = donor_id

    data = convert_dates(data)

    result = collection.insert_one(data)

    # Return the created document with populated fields
    created_doc = collection.find_one({"_id": result.inserted_id})
    created_doc = populate_donor_recipient(created_doc)
    
    return {"id": str(result.inserted_id), "message": "Created successfully", "data": serialize(created_doc) if created_doc else None}


# ---------------------------------------
# GET ALL - WITH SEARCH AND PAGINATION
# ---------------------------------------
@router.get("/", dependencies=[Depends(nephrologist_or_admin)])
def get_all(
    search: Optional[str] = Query(None, description="Search by transplant number, donor name, or recipient name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    query = {}
    
    # Add search condition if provided
    if search and search.strip():
        # First, get all patients that match the search term
        patient_query = {
            "$or": [
                {"firstName": {"$regex": search, "$options": "i"}},
                {"lastName": {"$regex": search, "$options": "i"}},
                {"$expr": {
                    "$regexMatch": {
                        "input": {"$concat": ["$firstName", " ", "$lastName"]},
                        "regex": search,
                        "options": "i"
                    }
                }}
            ]
        }
        
        matching_patients = list(patients_collection.find(patient_query, {"_id": 1}))
        matching_patient_ids = [p["_id"] for p in matching_patients]
        
        # Search by transplant number or matching patient IDs
        query["$or"] = [
            {"transplantNumber": {"$regex": search, "$options": "i"}},
            {"donor_id": {"$in": matching_patient_ids}},
            {"recipient_id": {"$in": matching_patient_ids}}
        ]
    
    # Get total count for pagination
    total = collection.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * limit
    docs = list(collection.find(query).skip(skip).limit(limit))
    
    # Populate donor and recipient for each document
    populated_docs = []
    for doc in docs:
        populated_doc = populate_donor_recipient(doc)
        populated_docs.append(serialize(populated_doc))
    
    return {
        "data": populated_docs,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit
    }


# ---------------------------------------
# GET ONE - WITH POPULATION
# ---------------------------------------
@router.get("/{id}", dependencies=[Depends(nephrologist_or_admin)])
def get_one(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID")

    doc = collection.find_one({"_id": obj_id})

    if not doc:
        raise HTTPException(404, "Not found")

    # Populate donor and recipient
    doc = populate_donor_recipient(doc)

    return serialize(doc)


# ---------------------------------------
# UPDATE
# ---------------------------------------
@router.patch("/{id}", dependencies=[Depends(nephrologist_or_admin)])
def update(id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID")

    updates.pop("_id", None)
    updates.pop("donor", None)
    updates.pop("recipient", None)

    if "recipient_id" in updates:
        updates["recipient_id"] = ObjectId(updates["recipient_id"])

    if "donor_id" in updates:
        updates["donor_id"] = ObjectId(updates["donor_id"])

    updates = convert_dates(updates)

    result = collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(404, "Not found")

    updated = collection.find_one({"_id": obj_id})
    updated = populate_donor_recipient(updated)

    return serialize(updated)


# ---------------------------------------
# DELETE
# ---------------------------------------
@router.delete("/{id}", dependencies=[Depends(nephrologist_or_admin)])
def delete(id: str):
    try:
        obj_id = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID")
        
    result = collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(404, "Not found")

    return {"message": "Deleted successfully"}


# ---------------------------------------
# GET BY DONOR OR RECIPIENT
# ---------------------------------------
@router.get("/by-donor/{donor_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_by_donor(donor_id: str):
    try:
        obj_id = ObjectId(donor_id)
    except:
        raise HTTPException(400, "Invalid ID")
    
    docs = list(collection.find({"donor_id": obj_id}))
    
    populated_docs = []
    for doc in docs:
        populated_doc = populate_donor_recipient(doc)
        populated_docs.append(serialize(populated_doc))
    
    return populated_docs


@router.get("/by-recipient/{recipient_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_by_recipient(recipient_id: str):
    try:
        obj_id = ObjectId(recipient_id)
    except:
        raise HTTPException(400, "Invalid ID")
    
    docs = list(collection.find({"recipient_id": obj_id}))
    
    populated_docs = []
    for doc in docs:
        populated_doc = populate_donor_recipient(doc)
        populated_docs.append(serialize(populated_doc))
    
    return populated_docs


# ---------------------------------------
# CHECK TRANSPLANT NUMBER EXISTS
# ---------------------------------------
@router.get("/check-transplant-number/{transplantNumber}", dependencies=[Depends(nephrologist_or_admin)])
def check_transplant_number_exists(transplantNumber: str):
    """Check if transplant number already exists"""
    transplantation = collection.find_one({"transplantNumber": transplantNumber})
    return {"exists": transplantation is not None}