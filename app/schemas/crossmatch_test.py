from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class CrossmatchMethod(str, Enum):
    CDC = "CDC"
    FLOW_CYTOMETRY = "FlowCytometry"
    VIRTUAL = "Virtual"

class CrossmatchResult(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"

class CrossmatchTest(BaseModel):
    testDate: date
    methode: CrossmatchMethod
    result: CrossmatchResult
    comment: Optional[str] = None
    
    # Reference to Transplantation
    transplantation_id: str