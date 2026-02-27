from fastapi import APIRouter, HTTPException, Body
from bson import ObjectId
from typing import List

from app.database import db
from app.schemas.barem import Barem

router = APIRouter(prefix="/barems", tags=["Barem Configuration"])

barem_collection = db["barems"]

# Create or update Barem configuration
@router.post("/")
def create_barem(barem: Barem):
    data = barem.dict()

    # Prevent duplicate rule
    existing = barem_collection.find_one({
        "value": data["value"],
        "key": data["key"]
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This scoring rule already exists for this attribute value"
        )

    result = barem_collection.insert_one(data)

    return {
        "message": "Scoring rule added",
        "id": str(result.inserted_id)
    }

# Get Barem configurations by key
@router.get("/by-key/{key}", response_model=list[dict])
def get_rules_for_key(key: str):
    rules = list(barem_collection.find({"key": key}))

    for r in rules:
        r["_id"] = str(r["_id"])

    return rules

# Get all Barem configurations
@router.get("/", response_model=List[dict])
def get_barems():
    barems = list(barem_collection.find())

    for b in barems:
        b["_id"] = str(b["_id"])

    return barems

# Update a Barem configuration
@router.patch("/{barem_id}")
def update_barem(barem_id: str, updates: dict = Body(...)):
    obj_id = ObjectId(barem_id)

    result = barem_collection.update_one({"_id": obj_id}, {"$set": updates})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Barem not found")

    return {"message": "Barem updated"}

# Delete a Barem configuration
@router.delete("/{barem_id}")
def delete_barem(barem_id: str):
    result = barem_collection.delete_one({"_id": ObjectId(barem_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Barem not found")

    return {"message": "Barem deleted"}
