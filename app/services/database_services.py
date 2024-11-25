"""This file handles database operations."""
from res.models.tshirt import TshirtWithIds


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
