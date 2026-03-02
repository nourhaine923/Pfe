from pydantic import BaseModel
from typing import List, Union, Optional


class Condition(BaseModel):
    operator: Optional[str] = None   # used for conditional
    value: Union[int, float, str, bool, List[Union[int, float]]]
    impact: int


class ValueRule(BaseModel):
    type: str  # "conditional" | "boolean" | "categorical"
    conditions: List[Condition]


class Barem(BaseModel):
    score: str
    key: str
    values: List[ValueRule]