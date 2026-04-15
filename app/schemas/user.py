from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum
from typing import Optional
from datetime import datetime

class UserRole(str, Enum):
    NEPHROLOGIST = "NEPHROLOGIST"
    ADMIN = "ADMIN"
    RESEARCHER = "RESEARCHER"
    
    @classmethod
    def _missing_(cls, value):
        """Make enum case-insensitive"""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.upper():
                    return member
        return None


class UserStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.NEPHROLOGIST
    
    @validator('role', pre=True)
    def validate_role(cls, v):
        """Convert role to uppercase before validation"""
        if isinstance(v, str):
            return v.upper()
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Normalize email to lowercase"""
        if v:
            return v.lower()
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        """Normalize email to lowercase"""
        if v:
            return v.lower()
        return v


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    status: UserStatus
    isApproved: bool
    createdAt: datetime
    updatedAt: Optional[datetime] = None