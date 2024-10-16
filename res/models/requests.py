from typing import Optional

from pydantic import BaseModel


class PatternRequest(BaseModel):
    patterns: Optional[int] = 3
    idea: str
