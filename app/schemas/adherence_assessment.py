from pydantic import BaseModel
from datetime import date


class AdherenceAssessment(BaseModel):
    date: date
    adherencePercent: float
    method: str

    # Reference
    followup_id: str
