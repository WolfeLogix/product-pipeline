from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

# from database.firebase import FireStore
from services.pattern_services import process_patterns_and_idea
from services.shopify_services import set_taxonomy_nodeID
from services.database_services import (
    write_tshirt_to_firestore,
    add_to_queue,
    pop_from_queue,
    count_collection
)
from database.firebase import get_firestore_db
from res.models.objects import TshirtWithIds, QueueItem
from res.models.requests import (
    PatternRequest,
    PatternQueuePostRequest,
    PatternQueueGetRequest
)
from res.models.responses import PatternResponse
from middleware.security import verify_api_key

router = APIRouter()


@router.post("/process_patterns",
             response_model=PatternResponse)
def process_patterns(
    request: PatternRequest,
    api_key: str = Depends(verify_api_key),
    firestore_db=Depends(get_firestore_db)
):
    """This endpoint creates the patterns with ideas provided by the user."""
    patterns = process_patterns_and_idea(
        request.patterns,
        request.idea,
        request.publish
    )

    response_patterns = []
    for pattern in patterns:
        shirt = TshirtWithIds(**pattern)
        response_patterns.append(shirt)
        write_tshirt_to_firestore(firestore_db, shirt)

    return PatternResponse(
        message="Generated Patterns Successfully",
        patterns=response_patterns
    )


@router.get("/fix_tax_category")
def correct_taxonomy():
    message = set_taxonomy_nodeID()
    return {"message": message}


@router.post("/pattern_queue")
def add_patterns_to_queue(
    request: PatternQueuePostRequest,
    api_key: str = Depends(verify_api_key),
    firestore_db=Depends(get_firestore_db)
):
    """This endpoint adds the patterns to the queue."""
    try:
        for pattern in request.queue:
            queue_item = QueueItem(
                idea=pattern.idea,
                patterns=pattern.patterns,
                timestamp=datetime.now()
            )
            add_to_queue(firestore_db, queue_item)
        return {"message": f"Added {len(request.queue)} items to queue"}
    except Exception:
        return {"message": "Error adding to queue"}


@router.get("/pattern_queue")
def process_pattern_queue(
    request: PatternQueueGetRequest,
    api_key: str = Depends(verify_api_key),
    firestore_db=Depends(get_firestore_db)
):
    """This endpoint processes the pattern queue."""

    pattern_to_be = pop_from_queue(firestore_db)

    if pattern_to_be is None:
        return JSONResponse(
            content={"message": "No items in queue"},
            status_code=404
        )

    return process_patterns(
        PatternRequest(
            patterns=pattern_to_be.patterns,
            idea=pattern_to_be.idea,
            publish=request.publish
        ),
        api_key=api_key,
        firestore_db=firestore_db
    )


@router.get("/pattern_queue/count")
def get_pattern_queue_count(
    api_key: str = Depends(verify_api_key),
    firestore_db=Depends(get_firestore_db)
):
    """This endpoint returns the number of items in the pattern queue."""
    count = count_collection(firestore_db, "ProductQueue")
    return JSONResponse(
        content={
            "message": f"There are {count} items in the queue",
            "count": count
        }
    )
