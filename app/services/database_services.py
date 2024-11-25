"""This file handles database operations."""
from res.models.objects import TshirtWithIds, ProductQueue


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


def add_to_queue(db, queue: ProductQueue):
    """Write a ProductQueue object to Firestore."""
    try:
        # Write the ProductQueue object to Firestore
        doc_ref = db.collection("ProductQueue").document()
        doc_ref.set(queue.dict())
        print("Successfully wrote product queue to Firestore")
    except Exception as e:
        print(f"Error writing ProductQueue to Firestore: {e}")
        raise
