import os
import json
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin.exceptions import FirebaseError


class FireStore():

    def __init__(self):
        """Initialize Firestore."""
        try:
            # Get the Firestore key from the environment variable
            credentials_content = os.getenv("FIRESTORE_USER")
            if not credentials_content:
                raise EnvironmentError(
                    "FIRESTORE_USER environment variable not set.")

            # Determine if it's a file path or JSON string
            try:
                cred_dict = json.loads(credentials_content)
                cred = credentials.Certificate(cred_dict)
            except json.JSONDecodeError:
                if os.path.exists(credentials_content):  # Local: It's a file path
                    cred = credentials.Certificate(credentials_content)
                else:
                    raise ValueError("Invalid credentials content: not a valid JSON string or file path")

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
