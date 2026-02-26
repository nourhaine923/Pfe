import datetime  
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from fastapi import Body

from app.database import db
from app.schemas.patient import Patient

router = APIRouter(prefix="/patients", tags=["Patients"])

patients_collection = db["patients"]

def convert_dates(obj):
    """Convert date objects to datetime for MongoDB"""
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    # Check if it's a date (but not a datetime)
    if isinstance(obj, datetime.date) and not isinstance(obj, datetime.datetime):
        # Convert date to datetime at midnight
        return datetime.datetime.combine(obj, datetime.time.min)
    return obj

# Create a new patient
@router.post("/")
def create_patient(patient: Patient):
    patient_dict = patient.dict()  # If using Pydantic v1
    # For Pydantic v2, use: patient_dict = patient.model_dump()
    
    # Convert any date fields to datetime
    data = convert_dates(patient_dict)

    result = patients_collection.insert_one(data)

    return {
        "message": "Patient created successfully",
        "id": str(result.inserted_id)
    }

# Get all patients
@router.get("/", response_model=List[dict])
def get_patients():
    patients = list(patients_collection.find())

    for patient in patients:
        patient["_id"] = str(patient["_id"])
        # Optional: Convert datetime back to date if needed
        # if "birth_date" in patient and isinstance(patient["birth_date"], datetime.datetime):
        #     patient["birth_date"] = patient["birth_date"].date()

    return patients

# Get a patient by ID
@router.get("/{patient_id}")
def get_patient(patient_id: str):
    patient = patients_collection.find_one({"_id": ObjectId(patient_id)})

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient["_id"] = str(patient["_id"])
    # Optional: Convert datetime back to date if needed
    # if "birth_date" in patient and isinstance(patient["birth_date"], datetime.datetime):
    #     patient["birth_date"] = patient["birth_date"].date()
    return patient

# Delete a patient by ID (just for testing)
@router.delete("/{patient_id}")
def delete_patient(patient_id: str):
    result = patients_collection.delete_one({"_id": ObjectId(patient_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {"message": "Patient deleted"}

# Update a patient by ID
@router.patch("/{patient_id}")
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