from pydantic import BaseModel

class HLATyping(BaseModel):
    hlaA1: str
    hlaA2: str
    hlaB1: str
    hlaB2: str
    hlaDR1: str
    hlaDR2: str
    hlaDQ1: str
    hlaDQ2: str
