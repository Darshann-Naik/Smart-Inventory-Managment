# /Smart-Invetory/app/store_service/services.py
import logging
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundException
from . import crud, models, schemas

logger = logging.getLogger(__name__)

async def create_new_store(db: AsyncSession, *, store_in: schemas.StoreCreate) -> models.Store:
    """
    Handles the business logic for creating a new store.
    - In a more complex scenario, you could add business logic here,
      e.g., checking if the GSTIN is in a valid format before even hitting the DB.
    """
    store = await crud.create_store(db=db, store_in=store_in)
    logger.info(f"New store created with ID: {store.id} and name: '{store.name}'")
    return store

async def get_store_by_id(db: AsyncSession, store_id: uuid.UUID) -> models.Store:
    """
    Handles the business logic for retrieving a single store by its ID.
    Raises a NotFoundException if the store does not exist.
    """
    store = await crud.get_store_by_id(db=db, store_id=store_id)
    if not store:
        logger.warning(f"Store with ID '{store_id}' not found.")
        raise NotFoundException(resource="Store", resource_id=str(store_id))
    logger.debug(f"Retrieved store with ID: {store_id}")
    return store

async def get_all_stores(db: AsyncSession, skip: int, limit: int) -> List[models.Store]:
    """
    Handles the business logic for retrieving a list of stores.
    """
    stores = await crud.get_stores(db=db, skip=skip, limit=limit)
    logger.debug(f"Retrieved {len(stores)} stores with skip={skip} and limit={limit}.")
    return stores

async def update_existing_store(
    db: AsyncSession, *, store_id: uuid.UUID, store_in: schemas.StoreUpdate
) -> models.Store:
    """
    Handles the business logic for updating an existing store.
    - Ensures the store exists before attempting an update.
    """
    # First, ensure the store exists. This re-uses the logic from get_store_by_id.
    store_to_update = await get_store_by_id(db=db, store_id=store_id)
    
    # Now, call the CRUD function to perform the update
    updated_store = await crud.update_store(db=db, store=store_to_update, store_in=store_in)
    logger.info(f"Store with ID '{store_id}' was updated.")
    return updated_store

async def delete_store_by_id(db: AsyncSession, store_id: uuid.UUID) -> None:
    """
    Handles the business logic for deleting a store.
    - Ensures the store exists before attempting to delete it.
    """
    # First, ensure the store exists before attempting to delete it.
    store_to_delete = await get_store_by_id(db=db, store_id=store_id)
    
    # Call the CRUD function to perform the deletion
    await crud.delete_store(db=db, store=store_to_delete)
    logger.info(f"Store with ID '{store_id}' was deleted.")
