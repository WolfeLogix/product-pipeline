import os
import random
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from requests import get

from services import process_patterns_and_idea
from util.printify.printify_util import PrintifyUtil
from util.ai_util import AiUtil
from res.models.tshirt import TshirtWithIds
from res.models.requests import PatternRequest
from res.models.responses import PatternResponse, HealthcheckResponse


# Load environment variables from .env file
load_dotenv('.env')

# Random Seeding
random.seed(int(datetime.now().timestamp()))

# Initialize FastAPI
app = FastAPI()

# Retrieve the API_KEY from environment variables
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set.")
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to verify the API key provided in the Authorization header.
    """
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@app.post("/process_patterns", response_model=PatternResponse)
def process_patterns(request: PatternRequest, api_key: str = Depends(verify_api_key)):
    """This endpoint creates the patterns with ideas provided by the user."""
    patterns = process_patterns_and_idea(
        request.patterns, request.idea)

    response_patterns = []
    for pattern in patterns:
        response_patterns.append(TshirtWithIds(**pattern))

    return PatternResponse(
        message="Generated Patterns Successfully",
        patterns=response_patterns
    )


@app.get("/", response_model=HealthcheckResponse,
         response_model_exclude_none=True)
@app.get("/healthcheck", response_model=HealthcheckResponse,
         response_model_exclude_none=True)
def healthcheck():
    """This is a basic status check to see if the API is running."""
    return HealthcheckResponse(
        status="OK"
    )


@app.get("/full_healthcheck", response_model=HealthcheckResponse)
def full_healthcheck(api_key: str = Depends(verify_api_key)):
    """This endpoint checks the status of all services used by the API."""
    services_status = {
        "printify": "Unknown",
        "openai": "Unknown",
        "github": "Unknown"
    }

    # Check Printify
    try:
        printify = PrintifyUtil()
        printify_response = printify.fetch_store_id()
        if printify_response is not None:
            services_status["printify"] = "OK"
        else:
            services_status["printify"] = f"Error {
                printify_response.status_code}"
    except Exception as e:
        services_status["printify"] = f"Exception {str(e)}"

    # Check OpenAI
    try:
        ai = AiUtil()
        try:
            services_status["openai"] = ai.status_check()
        except Exception as e:
            services_status["openai"] = f"Error {str(e)}"
    except Exception as e:
        services_status["openai"] = f"Exception {str(e)}"

    # Check GitHub
    try:
        github_response = get(
            "https://api.github.com/user/repos",
            headers={"Authorization": f"Bearer {os.getenv('GH_PAT')}"},
            timeout=10
        )
        if github_response.status_code == 200:
            services_status["github"] = "OK"
        else:
            services_status["github"] = f"Error {github_response.status_code}"
    except Exception as e:
        services_status["github"] = f"Exception {str(e)}"

    return HealthcheckResponse(
        status="OK" if all(
            status == "OK" for status in services_status.values()) else "Error",
        details=services_status
    )
