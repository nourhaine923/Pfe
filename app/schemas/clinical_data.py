from pydantic import BaseModel
from typing import Optional


class ClinicalData(BaseModel):
    age_at_transplant: Optional[int] = None
    blood_group: Optional[str] = None
    primary_nephropathy: Optional[str] = None
    dialysis_type: Optional[str] = None
    dialysis_duration: Optional[int] = None
    comorbidities: Optional[str] = None
    transplant_rank: Optional[int] = None
