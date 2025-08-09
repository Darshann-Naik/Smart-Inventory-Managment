# /app/store_product_service/crud.py
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from . import models, schemas

async def get(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID) -> Optional[models.StoreProduct]:
    """Gets a specific Store-Product link by its composite primary key."""
    statement = select(models.StoreProduct).where(
        models.StoreProduct.store_id == store_id,
        models.StoreProduct.product_id == product_id
    )
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_all_by_store(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.StoreProduct]:
    """Gets all products linked to a specific store with pagination."""
    statement = select(models.StoreProduct).where(models.StoreProduct.store_id == store_id).offset(skip).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()

async def create(db: AsyncSession, mapping_in: schemas.StoreProductCreate) -> models.StoreProduct:
    """Creates a new link between a store and a product."""
    db_mapping = models.StoreProduct.model_validate(mapping_in)
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

async def remove(db: AsyncSession, db_mapping: models.StoreProduct) -> None:
    """Removes the link between a store and a product."""
    await db.delete(db_mapping)
    await db.commit()