from pydantic import BaseModel
from typing import Optional
from datetime import date


class BiologicalMeasurement(BaseModel):
    date: date

    creatinine: Optional[float] = None
    urea: Optional[float] = None
    gfr: Optional[float] = None
    hemoglobin: Optional[float] = None
    crp: Optional[float] = None
    tsh: Optional[float] = None
    proteinuria: Optional[float] = None

    otherBioMarker1: Optional[float] = None
    otherBioMarker2: Optional[float] = None

    # Reference to FollowUp
    followup_id: str
