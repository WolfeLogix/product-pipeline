import os
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin.exceptions import FirebaseError


class FireStore:

    def __init__(self):
        """Initialize Firestore."""
        try:
            # Get the Firestore key from the environment variable
            credentials_path = os.getenv("GCP_FIRESTORE_KEY", None)
            cred = None
            if credentials_path:
                cred = credentials.Certificate(credentials_path)

            # Initialize Firestore
            initialize_app(cred)
            self.db = firestore.client()
            print("Successfully connected to Firestore.")
        except Exception as e:
            print(f"Error initializing Firestore: {e}")
            raise

    def healthcheck(self):
        """Check the health of Firestore."""
        try:
            # Arbitrary read operation to ensure Firestore connection
            test_collection = self.db.collection("test")
            test_document = test_collection.document("healthcheck")
            test_document.get()  # Attempt to fetch the document
            return {"status": "ok"}
        except FirebaseError as e:
            print(f"Firestore healthcheck failed: {e}")
            return {"status": "error", "details": str(e)}
        except Exception as e:
            print(f"Unexpected error during healthcheck: {e}")
            return {"status": "error", "details": "Unexpected error occurred."}
