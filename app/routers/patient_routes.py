from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from fastapi import Body

from app.database import db
from app.schemas.patient import Patient

router = APIRouter(prefix="/patients", tags=["Patients"])

patients_collection = db["patients"]

# Create a new patient
@router.post("/")
def create_patient(patient: Patient):
    patient_dict = patient.dict()

    result = patients_collection.insert_one(patient_dict)

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

    return patients
# Get a patient by ID
@router.get("/{patient_id}")
def get_patient(patient_id: str):
    patient = patients_collection.find_one({"_id": ObjectId(patient_id)})

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient["_id"] = str(patient["_id"])
    return patient
#delete a patient by ID(just for testing )
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

    result = patients_collection.update_one(
        {"_id": obj_id},
        {"$set": updates}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {"message": "Patient updated partially"}
