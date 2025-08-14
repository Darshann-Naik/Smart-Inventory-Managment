# /app/dashboard_service/schemas.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from typing import List, Optional

# --- Schemas for Core Metrics ---

class KPISummary(BaseModel):
    """High-level Key Performance Indicators for a store."""
    total_revenue: float
    total_sales_transactions: int
    average_transaction_value: float
    total_products_in_stock: int

class TimeSeriesDataPoint(BaseModel):
    """A single data point for a time-series chart."""
    timestamp: date
    value: float

# --- Schemas for Profit & Cost Analysis ---

class ProfitSummary(BaseModel):
    """Summary of profit metrics over a period."""
    total_revenue: float
    total_cogs: float # Cost of Goods Sold
    gross_profit: float
    gross_profit_margin: float # In percentage
    start_date: date
    end_date: date
    is_estimated: bool = Field(..., description="True if some transactions lacked cost data, making profit an estimate.")

# --- Schemas for Inventory Insights ---

class ProductPerformance(BaseModel):
    """Details of a top-performing product."""
    product_id: UUID
    product_name: str
    sku: str
    total_revenue: float
    units_sold: int

class LowStockProduct(BaseModel):
    """Details of a product that needs reordering."""
    product_id: UUID
    product_name: str
    sku: str
    current_stock: int
    reorder_point: int
