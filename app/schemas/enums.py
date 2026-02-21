from enum import Enum

class Sex(str, Enum):
    M = "M"
    F = "F"

class BloodGroup(str, Enum):
    O = "O"
    A = "A"
    B = "B"
    AB = "AB"
