from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from typing import List, Optional
from datetime import date, datetime

from app.database import db
from app.schemas.crossmatch_test import CrossmatchTest
from app.auth.dependencies import nephrologist_or_admin

router = APIRouter(prefix="/crossmatch-tests", tags=["Crossmatch Tests"])

crossmatch_collection = db["crossmatch_tests"]
transplantation_collection = db["transplantations"]


# Helper function to convert dates
def convert_dates(obj):
    if isinstance(obj, list):
        return [convert_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, date) and not isinstance(obj, datetime):
        return datetime.combine(obj, datetime.min.time())
    return obj


# Helper function to serialize MongoDB document
def serialize_crossmatch(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
        doc["transplantation_id"] = str(doc["transplantation_id"])
    return doc


# Create a new crossmatch test
@router.post("/", dependencies=[Depends(nephrologist_or_admin)])
def create_crossmatch_test(test: CrossmatchTest):
    data = test.dict()
    data = convert_dates(data)
    
    try:
        transplantation_id = ObjectId(data["transplantation_id"])
    except:
        raise HTTPException(status_code=400, detail="Invalid transplantation_id")
    
    # Verify transplantation exists
    if not transplantation_collection.find_one({"_id": transplantation_id}):
        raise HTTPException(status_code=404, detail="Transplantation not found")
    
    data["transplantation_id"] = transplantation_id
    
    result = crossmatch_collection.insert_one(data)
    
    return {
        "message": "Crossmatch test created successfully",
        "id": str(result.inserted_id)
    }


# Get all crossmatch tests
@router.get("/", dependencies=[Depends(nephrologist_or_admin)])
def get_all_crossmatch_tests():
    tests = list(crossmatch_collection.find())
    for test in tests:
        test["_id"] = str(test["_id"])
        test["transplantation_id"] = str(test["transplantation_id"])
    return tests


# Get crossmatch tests by transplantation ID
@router.get("/by-transplantation/{transplantation_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_crossmatch_tests_by_transplantation(transplantation_id: str):
    try:
        obj_id = ObjectId(transplantation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid transplantation ID")
    
    tests = list(crossmatch_collection.find({"transplantation_id": obj_id}))
    
    for test in tests:
        test["_id"] = str(test["_id"])
        test["transplantation_id"] = str(test["transplantation_id"])
    
    return tests


# Get a single crossmatch test by ID
@router.get("/{test_id}", dependencies=[Depends(nephrologist_or_admin)])
def get_crossmatch_test(test_id: str):
    try:
        obj_id = ObjectId(test_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid test ID")
    
    test = crossmatch_collection.find_one({"_id": obj_id})
    
    if not test:
        raise HTTPException(status_code=404, detail="Crossmatch test not found")
    
    test["_id"] = str(test["_id"])
    test["transplantation_id"] = str(test["transplantation_id"])
    
    return test


# Update a crossmatch test
@router.patch("/{test_id}", dependencies=[Depends(nephrologist_or_admin)])
def update_crossmatch_test(test_id: str, updates: dict):
    try:
        obj_id = ObjectId(test_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid test ID")
    
    # Remove internal fields
    updates.pop("_id", None)
    
    # Convert dates
    updates = convert_dates(updates)
    
    # If transplantation_id is being updated, convert it
    if "transplantation_id" in updates:
        try:
            updates["transplantation_id"] = ObjectId(updates["transplantation_id"])
        except:
            raise HTTPException(status_code=400, detail="Invalid transplantation_id")
    
    result = crossmatch_collection.update_one(
        {"_id": obj_id},
        {"$set": updates}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Crossmatch test not found")
    
    return {"message": "Crossmatch test updated successfully"}


# Delete a crossmatch test
@router.delete("/{test_id}", dependencies=[Depends(nephrologist_or_admin)])
def delete_crossmatch_test(test_id: str):
    try:
        obj_id = ObjectId(test_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid test ID")
    
    result = crossmatch_collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Crossmatch test not found")
    
    return {"message": "Crossmatch test deleted successfully"}