from pydantic import BaseModel
from typing import Optional
from datetime import date


class TherapeuticTreatment(BaseModel):
    drugName: str
    dosage: float
    dosageUnit: str
    route: str

    startDate: date
    endDate: Optional[date] = None

    bloodLevel: Optional[float] = None
    interpretation: Optional[str] = None

    # Reference to FollowUp
    followup_id: str

