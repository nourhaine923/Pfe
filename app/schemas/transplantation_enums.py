from enum import Enum

class TransplantLocation(str, Enum):
    HCN = "HCN"
    RABTA = "RABTA"
    HMPIT = "HMPIT"
    MONASTIR = "MONASTIR"
    SOUSSE = "SOUSSE"
    SFAX = "SFAX"

class ServiceOrigin(str, Enum):
    Nephrology_HCN = "Nephrology_HCN"
    Pediatrics_HCN = "Pediatrics_HCN"
    RABTA = "RABTA"
    MONASTIR = "MONASTIR"
    SOUSSE = "SOUSSE"
