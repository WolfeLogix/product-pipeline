"""This file handles database operations."""
from res.models.objects import TshirtWithIds, QueueItem


def write_tshirt_to_firestore(db, tshirt: TshirtWithIds):
    """Write a TshirtWithIds object to Firestore."""
    try:
        # Write the TshirtWithIds object to Firestore
        doc_ref = db.collection("Products").document(tshirt.product_id)
        doc_ref.set(tshirt.dict())
        print(f"Successfully wrote product to Firestore: {tshirt.product_id}")
    except Exception as e:
        print(f"Error writing TshirtWithIds to Firestore: {e}")
        raise


def add_to_queue(db, queue: QueueItem):
    """Write a ProductQueue object to Firestore."""
    try:
        # Write the ProductQueue object to Firestore
        doc_ref = db.collection("ProductQueue").document()
        doc_ref.set(queue.dict())
        print("Successfully wrote product queue to Firestore")
    except Exception as e:
        print(f"Error writing ProductQueue to Firestore: {e}")
        raise


def pop_from_queue(db):
    """Return and remove the oldest ProductQueue object from Firestore."""
    # Get the oldest ProductQueue object from Firestore
    queue_ref = db.collection("ProductQueue").order_by("timestamp").limit(1)
    queue = queue_ref.get()

    if queue:
        # Delete the oldest ProductQueue object from Firestore
        db.collection("ProductQueue").document(queue[0].id).delete()
        return QueueItem(**queue[0].to_dict())
    return None


def count_collection(db, collection_name: str):
    """Return the number of ProductQueue objects in Firestore."""
    queue_ref = db.collection(collection_name)
    queue = queue_ref.get()
    return len(queue)
