# /app/store_service/services.py
import logging
import uuid
import json # Import the json library
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.user_service.models import User
from core.exceptions import ConflictException, NotFoundException
from app.audit_log_service.services import AuditLogger
from . import crud, models, schemas

logger = logging.getLogger(__name__)

async def create_store(db: AsyncSession, store_in: schemas.StoreCreate, current_user: User, request: Request) -> schemas.StoreOut:
    """Handles the business logic for creating a new store and logs the action."""
    
    store_model = await crud.create(db=db, store_in=store_in, user_id=current_user.id)
    logger.info(f"New store created with ID: {store_model.id} and name: '{store_model.name}' by user {current_user.id}")
    
    store_schema = schemas.StoreOut.model_validate(store_model)

    audit_logger = AuditLogger(db, current_user=current_user, request=request)
    await audit_logger.record_event(
        action="CREATE_STORE",
        entity_type="Store",
        entity_id=str(store_schema.id),
        after=json.loads(store_schema.model_dump_json())
    )

    return store_schema

async def get_store(db: AsyncSession, store_id: uuid.UUID) -> schemas.StoreOut:
    """Handles retrieving a single store and returns it as a Pydantic schema."""
    store_model = await crud.get(db=db, store_id=store_id)
    if not store_model:
        logger.warning(f"Store with ID '{store_id}' not found.")
        raise NotFoundException(resource="Store", resource_id=str(store_id))
    logger.debug(f"Retrieved store with ID: {store_id}")
    
    return schemas.StoreOut.model_validate(store_model)

async def get_all_stores(db: AsyncSession, skip: int, limit: int) -> List[schemas.StoreOut]:
    """Handles retrieving a list of stores as Pydantic schemas."""
    stores_list = await crud.get_all(db=db, skip=skip, limit=limit)
    logger.debug(f"Retrieved {len(stores_list)} stores with skip={skip} and limit={limit}.")
    
    return [schemas.StoreOut.model_validate(store) for store in stores_list]

async def update_store(db: AsyncSession, store_id: uuid.UUID, store_in: schemas.StoreUpdate, current_user: User, request: Request) -> schemas.StoreOut:
    """Handles updating an existing store, logs the changes, and returns a Pydantic schema."""
    
    store_to_update = await crud.get(db=db, store_id=store_id)
    if not store_to_update:
        raise NotFoundException(resource="Store", resource_id=str(store_id))
        
    before_schema = schemas.StoreOut.model_validate(store_to_update)
    before_state = json.loads(before_schema.model_dump_json())

    updated_store_model = await crud.update(db=db, store=store_to_update, store_in=store_in)
    logger.info(f"Store with ID '{store_id}' was updated.")
    
    after_schema = schemas.StoreOut.model_validate(updated_store_model)
    after_state = json.loads(after_schema.model_dump_json())

    audit_logger = AuditLogger(db, current_user=current_user, request=request)
    await audit_logger.record_event(
        action="UPDATE_STORE",
        entity_type="Store",
        entity_id=str(store_id),
        before=before_state,
        after=after_state
    )

    return after_schema
async def deactivate(db: AsyncSession, store_id: uuid.UUID, current_user: User, request: Request) -> None:
    """Handles deactivating a store, logs the action, and ensures it's not in use."""
    store_to_deactivate = await crud.get(db=db, store_id=store_id)
    if not store_to_deactivate:
         raise NotFoundException(resource="Store", resource_id=str(store_id))
    
    before_schema = schemas.StoreOut.model_validate(store_to_deactivate)
    before_state = json.loads(before_schema.model_dump_json())

    if await crud.is_in_use(db, store_id):
        logger.warning(f"Attempt to deactivate store '{store_id}' which has linked entities.")
        raise ConflictException(
            detail="Cannot delete store: It is linked to active users, products, or transactions."
        )

    deactivated_store = await crud.deactivate(db=db, db_store=store_to_deactivate, user_id=current_user.id)
    after_schema = schemas.StoreOut.model_validate(deactivated_store)
    after_state = json.loads(after_schema.model_dump_json())
    
    audit_logger = AuditLogger(db, current_user=current_user, request=request)
    await audit_logger.record_event(
        action="DEACTIVATE_STORE",
        entity_type="Store",
        entity_id=str(store_id),
        before=before_state,
        after=after_state
    )

    logger.info(f"Store with ID '{store_id}' was deactivated successfully by user {current_user.id}.")