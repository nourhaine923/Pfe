from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

from app.schemas.pretransplant_assessment import PreTransplantAssessment

class TransplantStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Transplantation(BaseModel):
    transplantNumber: str
    transplantDate: date
    transplantLocation: str
    serviceOrigin: str

    coldIschemiaHours: float
    warmIschemiaMinutes: float

    # References (will be converted to ObjectId in routes)
    recipient_id: str
    donor_id: str

    # Embedded document
    preTransplantAssessment: PreTransplantAssessment
    
    # Status field with default value
    status: TransplantStatus = TransplantStatus.PENDING