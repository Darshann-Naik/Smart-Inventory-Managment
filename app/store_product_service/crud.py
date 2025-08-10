# /app/store_product_service/crud.py
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.transaction_service.models import InventoryTransaction
from datetime import datetime, timezone

from . import models, schemas

async def get(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID) -> Optional[models.StoreProduct]:
    """Gets a specific active Store-Product link by its composite primary key."""
    statement = select(models.StoreProduct).where(
        models.StoreProduct.store_id == store_id,
        models.StoreProduct.product_id == product_id,
        models.StoreProduct.is_active == True
    )
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_all_by_store(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.StoreProduct]:
    """Gets all active products linked to a specific store with pagination."""
    statement = (
        select(models.StoreProduct)
        .where(
            models.StoreProduct.store_id == store_id,
            models.StoreProduct.is_active == True
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(statement)
    return result.scalars().all()

async def create(db: AsyncSession, mapping_in: schemas.StoreProductCreate,user_id:uuid.UUID) -> models.StoreProduct:
    """Creates a new link between a store and a product."""
    db_mapping = models.StoreProduct.model_validate(mapping_in)
    db_mapping.created_by=user_id
    db.add(db_mapping)
    await db.commit()
    await db.refresh(db_mapping)
    return db_mapping

async def update(db: AsyncSession, db_mapping: models.StoreProduct, update_data: schemas.StoreProductUpdate) -> models.StoreProduct:
    """Updates the details of a store-product link (e.g., price, stock)."""
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_mapping, key, value)
    db.add(db_mapping)
    await db.commit()
    await db.refresh(db_mapping)
    return db_mapping

async def deactivate(db: AsyncSession, db_mapping: models.StoreProduct, user_id: uuid.UUID) -> models.StoreProduct:
    """Soft-deactivates the link between a store and a product."""
    db_mapping.deactivated_at = datetime.now(timezone.utc)
    db_mapping.is_active = False
    db_mapping.deactivated_by = user_id

    db.add(db_mapping)
    await db.commit()
    await db.refresh(db_mapping)
    return db_mapping

async def is_in_use(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID) -> bool:
    """
    Checks if a store-product mapping is in use.
    A mapping is considered 'in use' if it has any linked inventory transactions.
    """

    result = await db.execute(
        select(InventoryTransaction)
        .where(
            InventoryTransaction.store_id == store_id,
            InventoryTransaction.product_id == product_id
        )
        .limit(1)  # optimization: no need to fetch all
    )
    return result.scalar_one_or_none() is not None