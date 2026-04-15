from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from typing import List, Optional

from app.database import db
from app.schemas.barem import Barem
from app.auth.dependencies import nephrologist_or_admin
from fastapi import Depends


router = APIRouter(prefix="/barems", tags=["Barems"])

barem_collection = db["barems"]


# Helper: Convert Mongo _id to string
def serialize_barem(doc):
    doc["_id"] = str(doc["_id"])
    return doc


# CREATE a new Barem rule
@router.post("/", response_model=dict, dependencies=[Depends(nephrologist_or_admin)])
def create_barem(barem: Barem):

    # Prevent duplicate key for same score
    existing = barem_collection.find_one({
        "score": barem.score,
        "key": barem.key
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Barem already exists for key '{barem.key}' in score '{barem.score}'"
        )

    result = barem_collection.insert_one(barem.model_dump())

    return {
        "message": "Barem created successfully",
        "id": str(result.inserted_id)
    }


# GET all Barems (optionally filter by score)
@router.get("/", response_model=List[dict], dependencies=[Depends(nephrologist_or_admin)])
def get_barems(score: Optional[str] = Query(None)):
    """
    Retrieve all barems, or filter by score name.
    """

    query = {"score": score} if score else {}

    docs = list(barem_collection.find(query))

    return [serialize_barem(doc) for doc in docs]


# GET a single Barem by ID
@router.get("/{barem_id}", response_model=dict, dependencies=[Depends(nephrologist_or_admin)])
def get_barem(barem_id: str):
    doc = barem_collection.find_one({"_id": ObjectId(barem_id)})

    if not doc:
        raise HTTPException(status_code=404, detail="Barem not found")

    return serialize_barem(doc)


# UPDATE a Barem (doctor edits rules)
@router.put("/{barem_id}", response_model=dict, dependencies=[Depends(nephrologist_or_admin)])
def update_barem(barem_id: str, barem: Barem):
    """
    Replace an existing rule definition.
    Used when doctor edits scoring logic.
    """

    result = barem_collection.update_one(
        {"_id": ObjectId(barem_id)},
        {"$set": barem.model_dump()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Barem not found")

    return {"message": "Barem updated successfully"}


# DELETE a Barem
@router.delete("/{barem_id}", response_model=dict, dependencies=[Depends(nephrologist_or_admin)])
def delete_barem(barem_id: str):

    result = barem_collection.delete_one({"_id": ObjectId(barem_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Barem not found")

    return {"message": "Barem deleted successfully"}