from fastapi import APIRouter, Depends

from services.pattern_services import process_patterns_and_idea
from services.shopify_services import set_taxonomy_nodeID
from res.models.tshirt import TshirtWithIds
from res.models.requests import PatternRequest
from res.models.responses import PatternResponse
from middleware.security import verify_api_key

router = APIRouter()


@router.post("/process_patterns", response_model=PatternResponse)
def process_patterns(request: PatternRequest, api_key: str = Depends(verify_api_key)):
    """This endpoint creates the patterns with ideas provided by the user."""
    patterns = process_patterns_and_idea(
        request.patterns, request.idea)

    response_patterns = []
    for pattern in patterns:
        response_patterns.append(TshirtWithIds(**pattern))

    return PatternResponse(
        message="Generated Patterns Successfully",
        patterns=response_patterns
    )


@router.get("/fix_tax_category")
def correct_taxonomy():
    message = set_taxonomy_nodeID()
    return {"message": message}
