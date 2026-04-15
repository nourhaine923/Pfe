from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
from typing import List
from app.database import db
from app.schemas.user import UserStatus
from app.auth.dependencies import admin_required

router = APIRouter(prefix="/admin", tags=["Admin"])

users_collection = db["users"]

# Get all users (admin only)
@router.get("/users", dependencies=[Depends(admin_required)])
def get_all_users():
    users = list(users_collection.find().sort("createdAt", -1))
    
    for user in users:
        user["_id"] = str(user["_id"])
        user.pop("password", None)  # Remove password field
    
    return users

# Get pending users only
@router.get("/users/pending", dependencies=[Depends(admin_required)])
def get_pending_users():
    users = list(users_collection.find(
        {"status": UserStatus.PENDING}
    ).sort("createdAt", 1))
    
    for user in users:
        user["_id"] = str(user["_id"])
        user.pop("password", None)
    
    return users

# Get user by ID
@router.get("/users/{user_id}", dependencies=[Depends(admin_required)])
def get_user(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = users_collection.find_one({"_id": obj_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.pop("password", None)
    user["_id"] = str(user["_id"])
    
    return user

# Get statistics about users
@router.get("/stats", dependencies=[Depends(admin_required)])
def get_user_stats():
    total_users = users_collection.count_documents({})
    pending_users = users_collection.count_documents({"status": UserStatus.PENDING})
    approved_users = users_collection.count_documents({"status": UserStatus.APPROVED})
    rejected_users = users_collection.count_documents({"status": UserStatus.REJECTED})
    
    return {
        "total": total_users,
        "pending": pending_users,
        "approved": approved_users,
        "rejected": rejected_users
    }

# Approve user account
@router.patch("/users/{user_id}/approve", dependencies=[Depends(admin_required)])
def approve_user(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = users_collection.find_one({"_id": obj_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["status"] == UserStatus.APPROVED:
        raise HTTPException(status_code=400, detail="User is already approved")
    
    # Update user status
    result = users_collection.update_one(
        {"_id": obj_id},
        {
            "$set": {
                "status": UserStatus.APPROVED,
                "isApproved": True,
                "approvedAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to approve user")
    
    # TODO: Send approval email to user
    # from app.services.email_service import send_approval_email
    # send_approval_email(user["email"])
    
    return {
        "message": f"User {user['email']} has been approved successfully",
        "user_id": user_id,
        "status": UserStatus.APPROVED
    }

# Reject user account
@router.patch("/users/{user_id}/reject", dependencies=[Depends(admin_required)])
def reject_user(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = users_collection.find_one({"_id": obj_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["status"] == UserStatus.REJECTED:
        raise HTTPException(status_code=400, detail="User is already rejected")
    
    # Update user status
    result = users_collection.update_one(
        {"_id": obj_id},
        {
            "$set": {
                "status": UserStatus.REJECTED,
                "isApproved": False,
                "rejectedAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to reject user")
    
    # TODO: Send rejection email to user
    # from app.services.email_service import send_rejection_email
    # send_rejection_email(user["email"])
    
    return {
        "message": f"User {user['email']} has been rejected",
        "user_id": user_id,
        "status": UserStatus.REJECTED
    }

# Delete user account
@router.delete("/users/{user_id}", dependencies=[Depends(admin_required)])
def delete_user(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = users_collection.find_one({"_id": obj_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = users_collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete user")
    
    return {
        "message": f"User {user['email']} has been deleted successfully"
    }