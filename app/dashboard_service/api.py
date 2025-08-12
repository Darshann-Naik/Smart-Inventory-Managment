# /app/dashboard_service/api.py
import uuid
from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db_session
from app.user_service.dependencies import get_current_active_user, require_role
from . import schemas, services

router = APIRouter()

@router.get(
    "/kpi-summary",
    response_model=schemas.KPISummary,
    summary="Get Key Performance Indicator Summary",
    dependencies=[Depends(require_role(["admin", "super_admin"]))]
)
async def get_kpi_summary(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Provides a high-level snapshot of key business metrics for a store."""
    return await services.get_kpi_summary(db, store_id)

@router.get(
    "/sales-over-time",
    response_model=List[schemas.TimeSeriesDataPoint],
    summary="Get Sales Data Over a Time Period",
    dependencies=[Depends(require_role(["admin", "super_admin"]))]
)
async def get_sales_over_time(
    store_id: uuid.UUID,
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db_session)
):
    """Returns time-series data for sales revenue, suitable for charts."""
    return await services.get_sales_over_time(db, store_id, start_date, end_date)

@router.get(
    "/top-performing-products",
    response_model=List[schemas.ProductPerformance],
    summary="Get Top Performing Products",
    dependencies=[Depends(require_role(["admin", "super_admin"]))]
)
async def get_top_performing_products(
    store_id: uuid.UUID,
    limit: int = Query(5, ge=1, le=50, description="Number of products to return"),
    sort_by: str = Query("revenue", enum=["revenue", "units_sold"]),
    db: AsyncSession = Depends(get_db_session)
):
    """Lists the best-selling products by revenue or units sold."""
    return await services.get_top_performing_products(db, store_id, limit, sort_by)

@router.get(
    "/low-stock-products",
    response_model=List[schemas.LowStockProduct],
    summary="Get Products with Low Stock",
    dependencies=[Depends(require_role(["admin", "super_admin"]))]
)
async def get_low_stock_products(
    store_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
):
    """Identifies products that are at or below their reorder point."""
    return await services.get_low_stock_products(db, store_id, page, size)

