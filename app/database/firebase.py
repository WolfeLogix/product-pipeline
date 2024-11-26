import os

from fastapi import Request

from firebase_admin import credentials, firestore, initialize_app
from firebase_admin.exceptions import FirebaseError


def initialize_firestore():
    """Initialize and return the Firestore client."""
    try:
        # Get credentials from environment variable
        credentials_path = os.getenv("GCP_FIRESTORE_KEY")
        cred = credentials.Certificate(
            credentials_path) if credentials_path else None

        # Initialize Firebase app
        initialize_app(cred)
        db = firestore.client()
        print("Successfully connected to Firestore.")
        return db
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        raise


def firestore_healthcheck(db):
    """Check the health of Firestore."""
    try:
        # Arbitrary read operation to ensure Firestore connection
        test_collection = db.collection("test")
        test_document = test_collection.document("healthcheck")
        test_document.get()  # Attempt to fetch the document
        return "OK"
    except FirebaseError as e:
        print(f"Firestore healthcheck failed: {e}")
        return {"status": "error", "details": "A Firebase error occurred."}
    except Exception as e:
        print(f"Unexpected error during healthcheck: {e}")
        return {"status": "error", "details": "Unexpected error occurred."}


def get_firestore_db(request: Request):
    """Dependency to get Firestore client from app state."""
    return request.app.state.firestore_db
