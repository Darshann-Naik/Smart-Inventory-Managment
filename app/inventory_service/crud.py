# /app/inventory_service/crud.py

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from .models import InventoryItem
from .schemas import InventoryItemCreate, InventoryItemUpdate

async def get_inventory_item(db: AsyncSession, *, item_id: uuid.UUID, store_id: uuid.UUID) -> Optional[InventoryItem]:
    """Retrieve a single inventory item by ID."""
    statement = select(InventoryItem).where(
        InventoryItem.id == item_id,
        InventoryItem.store_id == store_id
    ).options(selectinload(InventoryItem.product))
    result = await db.execute(statement)
    return result.scalar_one_or_none()
    
async def get_inventory_item_by_product_id(db: AsyncSession, *, product_id: uuid.UUID, store_id: uuid.UUID) -> Optional[InventoryItem]:
    """Retrieve an inventory item by product ID."""
    statement = select(InventoryItem).where(
        InventoryItem.product_id == product_id,
        InventoryItem.store_id == store_id
    ).options(selectinload(InventoryItem.product))
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_all_inventory_items(db: AsyncSession, *, store_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[InventoryItem]:
    """Retrieve all inventory items for a store."""
    statement = select(InventoryItem).where(
        InventoryItem.store_id == store_id
    ).options(selectinload(InventoryItem.product)).offset(skip).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()

async def create_inventory_item(db: AsyncSession, *, item_in: InventoryItemCreate, store_id: uuid.UUID) -> InventoryItem:
    """Create a new inventory item."""
    db_item = InventoryItem.model_validate(item_in, update={"store_id": store_id})
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item, attribute_names=["product"])
    return db_item
    
async def update_inventory_item(db: AsyncSession, *, db_item: InventoryItem, item_in: InventoryItemUpdate) -> InventoryItem:
    """Update an inventory item."""
    update_data = item_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item, attribute_names=["product"])
    return db_item