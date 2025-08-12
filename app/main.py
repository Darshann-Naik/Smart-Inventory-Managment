# /app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

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
from app.store_product_service.api import router as store_product_router
from app.transaction_service.api import router as transaction_router

from app.ml_service.api import router as ml_router
# CORRECTED: The inventory_service import has been removed.

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Initializing services... ---")
    setup_logging()
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

# ... (Exception handlers and CORS middleware remain the same) ...
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Main API Router Setup ---
api_router = StandardAPIRouter()

api_router.include_router(user_router, prefix="/users", tags=["Authentication & Users"])
api_router.include_router(store_router, prefix="/stores", tags=["Stores"])
api_router.include_router(category_router, prefix="/categories", tags=["Product Categories (Admin)"])
api_router.include_router(product_router, prefix="/products", tags=["Products"])
api_router.include_router(store_product_router, tags=["Store-Product Links"])
api_router.include_router(transaction_router, prefix="/transactions", tags=["Transaction Management"])
api_router.include_router(ml_router, prefix="/ml", tags=["Machine Learning"])
# CORRECTED: The inventory_router inclusion has been removed.

app.include_router(api_router, prefix=settings.API_V1_STR)
# --- End Router Setup ---

@app.get("/healthz", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}
from app.main import app

for route in app.routes:
    print(route.path, route.methods)
