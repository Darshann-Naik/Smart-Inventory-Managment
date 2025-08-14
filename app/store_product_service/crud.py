# /app/store_product_service/crud.py

import uuid
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Local application imports
from . import models, schemas
from app.transaction_service.models import InventoryTransaction


# --- REFINED & RENAMED ---
async def get_by_id(db: AsyncSession, store_product_id: uuid.UUID) -> Optional[models.StoreProduct]:
    """
    Gets a single StoreProduct by its primary key (ID), eagerly loading the 
    related Product details. This is the canonical way to get a single,
    fully-detailed record.
    """
    statement = (
        select(models.StoreProduct)
        .options(selectinload(models.StoreProduct.product))
        .where(models.StoreProduct.id == store_product_id)
    )
    result = await db.execute(statement)
    return result.scalar_one_or_none()


# --- REFINED & RENAMED ---
async def get_by_composite_key(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID) -> Optional[models.StoreProduct]:
    """
    Gets a specific active Store-Product link by its composite business key 
    (store_id, product_id), eagerly loading the related Product.
    """
    statement = (
        select(models.StoreProduct)
        .where(
            models.StoreProduct.store_id == store_id,
            models.StoreProduct.product_id == product_id,
            models.StoreProduct.is_active == True
        )
        .options(selectinload(models.StoreProduct.product)) # Eagerly load for response model
    )
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def get_all_by_store(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.StoreProduct]:
    """
    Gets all active products linked to a store, with pagination, eagerly 
    loading related Product details for each.
    """
    statement = (
        select(models.StoreProduct)
        .where(
            models.StoreProduct.store_id == store_id,
            models.StoreProduct.is_active == True
        )
        .options(selectinload(models.StoreProduct.product)) # Eagerly load for response model
        .order_by(models.StoreProduct.created_at.desc()) # Added default sorting
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(statement)
    return result.scalars().all()


async def create(db: AsyncSession, mapping_in: schemas.StoreProductCreate, user_id: uuid.UUID) -> models.StoreProduct:
    """
    Creates a new link between a store and a product.

    Returns:
        The newly created StoreProduct ORM object with the 'product' relationship
        eagerly loaded, ready to be used in a response.
    """
    db_mapping = models.StoreProduct.model_validate(
        mapping_in,
        update={'created_by': user_id}
    )
    db.add(db_mapping)
    await db.flush() # Flush to assign the auto-generated ID to db_mapping.id
    
    # The definitive fix: Re-fetch the object using its new ID.
    # This is the most reliable way to get an object with all relationships
    # loaded as defined in the get_by_id function.
    created_mapping = await get_by_id(db, store_product_id=db_mapping.id)
    return created_mapping


async def update(db: AsyncSession, db_mapping: models.StoreProduct, update_data: schemas.StoreProductUpdate) -> models.StoreProduct:
    """
    Updates the details of a store-product link.

    Returns:
        The updated StoreProduct ORM object with the 'product' relationship
        eagerly loaded, ready to be used in a response.
    """
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_mapping, key, value)
        
    db.add(db_mapping)
    await db.flush()
    
    # Re-fetch using the ID to ensure relationships are loaded correctly
    # for the response, maintaining consistency with the 'create' and 'get' functions.
    updated_mapping = await get_by_id(db, store_product_id=db_mapping.id)
    return updated_mapping


async def deactivate(db: AsyncSession, db_mapping: models.StoreProduct, user_id: uuid.UUID) -> None:
    """
    Soft-deactivates the link between a store and a product.
    This operation does not return the object as it's a terminal state change.
    """
    db_mapping.deactivated_at = datetime.now(timezone.utc)
    db_mapping.is_active = False
    db_mapping.deactivated_by = user_id
    db.add(db_mapping)
    await db.flush() # The service layer will handle the commit.


async def is_in_use(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID) -> bool:
    """
    Checks if a store-product mapping has any linked inventory transactions,
    which would prevent its deletion or deactivation.
    """
    statement = (
        select(InventoryTransaction.id)
        .where(
            InventoryTransaction.store_id == store_id,
            InventoryTransaction.product_id == product_id
        )
        .limit(1)
    )
    result = await db.execute(statement)
    return result.scalar_one_or_none() is not None

