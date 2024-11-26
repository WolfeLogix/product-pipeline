import os

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from requests import get

from database.firebase import get_firestore_db, firestore_healthcheck
from util.printify.printify_util import PrintifyUtil
from util.shopify_util import ShopifyUtil
from util.ai_util import AiUtil
from res.models.responses import HealthcheckResponse
from middleware.security import verify_api_key

router = APIRouter()


@router.get("/", response_model=HealthcheckResponse,
            response_model_exclude_none=True)
@router.get("/healthcheck", response_model=HealthcheckResponse,
            response_model_exclude_none=True)
def healthcheck():
    """This is a basic status check to see if the API is running."""
    return HealthcheckResponse(
        status="OK"
    )


@router.get("/full_healthcheck", response_model=HealthcheckResponse)
def full_healthcheck(
    api_key: str = Depends(verify_api_key),
    firestore_db=Depends(get_firestore_db)
):
    """This endpoint checks the status of all services used by the API."""
    services_status = {
        "printify": "Unknown",
        "shopify": "Unknown",
        "openai": "Unknown",
        "github": "Unknown",
        "firestore": "Unknown"
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

    # Check Shopify
    try:
        shopify = ShopifyUtil()
        try:
            services_status["shopify"] = shopify.healthcheck()
        except Exception as e:
            services_status["shopify"] = f"Error {str(e)}"
    except Exception as e:
        services_status["shopify"] = f"Exception {str(e)}"

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

    # Check Firestore
    try:
        status = firestore_healthcheck(firestore_db)
        services_status["firestore"] = status
    except Exception:
        services_status["firestore"] = "Error: check logs"

    response = HealthcheckResponse(
        status="OK" if all(
            status == "OK" for status in services_status.values()) else "Error",
        details=services_status
    )
    status_code = 200 if response.status == "OK" else 503
    return JSONResponse(content=response.model_dump(), status_code=status_code)


@router.get("/healthcheck/db")
def db_healthcheck(
    api_key: str = Depends(verify_api_key),
    firestore_db=Depends(get_firestore_db)
):
    """Check the health of Firestore."""
    try:
        status = firestore_healthcheck(firestore_db)
        return {"status": status}
    except Exception:
        return {"status": "error", "details": "An error has occurred, check the logs"}
