from pydantic import BaseModel
from datetime import datetime


class Score(BaseModel):
    scoreType: str      # Pre-transplant | Post-transplant | Emergency
    value: int          # computed score
    calculatedAt: datetime

    # Reference to Transplantation
    transplantation_id: str | None = None
 