from typing import Optional, Dict

from pydantic import BaseModel

from res.models.tshirt import TshirtWithIds


class PatternResponse(BaseModel):
    message: str
    patterns: list[TshirtWithIds]


class HealthcheckResponse(BaseModel):
    status: str
    details: Optional[Dict[str, str]] = None
