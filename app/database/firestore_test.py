"""THIS FILE EXISTS TEMPORARILY TO REFERENCE WHILE DEVELOPING THE FIRESTORE DATABASE"""


import os
from firebase_admin import credentials, firestore, initialize_app


def initialize_firestore():
    try:
        # Ensure the environment variable is set
        credentials_path = os.getenv("GCP_FIRESTORE_KEY")
        if not credentials_path:
            raise EnvironmentError(
                "GCP_FIRESTORE_KEY environment variable not set.")

        cred = credentials.Certificate(credentials_path)
        initialize_app(cred)
        db = firestore.client()
        print("Successfully connected to Firestore.")
        return db
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        raise


def test_firestore_connection(db):
    collection_name = "test"
    test_data = {"test_field": "Hello, Firestore!"}

    try:
        # Write a test document
        print("Writing a test document...")
        doc_ref = db.collection(collection_name).document("test_document")
        doc_ref.set(test_data)
        print("Test document written successfully.")

        # Read the test document
        print("Reading the test document...")
        doc = doc_ref.get()
        if doc.exists:
            print("Test document read successfully:", doc.to_dict())
        else:
            print("Test document not found.")

        # Delete the test document
        print("Deleting the test document...")
        doc_ref.delete()
        print("Test document deleted successfully.")
    except Exception as e:
        print(f"Error during Firestore operations: {e}")
        raise


if __name__ == "__main__":
    try:
        db = initialize_firestore()
        test_firestore_connection(db)
    except Exception as e:
        print("Firestore test failed:", e)
