from pydantic import BaseModel
from datetime import date


class TransfusionEvent(BaseModel):
    date: date
    units: int
    aboType: str
    indication: str

    # Reference to Patient
    patient_id: str