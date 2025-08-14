# /app/dashboard_service/services.py
import uuid
from datetime import date
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas

async def get_kpi_summary(db: AsyncSession, store_id: uuid.UUID) -> schemas.KPISummary:
    """Service to orchestrate fetching and calculating KPI summary data."""
    kpi_data = await crud.get_kpi_summary(db, store_id)
    
    avg_transaction_value = 0
    if kpi_data["total_sales_transactions"] > 0:
        avg_transaction_value = kpi_data["total_revenue"] / kpi_data["total_sales_transactions"]
        
    return schemas.KPISummary(
        total_revenue=kpi_data["total_revenue"],
        total_sales_transactions=kpi_data["total_sales_transactions"],
        average_transaction_value=avg_transaction_value,
        total_products_in_stock=kpi_data["total_products_in_stock"]
    )

async def get_sales_over_time(db: AsyncSession, store_id: uuid.UUID, start_date: date, end_date: date) -> List[schemas.TimeSeriesDataPoint]:
    """Service to get sales data formatted for time-series charts."""
    sales_data = await crud.get_sales_over_time(db, store_id, start_date, end_date)
    return [schemas.TimeSeriesDataPoint(**data) for data in sales_data]

async def get_profit_summary(db: AsyncSession, store_id: uuid.UUID, start_date: date, end_date: date) -> schemas.ProfitSummary:
    """Service to calculate profit summary and handle business logic."""
    profit_data = await crud.get_profit_summary(db, store_id, start_date, end_date)
    
    total_revenue = profit_data["total_revenue"]
    total_cogs = profit_data["total_cogs"]
    gross_profit = total_revenue - total_cogs
    
    gross_profit_margin = 0.0
    if total_revenue > 0:
        gross_profit_margin = (gross_profit / total_revenue) * 100
        
    return schemas.ProfitSummary(
        total_revenue=total_revenue,
        total_cogs=total_cogs,
        gross_profit=gross_profit,
        gross_profit_margin=gross_profit_margin,
        start_date=start_date,
        end_date=end_date,
        is_estimated=profit_data["is_estimated"]
    )

async def get_top_performing_products(db: AsyncSession, store_id: uuid.UUID, limit: int, sort_by: str) -> List[schemas.ProductPerformance]:
    """Service to get a list of top-performing products."""
    products_data = await crud.get_top_performing_products(db, store_id, limit, sort_by)
    return [schemas.ProductPerformance(**data) for data in products_data]

async def get_low_stock_products(db: AsyncSession, store_id: uuid.UUID, page: int, size: int) -> List[schemas.LowStockProduct]:
    """Service to get a paginated list of low-stock products."""
    products_data = await crud.get_low_stock_products(db, store_id, page, size)
    return [schemas.LowStockProduct(**data) for data in products_data]
