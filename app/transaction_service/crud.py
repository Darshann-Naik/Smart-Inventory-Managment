# /app/transaction_service/crud.py
import uuid
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from . import models, schemas
from app.store_product_service.models import StoreProduct

async def create(db: AsyncSession, transaction_in: schemas.TransactionCreate, user_id: uuid.UUID) -> Tuple[models.InventoryTransaction, int]:
    result = await db.execute(
        select(StoreProduct).where(
            StoreProduct.store_id == transaction_in.store_id,
            StoreProduct.product_id == transaction_in.product_id,
            StoreProduct.is_active == True
        ).with_for_update() # Lock the row for transaction safety
    )
    store_product = result.scalar_one_or_none()
    if not store_product:
        raise ValueError("Product not found in this store's inventory.")

    transaction_data = transaction_in.model_dump()
    transaction_data["recorded_by_user_id"] = user_id

    # --- ENTERPRISE COSTING & REVENUE LOGIC ---
    if transaction_in.transaction_type == models.TransactionType.PURCHASE:
        purchase_qty = transaction_in.quantity
        purchase_cost = transaction_in.unit_cost
        
        store_product.stock += purchase_qty
        store_product.last_purchase_price=purchase_cost
        transaction_data["total_amount"] = purchase_qty * purchase_cost

    elif transaction_in.transaction_type == models.TransactionType.SALE:
        sale_qty = transaction_in.quantity
        if store_product.stock < sale_qty:
            raise ValueError(f"Insufficient stock. Available: {store_product.stock}, Required: {sale_qty}")
        
        store_product.stock -= sale_qty
        
        # Fetch the price from the StoreProduct link (Single Source of Truth)
        price_at_sale = store_product.selling_price
        transaction_data["unit_price_at_sale"] = price_at_sale
        transaction_data["cost_of_goods_sold"] = sale_qty * (store_product.selling_price or 0.0)
        transaction_data["total_amount"] = (sale_qty * price_at_sale) - (transaction_in.discount or 0.0)
        transaction_data["quantity"] = -sale_qty
    
    else: # ADJUSTMENT
        store_product.stock += transaction_in.quantity
        transaction_data["total_amount"] = 0

    db_transaction = models.InventoryTransaction(**transaction_data)
    db.add(store_product)
    db.add(db_transaction)
    await db.flush()
    await db.refresh(db_transaction)
    
    return db_transaction, store_product.stock


async def get_all_by_store(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    statement = (
        select(models.InventoryTransaction)
        .where(models.InventoryTransaction.store_id == store_id)
        .order_by(models.InventoryTransaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(statement)
    return result.scalars().all()

async def get_all_by_store_and_product(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    """Retrieves all transactions for a specific product within a specific store with pagination."""
    statement = (
        select(models.InventoryTransaction)
        .where(
            models.InventoryTransaction.store_id == store_id,
            models.InventoryTransaction.product_id == product_id
        )
        .order_by(models.InventoryTransaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(statement)
    return result.scalars().all()
