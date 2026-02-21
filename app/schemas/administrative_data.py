from pydantic import BaseModel
from typing import Optional


class AdministrativeData(BaseModel):
    printing_flag: bool = False
    validation_status: Optional[str] = None
    comments: Optional[str] = None
