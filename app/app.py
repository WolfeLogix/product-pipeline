from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from endpoints import products, healthcheck
from database.firebase import initialize_firestore

# Load environment variables from .env file
load_dotenv('.env')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Firestore and store it in app state
    app.state.firestore_db = initialize_firestore()
    print("Firestore initialized at startup.")
    yield
    # Terminate Firestore connection
    app.state.firestore_db.close()
    print("Application shutdown.")

# Initialize FastAPI with the lifespan context manager
app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(products.router)
app.include_router(healthcheck.router)
