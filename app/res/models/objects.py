"""This module contains the pydantic models for the tshirt resource"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TshirtFromAi(BaseModel):
    """A pydantic model for ai generated fields"""
    product_name: str
    description: str
    # tshirt_text is the text that will be printed on the tshirt
    tshirt_text: str
    marketing_tags: list[str]


class TshirtFromAiList(BaseModel):
    """A pydantic model for a list of ai generated fields"""
    patterns: list[TshirtFromAi]


class TshirtWithIds(TshirtFromAi):
    """A pydantic model that extends TshirtFromAi with a product_id"""
    product_id: str
    image_ids: list[str]


class ProductQueue(BaseModel):
    """inputs needed to trigger the product pipeline."""
    idea: str
    patterns: Optional[int] = 10


class QueueItem(ProductQueue):
    """A pydantic model that extends ProductQueue with a timestamp"""
    timestamp: datetime
