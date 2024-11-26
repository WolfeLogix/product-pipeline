
# Import FastAPI and endpoints
from endpoints import products
from endpoints import healthcheck

from dotenv import load_dotenv
from fastapi import FastAPI

from database.firebase import initialize_firestore


# Load environment variables from .env file
load_dotenv('.env')

# Initialize FastAPI
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    # Initialize Firestore and store it in app state
    app.state.firestore_db = initialize_firestore()
    print("Firestore initialized at startup.")

app.include_router(products.router)
app.include_router(healthcheck.router)
