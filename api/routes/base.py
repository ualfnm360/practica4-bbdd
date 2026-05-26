from fastapi import APIRouter, status, Request

router = APIRouter()

# Define the root endpoint with HATEOAS links
@router.get("/")
async def root(request: Request):
    base = str(request.base_url).rstrip("/")

    return {
        "message": "Welcome to Products API",
        "_links": {
            "self": f"{base}/",
            "health": f"{base}/health",
            "docs": f"{base}/docs",
            "redoc": f"{base}/redoc",
            "openapi": f"{base}/openapi.json",
        }
    }

# Define a test API endpoint
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}