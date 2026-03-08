from fastapi import APIRouter, HTTPException
from app.database import db
from app.schemas.user import UserCreate, UserLogin
from app.auth.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

users_collection = db["users"]


# ------------------------
# REGISTER
# ------------------------
@router.post("/register")
def register(user: UserCreate):

    existing_user = users_collection.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user_data = {
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role.value
    }

    users_collection.insert_one(user_data)

    return {"message": "User registered successfully"}


# ------------------------
# LOGIN
# ------------------------
@router.post("/login")
def login(user: UserLogin):

    db_user = users_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found. Please register.")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(db_user["email"], db_user["role"])

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }