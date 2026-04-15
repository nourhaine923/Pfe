from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timedelta
import bcrypt
import jwt
from typing import Optional
import os

from app.database import db
from app.schemas.user import UserCreate, UserLogin, UserStatus

router = APIRouter(prefix="/auth", tags=["Authentication"])

users_collection = db["users"]

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token with expiration"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Register new user (always PENDING)
@router.post("/register")
def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user_data.email})
    
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already exists")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user document with PENDING status
    user_doc = {
        "email": user_data.email,
        "password": hashed_password,
        "role": user_data.role.value if hasattr(user_data.role, 'value') else user_data.role,
        "status": UserStatus.PENDING,
        "isApproved": False,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = users_collection.insert_one(user_doc)
    
    # Remove password from response
    user_doc["_id"] = str(result.inserted_id)
    user_doc.pop("password", None)
    
    return {
        "message": "Registration successful. Please wait for admin approval.",
        "user": user_doc
    }

# Login user (checks account status)
@router.post("/login")
def login(credentials: UserLogin):
    # Find user by email
    user = users_collection.find_one({"email": credentials.email})
    
    if not user:
        raise HTTPException(status_code=401, detail="Email not found")
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # Check account status
    if user["status"] == UserStatus.PENDING:
        raise HTTPException(
            status_code=403, 
            detail="ACCOUNT_PENDING"
        )
    
    if user["status"] == UserStatus.REJECTED:
        raise HTTPException(
            status_code=403, 
            detail="ACCOUNT_REJECTED"
        )
    
    # Create access token with status field
    token_data = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "status": user["status"],
        "isApproved": user["isApproved"]
    }
    
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "status": user["status"],
            "isApproved": user["isApproved"]
        }
    }