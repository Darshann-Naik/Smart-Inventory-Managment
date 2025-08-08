# /app/transaction_service/crud.py

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

# --- RENAMED ---
from .models import InventoryTransaction
from .schemas import InventoryTransactionCreate
from app.inventory_service.models import InventoryItem

async def create_transaction(db: AsyncSession, *, transaction_in: InventoryTransactionCreate, store_id: uuid.UUID, user_id: uuid.UUID) -> InventoryTransaction:
    """
    Creates a transaction and updates the corresponding inventory item quantity
    in a single database transaction.
    """
    async with db.begin():
        inventory_item = (await db.execute(
            select(InventoryItem)
            .where(InventoryItem.product_id == transaction_in.product_id, InventoryItem.store_id == store_id)
            .with_for_update()
        )).scalar_one_or_none()

        if not inventory_item:
            raise ValueError("Inventory item not found for this product.")

        if transaction_in.quantity_change < 0 and inventory_item.quantity < abs(transaction_in.quantity_change):
            raise ValueError("Insufficient stock for this transaction.")
        
        inventory_item.quantity += transaction_in.quantity_change
        db.add(inventory_item)

        db_transaction = InventoryTransaction.model_validate(
            transaction_in, 
            update={"store_id": store_id, "recorded_by_user_id": user_id}
        )
        db.add(db_transaction)
    
    await db.refresh(db_transaction)
    return db_transaction

async def get_transactions(db: AsyncSession, *, store_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[InventoryTransaction]:
    """Retrieve all transactions for a store."""
    statement = select(InventoryTransaction).where(InventoryTransaction.store_id == store_id).offset(skip).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()