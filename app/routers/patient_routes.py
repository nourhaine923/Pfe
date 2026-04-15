# patient_routes.py
import datetime  
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from typing import List, Optional
from fastapi import Body, Depends

from app.database import db
from app.schemas.patient import Patient
from app.auth.dependencies import nephrologist_or_admin
from fastapi import Depends

router = APIRouter(prefix="/patients", tags=["Patients"])

patients_collection = db["patients"]

def convert_dates(obj):
    """Convert date objects to datetime for MongoDB"""
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, datetime.date) and not isinstance(obj, datetime.datetime):
        return datetime.datetime.combine(obj, datetime.time.min)
    return obj

# Create a new patient
@router.post("/", dependencies=[Depends(nephrologist_or_admin)])
def create_patient(patient: Patient):
    patient_dict = patient.dict()  
    
    # Convert any date fields to datetime
    data = convert_dates(patient_dict)

    result = patients_collection.insert_one(data)

    return {
        "message": "Patient created successfully",
        "id": str(result.inserted_id)
    }

# Get all patients with pagination
@router.get("/", dependencies=[Depends(nephrologist_or_admin)])
def get_patients(
    search: Optional[str] = Query(None, description="Search by name or MRN"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    query = {}
    
    # Add search condition if provided
    if search and search.strip():
        if search.isdigit():
            query["medicalRecordNumber"] = int(search)
        else:
            query["$or"] = [
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
    
    # Get total count
    total = patients_collection.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * limit
    patients = list(patients_collection.find(query).skip(skip).limit(limit))
    
    for patient in patients:
        patient["_id"] = str(patient["_id"])
    
    return {
        "data": patients,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": (total + limit - 1) // limit
    }

# Get all patients without pagination (for frontend filtering)
@router.get("/all", dependencies=[Depends(nephrologist_or_admin)])
def get_all_patients(
    search: Optional[str] = Query(None, description="Search by name or MRN")
):
    query = {}
    
    # Add search condition if provided
    if search and search.strip():
        if search.isdigit():
            query["medicalRecordNumber"] = int(search)
        else:
            query["$or"] = [
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
    
    patients = list(patients_collection.find(query))
    
    for patient in patients:
        patient["_id"] = str(patient["_id"])
    
    return patients

# Get a patient by ID
@router.get("/{patient_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_patient(patient_id: str):
    try:
        obj_id = ObjectId(patient_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid patient ID")
    
    patient = patients_collection.find_one({"_id": obj_id})

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient["_id"] = str(patient["_id"])
    return patient

# Delete a patient by ID
@router.delete("/{patient_id}", dependencies=[Depends(nephrologist_or_admin)])
def delete_patient(patient_id: str):
    try:
        obj_id = ObjectId(patient_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid patient ID")
    
    result = patients_collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {"message": "Patient deleted"}

# Update a patient by ID
@router.patch("/{patient_id}", dependencies=[Depends(nephrologist_or_admin)])
def partial_update_patient(patient_id: str, updates: dict = Body(...)):
    try:
        obj_id = ObjectId(patient_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    # Prevent updating Mongo internal id
    if "_id" in updates:
        del updates["_id"]
    
    # Also convert dates in updates
    updates = convert_dates(updates)

    result = patients_collection.update_one(
        {"_id": obj_id},
        {"$set": updates}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {"message": "Patient updated partially"}

# Check if MRN exists
@router.get("/check-mrn/{mrn}", dependencies=[Depends(nephrologist_or_admin)])
def check_mrn_exists(mrn: int):
    """Check if MRN already exists"""
    patient = patients_collection.find_one({"medicalRecordNumber": mrn})
    return {"exists": patient is not None}