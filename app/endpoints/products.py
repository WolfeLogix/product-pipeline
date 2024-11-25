from datetime import datetime

from fastapi import APIRouter, Depends

from database.firebase import FireStore
from services.pattern_services import process_patterns_and_idea
from services.shopify_services import set_taxonomy_nodeID
from services.database_services import (
    write_tshirt_to_firestore,
    add_to_queue,
    pop_from_queue
)
from res.models.objects import TshirtWithIds, QueueItem
from res.models.requests import PatternRequest, PatternQueueRequest
from res.models.responses import PatternResponse
from middleware.security import verify_api_key

router = APIRouter()


@router.post("/process_patterns", response_model=PatternResponse)
def process_patterns(request: PatternRequest, api_key: str = Depends(verify_api_key)):
    """This endpoint creates the patterns with ideas provided by the user."""
    patterns = process_patterns_and_idea(
        request.patterns, request.idea)

    # Initialize Firestore
    firestore = FireStore()

    response_patterns = []
    for pattern in patterns:
        shirt = TshirtWithIds(**pattern)
        response_patterns.append(shirt)
        write_tshirt_to_firestore(firestore.db, shirt)

    return PatternResponse(
        message="Generated Patterns Successfully",
        patterns=response_patterns
    )


@router.get("/fix_tax_category")
def correct_taxonomy():
    message = set_taxonomy_nodeID()
    return {"message": message}


@router.post("/pattern_queue")
def add_patterns_to_queue(request: PatternQueueRequest, api_key: str = Depends(verify_api_key)):
    """This endpoint adds the patterns to the queue."""

    # Initialize Firestore
    firestore = FireStore()

    try:
        for pattern in request.queue:
            queue_item = QueueItem(
                idea=pattern.idea,
                patterns=pattern.patterns,
                timestamp=datetime.now()
            )
            add_to_queue(firestore.db, queue_item)
        return {"message": f"Added {len(request.queue)} items to queue"}
    except Exception:
        return {"message": "Error adding to queue"}


@router.get("/pattern_queue")
def process_pattern_queue(api_key: str = Depends(verify_api_key)):
    """This endpoint processes the pattern queue."""
    # Initialize Firestore
    firestore = FireStore()
    pattern_to_be = pop_from_queue(firestore.db)

    patterns = process_patterns_and_idea(
        pattern_to_be.patterns,
        pattern_to_be.idea
    )

    response_patterns = []
    for pattern in patterns:
        shirt = TshirtWithIds(**pattern)
        response_patterns.append(shirt)
        write_tshirt_to_firestore(firestore.db, shirt)

    return PatternResponse(
        message="Generated Patterns Successfully",
        patterns=response_patterns
    )
