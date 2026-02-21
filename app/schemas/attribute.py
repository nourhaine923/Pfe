from pydantic import BaseModel


class Attribute(BaseModel):
    label: str

    # Reference to barem document
    barem_id: str
