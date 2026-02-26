from pydantic import BaseModel
from datetime import date


class RejectionEpisode(BaseModel):
    date: date
    type: str           # Cellular | AntibodyMediated | Mixed
    grade: str          # Banff classification
    biopsyProven: bool
    treatment: str
    resolved: bool

    # Reference to FollowUp
    followup_id: str