from pydantic import BaseModel


class Barem(BaseModel):
    score: str      # SCORE_1, SCORE_2, SCORE_3
    key: str      # attribute name (hla_matching, diabetes, etc.)
    value: str        # category value (True, 0/6, >38°C, etc.)
    impact: int     # points assigned