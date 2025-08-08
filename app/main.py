# /app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# This custom router is essential for consistent success responses
from core.router import StandardAPIRouter
from core.schemas import ErrorResponse, ErrorDetail
from core.config import settings
from core.exceptions import APIException
from core.logging import setup_logging

# Import all the service routers
from app.user_service.api import router as user_router
from app.store_service.api import router as store_router
from app.category_service.api import router as category_router
from app.product_service.api import router as product_router
from app.inventory_service.api import router as inventory_router
from app.transaction_service.api import router as transaction_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    """
    print("--- Initializing services... ---")
    setup_logging()
    # In a real application, you would initialize database connections,
    # Redis pools, etc. here.
    print("--- Application startup complete. ---")
    yield
    print("--- Application shutdown. ---")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    debug=settings.DEBUG,
    lifespan=lifespan
)

logger = logging.getLogger(__name__)

# Exception handler for custom API exceptions
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    error_detail = ErrorDetail(
        status=str(exc.status_code),
        title=exc.title,
        detail=exc.detail
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(errors=[error_detail]).model_dump(),
    )

# Fallback exception handler for any unhandled errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    error_detail = ErrorDetail(
        status=str(status.HTTP_500_INTERNAL_SERVER_ERROR),
        title="Internal Server Error",
        detail="An unexpected error occurred. Please try again later."
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(errors=[error_detail]).model_dump(),
    )

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Main API Router Setup ---
# Create a single main router that will aggregate all service routers
api_router = StandardAPIRouter()

# Include each service's router with a specific prefix and tags
api_router.include_router(user_router, prefix="/users", tags=["Authentication & Users"])
api_router.include_router(store_router, prefix="/stores", tags=["Stores"])
api_router.include_router(category_router, prefix="/categories", tags=["Product Categories (Admin)"])
api_router.include_router(product_router, prefix="/products", tags=["Product Management"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["Inventory Management"])
api_router.include_router(transaction_router, prefix="/transactions", tags=["Transaction Management"])

# Include the single main router into the app with the global API version prefix
app.include_router(api_router, prefix=settings.API_V1_STR)
# --- End Router Setup ---

@app.get("/healthz", tags=["Health Check"])
async def health_check():
    """
    A simple health check endpoint to confirm the API is running.
    """
    logger.info("Health check endpoint was called.")
    return {"status": "ok"}
