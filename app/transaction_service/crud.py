# /app/transaction_service/crud.py
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from . import models, schemas
from app.store_product_service.models import StoreProduct

async def create(db: AsyncSession, transaction_in: schemas.TransactionCreate, user_id: uuid.UUID) -> models.InventoryTransaction:
    """
    Atomically creates a transaction record and updates the stock level.
    This is the only way transactions should be created.
    """
    # Use a pessimistic lock on the inventory item to prevent race conditions
    store_product = await db.get(
        StoreProduct,
        (transaction_in.store_id, transaction_in.product_id),
        with_for_update=True
    )
    if not store_product:
        raise ValueError("Product not found in this store's inventory.")

    # Calculate quantity_change based on transaction type
    quantity_change = abs(transaction_in.quantity)
    if transaction_in.transaction_type == models.TransactionType.SALE:
        quantity_change = -quantity_change
        if store_product.stock < transaction_in.quantity:
            raise ValueError(f"Insufficient stock. Available: {store_product.stock}, Required: {transaction_in.quantity}")

    # Update the stock
    store_product.stock += quantity_change
    db.add(store_product)

    # Prepare transaction data
    total_amount = transaction_in.quantity * transaction_in.unit_cost
    db_transaction = models.InventoryTransaction(
        **transaction_in.model_dump(),
        recorded_by_user_id=user_id,
        quantity_change=quantity_change,
        total_amount=total_amount
    )

    db.add(db_transaction)
    await db.flush()  # Flush to ensure transaction is in the session before refresh
    await db.refresh(db_transaction)
    return db_transaction

async def get_all_by_store(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    """Retrieves all transactions for a specific store with pagination."""
    statement = (
        select(models.InventoryTransaction)
        .where(models.InventoryTransaction.store_id == store_id)
        .order_by(models.InventoryTransaction.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(statement)
    return result.scalars().all()