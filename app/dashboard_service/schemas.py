# /app/dashboard_service/schemas.py
from pydantic import BaseModel
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

# --- Schemas for Inventory Insights ---

class InventorySummary(BaseModel):
    """A snapshot of the current inventory state."""
    total_stock_quantity: int
    total_stock_value: float
    out_of_stock_products_count: int

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

# --- Schemas for AI/Futuristic Endpoints ---

class SalesForecast(BaseModel):
    """Represents a sales forecast for a product."""
    product_id: UUID
    product_name: str
    forecast: List[TimeSeriesDataPoint]

