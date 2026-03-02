from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from app.database import db

router = APIRouter(prefix="/immunosuppressions", tags=["Immunosuppression"])

collection = db["immunosuppression_regimens"]


# ---------------------------------------
# Helper: serialize Mongo document
# ---------------------------------------
def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc


# ---------------------------------------
# CREATE Immunosuppression Regimen
# ---------------------------------------
@router.post("/")
def create_regimen(data: dict):

    result = collection.insert_one(data)

    new_doc = collection.find_one({"_id": result.inserted_id})

    return serialize(new_doc)


# ---------------------------------------
# GET All Regimens
# ---------------------------------------
@router.get("/")
def get_all_regimens():

    docs = list(collection.find())

    return [serialize(doc) for doc in docs]


# ---------------------------------------
# GET One Regimen
# ---------------------------------------
@router.get("/{regimen_id}")
def get_regimen(regimen_id: str):

    doc = collection.find_one({"_id": ObjectId(regimen_id)})

    if not doc:
        raise HTTPException(status_code=404, detail="Regimen not found")

    return serialize(doc)


# ---------------------------------------
# UPDATE Regimen (Partial Update)
# ---------------------------------------
@router.patch("/{regimen_id}")
def update_regimen(regimen_id: str, updates: dict):

    result = collection.update_one(
        {"_id": ObjectId(regimen_id)},
        {"$set": updates}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Regimen not found")

    updated_doc = collection.find_one({"_id": ObjectId(regimen_id)})

    return serialize(updated_doc)


# ---------------------------------------
# DELETE Regimen
# ---------------------------------------
@router.delete("/{regimen_id}")
def delete_regimen(regimen_id: str):

    result = collection.delete_one({"_id": ObjectId(regimen_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Regimen not found")

    return {"message": "Regimen deleted successfully"}