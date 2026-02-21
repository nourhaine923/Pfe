from pydantic import BaseModel
from typing import Optional
from datetime import date


class AdverseEvent(BaseModel):
    eventType: str
    severity: str
    date: date
    comment: Optional[str] = None
    infectionSeverity: Optional[str] = None
    infectionType: Optional[str] = None

    # Correct relationship: belongs to FollowUp
    followup_id: str
