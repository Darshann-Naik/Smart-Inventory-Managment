# /app/store_service/services.py
import logging
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundException
from . import crud, models, schemas

logger = logging.getLogger(__name__)

async def create_store(db: AsyncSession, store_in: schemas.StoreCreate) -> models.Store:
    """Handles the business logic for creating a new store."""
    store = await crud.create(db=db, store_in=store_in)
    logger.info(f"New store created with ID: {store.id} and name: '{store.name}'")
    return store

async def get_store(db: AsyncSession, store_id: uuid.UUID) -> models.Store:
    """Handles retrieving a single store by its ID, raising an error if not found."""
    store = await crud.get(db=db, store_id=store_id)
    if not store:
        logger.warning(f"Store with ID '{store_id}' not found.")
        raise NotFoundException(resource="Store", resource_id=str(store_id))
    logger.debug(f"Retrieved store with ID: {store_id}")
    return store

async def get_all_stores(db: AsyncSession, skip: int, limit: int) -> List[models.Store]:
    """Handles retrieving a list of stores."""
    stores = await crud.get_all(db=db, skip=skip, limit=limit)
    logger.debug(f"Retrieved {len(stores)} stores with skip={skip} and limit={limit}.")
    return stores

async def update_store(db: AsyncSession, store_id: uuid.UUID, store_in: schemas.StoreUpdate) -> models.Store:
    """Handles updating an existing store, ensuring it exists first."""
    store_to_update = await get_store(db=db, store_id=store_id)
    updated_store = await crud.update(db=db, store=store_to_update, store_in=store_in)
    logger.info(f"Store with ID '{store_id}' was updated.")
    return updated_store

async def delete_store(db: AsyncSession, store_id: uuid.UUID) -> None:
    """Handles deleting a store, ensuring it exists first."""
    store_to_delete = await get_store(db=db, store_id=store_id)
    await crud.remove(db=db, store=store_to_delete)
    logger.info(f"Store with ID '{store_id}' was deleted.")