# /app/dashboard_service/crud.py
import uuid
from datetime import date
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, and_

from app.transaction_service.models import InventoryTransaction, TransactionType
from app.store_product_service.models import StoreProduct
from app.product_service.models import Product

async def get_kpi_summary(db: AsyncSession, store_id: uuid.UUID) -> Dict[str, Any]:
    """
    Performs database aggregations to calculate Key Performance Indicators.
    """
    sales_query = select(
        func.sum(InventoryTransaction.total_amount),
        func.count(InventoryTransaction.id)
    ).where(
        InventoryTransaction.store_id == store_id,
        InventoryTransaction.transaction_type == TransactionType.SALE
    )
    sales_result = (await db.execute(sales_query)).one_or_none()
    total_revenue, total_sales_transactions = sales_result or (0.0, 0)

    stock_query = select(
        func.sum(StoreProduct.stock)
    ).where(
        StoreProduct.store_id == store_id,
        StoreProduct.is_active == True
    )
    total_products_in_stock = (await db.execute(stock_query)).scalar_one_or_none() or 0

    return {
        "total_revenue": total_revenue or 0.0,
        "total_sales_transactions": total_sales_transactions or 0,
        "total_products_in_stock": total_products_in_stock
    }

async def get_sales_over_time(db: AsyncSession, store_id: uuid.UUID, start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """
    Aggregates sales data by day over a given date range.
    """
    query = select(
        func.date(InventoryTransaction.timestamp).label("date"),
        func.sum(InventoryTransaction.total_amount).label("total_revenue")
    ).where(
        InventoryTransaction.store_id == store_id,
        InventoryTransaction.transaction_type == TransactionType.SALE,
        func.date(InventoryTransaction.timestamp) >= start_date,
        func.date(InventoryTransaction.timestamp) <= end_date
    ).group_by(
        func.date(InventoryTransaction.timestamp)
    ).order_by(
        func.date(InventoryTransaction.timestamp)
    )
    
    result = await db.execute(query)
    return [{"timestamp": row.date, "value": row.total_revenue} for row in result.all()]

async def get_top_performing_products(db: AsyncSession, store_id: uuid.UUID, limit: int, sort_by: str) -> List[Dict[str, Any]]:
    """
    Retrieves top-performing products based on revenue or units sold.
    """
    group_by_cols = [
        Product.id,
        Product.name,
        Product.sku
    ]
    
    query = select(
        *group_by_cols,
        func.sum(InventoryTransaction.total_amount).label("total_revenue"),
        func.sum(InventoryTransaction.quantity).label("units_sold")
    ).join(
        Product, InventoryTransaction.product_id == Product.id
    ).where(
        InventoryTransaction.store_id == store_id,
        InventoryTransaction.transaction_type == TransactionType.SALE
    ).group_by(
        *group_by_cols
    )

    if sort_by == 'revenue':
        query = query.order_by(func.sum(InventoryTransaction.total_amount).desc())
    else: # sort by units_sold
        query = query.order_by(func.sum(InventoryTransaction.quantity).desc())
        
    query = query.limit(limit)
    
    result = await db.execute(query)
    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "sku": row.sku,
            "total_revenue": row.total_revenue,
            "units_sold": abs(row.units_sold) # Sales are negative, so take absolute value
        }
        for row in result.all()
    ]

async def get_low_stock_products(db: AsyncSession, store_id: uuid.UUID, page: int, size: int) -> List[Dict[str, Any]]:
    """
    Retrieves a paginated list of products at or below their reorder point.
    """
    offset = (page - 1) * size
    query = select(
        Product.id,
        Product.name,
        Product.sku,
        StoreProduct.stock,
        StoreProduct.reorder_point
    ).join(
        StoreProduct, Product.id == StoreProduct.product_id
    ).where(
        StoreProduct.store_id == store_id,
        StoreProduct.stock <= StoreProduct.reorder_point,
        StoreProduct.is_active == True
    ).offset(
        offset
    ).limit(
        size
    )
    
    result = await db.execute(query)
    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "sku": row.sku,
            "current_stock": row.stock,
            "reorder_point": row.reorder_point
        }
        for row in result.all()
    ]
