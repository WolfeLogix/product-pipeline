from pydantic import BaseModel

from res.models.tshirt import TshirtWithIds


class PatternResponse(BaseModel):
    message: str
    patterns: list[TshirtWithIds]


class HealthcheckResponse(BaseModel):
    status: str
