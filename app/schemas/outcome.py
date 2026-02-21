from pydantic import BaseModel
from datetime import date


class Outcome(BaseModel):
    lastNewsDate: date

    aliveWithFunctioningGraft: bool
    returnToDialysis: bool
    deathWithFunctioningGraft: bool
    lostToFollowUp: bool
    delayedGraftFunction: bool

    # Reference to Transplantation
    transplantation_id: str
