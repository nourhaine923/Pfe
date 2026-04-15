from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from app.database import db
from app.auth.dependencies import nephrologist_or_admin
from fastapi import Depends

router = APIRouter(prefix="/immunosuppressions", tags=["Immunosuppression"])

collection = db["immunosuppression_regimens"]


# ---------------------------------------
# Helper: serialize Mongo document
# ---------------------------------------
def serialize(doc):
    if not doc:
        return None
    return {
        "_id": str(doc["_id"]),
        "startDate": doc.get("startDate"),
        "endDate": doc.get("endDate"),
        "corticosteroids": doc.get("corticosteroids", False),
        "mmf": doc.get("mmf", False),
        "azathioprine": doc.get("azathioprine", False),
        "tacrolimus": doc.get("tacrolimus", False),
        "ciclosporine": doc.get("ciclosporine", False),
        "sirolimus": doc.get("sirolimus", False),
        "followup_id": str(doc["followup_id"]) if doc.get("followup_id") else None
    }


# ---------------------------------------
# CREATE Immunosuppression Regimen
# ---------------------------------------
@router.post("/", dependencies=[Depends(nephrologist_or_admin)])
def create_regimen(data: dict):
    # Convert followup_id string to ObjectId
    if "followup_id" in data:
        if isinstance(data["followup_id"], str):
            data["followup_id"] = ObjectId(data["followup_id"])
    
    result = collection.insert_one(data)

    new_doc = collection.find_one({"_id": result.inserted_id})

    return serialize(new_doc)


# ---------------------------------------
# GET All Regimens
# ---------------------------------------
@router.get("/", dependencies=[Depends(nephrologist_or_admin)])
def get_all_regimens():
    docs = list(collection.find())
    return [serialize(doc) for doc in docs if doc]


# ---------------------------------------
# GET One Regimen
# ---------------------------------------
@router.get("/{regimen_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_regimen(regimen_id: str):
    doc = collection.find_one({"_id": ObjectId(regimen_id)})

    if not doc:
        raise HTTPException(status_code=404, detail="Regimen not found")

    return serialize(doc)


# ---------------------------------------
# UPDATE Regimen (Partial Update)
# ---------------------------------------
@router.patch("/{regimen_id}", dependencies=[Depends(nephrologist_or_admin)])
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
@router.delete("/{regimen_id}", dependencies=[Depends(nephrologist_or_admin)])
def delete_regimen(regimen_id: str):
    result = collection.delete_one({"_id": ObjectId(regimen_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Regimen not found")

    return {"message": "Regimen deleted successfully"}


# ---------------------------------------
# GET Regimen by FollowUp ID
# ---------------------------------------
@router.get("/by-followup/{followup_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_regimen_by_followup(followup_id: str):
    try:
        obj_id = ObjectId(followup_id)
    except:
        raise HTTPException(400, "Invalid followup ID")
    
    doc = collection.find_one({"followup_id": obj_id})
    
    if not doc:
        # Return 404 to indicate not found, frontend will handle null
        return None
    
    return serialize(doc)