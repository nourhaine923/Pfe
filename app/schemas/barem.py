from pydantic import BaseModel


class Barem(BaseModel):
    key: str
    label: str
    impact: int
    condition: str