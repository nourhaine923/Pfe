from pydantic import BaseModel
from datetime import date
from typing import Optional


class CrossmatchTest(BaseModel):
    testDate: date
    methode: str   # CDC, FlowCytometry, Virtual
    result: str    # Positive, Negative
    comment: Optional[str] = None

    # Reference
    transplantation_id: str
