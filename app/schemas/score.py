from pydantic import BaseModel
from datetime import datetime


class Score(BaseModel):
    scoreType: str      # SCORE_1 | SCORE_2 | SCORE_3
    value: int          # computed score
    calculatedAt: datetime

    transplantation_id: str | None = None
 