from typing import Optional

from pydantic import BaseModel

from res.models.objects import ProductQueue


class PatternRequest(BaseModel):
    patterns: Optional[int] = 3
    idea: str
    publish: Optional[bool] = False


class PatternQueuePostRequest(BaseModel):
    queue: list[ProductQueue]
