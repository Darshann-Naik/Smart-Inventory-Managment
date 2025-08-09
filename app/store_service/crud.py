# /app/store_service/crud.py
from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from core.exceptions import ConflictException
from . import models, schemas

async def get(db: AsyncSession, store_id: uuid.UUID) -> Optional[models.Store]:
    """Gets a store by its UUID."""
    return await db.get(models.Store, store_id)

async def get_all(db: AsyncSession, skip: int, limit: int) -> List[models.Store]:
    """Gets a list of all stores with pagination."""
    statement = select(models.Store).offset(skip).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()

async def create(db: AsyncSession, store_in: schemas.StoreCreate) -> models.Store:
    """Creates a new store in the database."""
    db_store = models.Store.model_validate(store_in)
    db.add(db_store)
    try:
        await db.commit()
        await db.refresh(db_store)
        return db_store
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail=f"A store with the name '{store_in.name}' or GSTIN '{store_in.gstin}' may already exist.")

async def update(db: AsyncSession, store: models.Store, store_in: schemas.StoreUpdate) -> models.Store:
    """Updates an existing store's data."""
    store_data = store_in.model_dump(exclude_unset=True)
    for key, value in store_data.items():
        setattr(store, key, value)
    db.add(store)
    try:
        await db.commit()
        await db.refresh(store)
        return store
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail=f"A store with the updated name or GSTIN may already exist.")

async def remove(db: AsyncSession, store: models.Store) -> None:
    """Deletes a store from the database."""
    await db.delete(store)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail=f"Cannot delete store '{store.name}' as it is still linked to other resources (e.g., users).")