from pydantic import BaseModel
from datetime import date

from app.schemas.pretransplant_assessment import PreTransplantAssessment


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
