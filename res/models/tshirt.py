from pydantic import BaseModel

class tshirt_from_ai(BaseModel):
    """A pydantic model for ai generated fields"""
    title: str
    description: str
    # tshirt_text is the text that will be printed on the tshirt
    tshirt_text: str
    marketing_tags: list[str]

class tshirt_from_ai_list(BaseModel):
    """A pydantic model for a list of ai generated fields"""
    patterns: list[tshirt_from_ai]
