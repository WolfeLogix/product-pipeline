
# Import FastAPI and endpoints
from endpoints import products
from endpoints import healthcheck

from dotenv import load_dotenv
from fastapi import FastAPI

from database.firebase import FireStore


# Load environment variables from .env file
load_dotenv('.env')

# Initialize FastAPI
app = FastAPI()
app.include_router(products.router)
app.include_router(healthcheck.router)


