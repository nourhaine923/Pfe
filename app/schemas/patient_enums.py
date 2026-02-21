from enum import Enum

class PatientRole(str, Enum):
    DONOR = "Donor"
    RECIPIENT = "Recipient"
