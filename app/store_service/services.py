# /app/store_service/services.py
import logging
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import ConflictException, NotFoundException
from . import crud, models, schemas

logger = logging.getLogger(__name__)

async def create_store(db: AsyncSession, store_in: schemas.StoreCreate, user_id: uuid.UUID) -> models.Store:
    """Handles the business logic for creating a new store."""
    store = await crud.create(db=db, store_in=store_in, user_id=user_id)
    logger.info(f"New store created with ID: {store.id} and name: '{store.name}' by user {user_id}")
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

async def deactivate(db: AsyncSession, store_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Handles deactivating a store, ensuring it exists and is not in use by any users."""
    store_to_deactivate = await get_store(db=db, store_id=store_id)

    # REFINED: Provide a more specific error if the store is in use.
    if await crud.is_in_use(db, store_id):
        logger.warning(f"Attempt to deactivate store '{store_id}' which has linked entities.")
        raise ConflictException(
            detail="Cannot delete store: It is linked to active users, products, or transactions."
        )

    await crud.deactivate(db=db, db_store=store_to_deactivate, user_id=user_id)
    logger.info(f"Store with ID '{store_id}' was deactivated successfully by user {user_id}.")