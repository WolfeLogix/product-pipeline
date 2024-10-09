"""This module contains the pydantic models for the tshirt resource"""
from pydantic import BaseModel


class TshirtFromAi(BaseModel):
    """A pydantic model for ai generated fields"""
    title: str
    description: str
    # tshirt_text is the text that will be printed on the tshirt
    tshirt_text: str
    marketing_tags: list[str]


class TshirtFromAiList(BaseModel):
    """A pydantic model for a list of ai generated fields"""
    patterns: list[TshirtFromAi]
