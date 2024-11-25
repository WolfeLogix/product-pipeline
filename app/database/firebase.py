import os
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin.exceptions import FirebaseError


class FireStore():

    def __init__(self):
        """Initialize Firestore."""
        try:
            # Ensure the environment variable is set
            credentials_path = os.getenv("GCP_FIRESTORE_KEY")
            if not credentials_path:
                raise EnvironmentError(
                    "GCP_FIRESTORE_KEY environment variable not set."
                )

            cred = credentials.Certificate(credentials_path)
            initialize_app(cred)
            db = firestore.client()
            print("Successfully connected to Firestore.")
            self.db = db
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
