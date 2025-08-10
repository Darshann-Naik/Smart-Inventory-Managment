# /app/store_service/crud.py
import uuid
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.store_product_service.models import StoreProduct
from app.transaction_service.models import InventoryTransaction
from core.exceptions import ConflictException
from . import models, schemas

async def get(db: AsyncSession, store_id: uuid.UUID) -> Optional[models.Store]:
    """Gets an active store by its UUID."""
    statement = select(models.Store).where(models.Store.id == store_id, models.Store.is_active == True)
    return (await db.execute(statement)).scalar_one_or_none()

# NEW: Added a function to get a store by name for convenience.
async def get_by_name(db: AsyncSession, name: str) -> Optional[models.Store]:
    """Gets an active store by its unique name."""
    statement = select(models.Store).where(models.Store.name == name, models.Store.is_active == True)
    return (await db.execute(statement)).scalar_one_or_none()

async def get_all(db: AsyncSession, skip: int, limit: int) -> List[models.Store]:
    """Gets a list of all active stores with pagination."""
    statement = select(models.Store).where(models.Store.is_active == True).offset(skip).limit(limit)
    return (await db.execute(statement)).scalars().all()

async def create(db: AsyncSession, store_in: schemas.StoreCreate, user_id: uuid.UUID) -> models.Store:
    """Creates a new store in the database."""
    # First, check if a store with the same name already exists to provide a better error message.
    if await get_by_name(db, name=store_in.name):
        raise ConflictException(detail=f"A store with the name '{store_in.name}' already exists.")

    db_store = models.Store.model_validate(store_in, update={'created_by': user_id})
    db.add(db_store)
    try:
        await db.commit()
        await db.refresh(db_store)
        return db_store
    except IntegrityError:
        await db.rollback()
        # This is a fallback for race conditions or other unique constraints like GSTIN.
        raise ConflictException(detail=f"A store with the provided details may already exist (e.g., duplicate GSTIN).")


async def update(db: AsyncSession, store: models.Store, store_in: schemas.StoreUpdate) -> models.Store:
    """Updates an existing store's data."""
    store_data = store_in.model_dump(exclude_unset=True)
    for key, value in store_data.items():
        setattr(store, key, value)
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store

async def deactivate(db: AsyncSession, db_store: models.Store, user_id: uuid.UUID) -> models.Store:
    """Soft-deletes a store by updating its status and metadata."""
    db_store.is_active = False
    db_store.deactivated_by = user_id
    db_store.deactivated_at = datetime.now(timezone.utc)
    db.add(db_store)
    await db.commit()
    await db.refresh(db_store)
    return db_store

async def is_in_use(db: AsyncSession, store_id: uuid.UUID) -> bool:
    """Checks if a store is linked to any critical entities."""
    # Check for linked users

    # Check for linked products
    product_count_stmt = select(func.count(StoreProduct.id)).where(StoreProduct.store_id == store_id)
    if (await db.execute(product_count_stmt)).scalar_one() > 0:
        return True

    # Check for linked transactions
    transaction_count_stmt = select(func.count(InventoryTransaction.id)).where(InventoryTransaction.store_id == store_id)
    if (await db.execute(transaction_count_stmt)).scalar_one() > 0:
        return True
        
    return False