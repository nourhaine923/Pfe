from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VitalSigns(BaseModel):
    dateTime: datetime
    heartRate: int
    temperature: float
    oxygenSaturation: float
    urineOutputMl: float
    mentalStatus: str
    bloodPressure: float
    graftUltraSound: Optional[str] = None

    # Reference to FollowUp
    followup_id: str