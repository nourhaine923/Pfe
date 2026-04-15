from pydantic import BaseModel
from typing import Optional
from datetime import date


class ImmunosuppressionRegimen(BaseModel):
    startDate: date
    endDate: Optional[date] = None

    corticosteroids: bool
    mmf: bool
    azathioprine: bool
    tacrolimus: bool
    ciclosporine: bool
    sirolimus: bool

    # Reference to follow up 
    followup_id: str
