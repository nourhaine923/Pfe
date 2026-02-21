from pydantic import BaseModel


class ImmunologicalMarker(BaseModel):
    markerType: str
    timePoint: str
    value: float
    unit: str

    # Reference to FollowUp
    followup_id: str
