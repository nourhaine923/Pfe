from pydantic import BaseModel
from typing import Optional
from datetime import date


class FollowUp(BaseModel):
    visitDate: date
    postTransplantDay: int
    postTransplantMonth: int

    visitType: str
    clinicalStatus: str
    comment: Optional[str] = None
    nephropathyRecurrence: str

    # Reference to Transplantation
    transplantation_id: str

    # Reference to ImmunosuppressionRegimen
    immunosuppression_regimen_id: str
