# /app/transaction_service/crud.py
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from . import models, schemas
from app.store_product_service.models import StoreProduct

async def create(db: AsyncSession, transaction_in: schemas.TransactionCreate, user_id: uuid.UUID) -> models.InventoryTransaction:
    result = await db.execute(
        select(StoreProduct).where(
            StoreProduct.store_id == transaction_in.store_id,
            StoreProduct.product_id == transaction_in.product_id,
            StoreProduct.is_active == True
        ).with_for_update()
    )
    store_product = result.scalar_one_or_none()
    if not store_product:
        raise ValueError("Product not found in this store's inventory.")

    quantity_change = abs(transaction_in.quantity)
    if transaction_in.transaction_type == models.TransactionType.SALE:
        quantity_change = -quantity_change
        if store_product.stock < abs(transaction_in.quantity):
            raise ValueError(
                f"Insufficient stock. Available: {store_product.stock}, Required: {abs(transaction_in.quantity)}"
            )

    store_product.stock += quantity_change

    total_amount = transaction_in.quantity * (transaction_in.unit_cost or 0.0)
    db_transaction = models.InventoryTransaction(
        **transaction_in.model_dump(),
        recorded_by_user_id=user_id,
        total_amount=total_amount
    )

    db.add(store_product)
    db.add(db_transaction)
    await db.flush()
    await db.refresh(db_transaction)
    
    # --- THIS IS THE KEY CHANGE ---
    # Return both the transaction and the new stock level.
    return db_transaction, store_product.stock


async def get_all_by_store(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    # ... (this function is correct and remains unchanged) ...
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