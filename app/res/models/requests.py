from typing import Optional

from pydantic import BaseModel

from res.models.objects import ProductQueue


class PatternRequest(BaseModel):
    patterns: Optional[int] = 3
    idea: str


class PatternQueueRequest(BaseModel):
    queue: list[ProductQueue]
