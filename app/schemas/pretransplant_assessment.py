from typing_extensions import Optional
from pydantic import BaseModel
from datetime import date


class PreTransplantAssessment(BaseModel):
    ageAtTransplant: int
    diabetes: bool
    hypertension: bool
    hbsAg: bool
    antiHCV: bool
    transfusion: bool
    acc: bool
    nephropathyType: str
    etiologyIRC: str
    eerModality: str
    eerStartDate: date
    trDelayMonths: int
    numberOfPreviousTransplants: int
    serumCreatinine: float