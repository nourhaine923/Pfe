from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from app.schemas.clinical_data import ClinicalData
from app.schemas.hla_typing import HLATyping
from app.schemas.administrative_data import AdministrativeData


class Patient(BaseModel):
    lastName: str
    firstName: str
    sex: str
    bloodGroup: str
    foreignPatient: bool
    heightCm: float
    weightKg: float

    # Role discriminator: "Donor" or "Recipient"
    patientRole: str

    # Donor-specific fields (only if role == Donor)
    donorType: Optional[str] = None
    ageAtDonation: Optional[int] = None

    # Recipient-specific fields (only if role == Recipient)
    birthDate: Optional[date] = None

    # Embedded documents
    clinicalData: Optional[ClinicalData] = None
    hlaTyping: Optional[HLATyping] = None

    # List of embedded administrative records
    administrativeData: Optional[List[AdministrativeData]] = []
