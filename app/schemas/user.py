from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    doctor = "doctor"
    admin = "admin"
    researcher = "researcher"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str