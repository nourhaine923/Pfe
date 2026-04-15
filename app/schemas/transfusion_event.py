from pydantic import BaseModel
from datetime import date
from typing import Optional

class TransfusionEvent(BaseModel):
    transfusionDate: date
    units: int
    aboType: str
    indication: str
    
    # Reference to Patient
    patient_id: str