# /app/store_product_service/services.py
import uuid
import json
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import Request

from . import crud, schemas, models
from app.product_service.crud import get_by_id as get_product_by_id
from app.store_service.crud import get as get_store
from core.exceptions import ConflictException, NotFoundException, BadRequestException
from app.audit_log_service.services import AuditLogger
from app.user_service.models import User

async def link(db: AsyncSession, mapping_in: schemas.StoreProductCreate, current_user: User, request: Request) -> schemas.StoreProductOut:
    """
    Links a product to a store and creates an audit log for the action.
    """
    if not await get_product_by_id(db, product_id=mapping_in.product_id):
        raise NotFoundException(resource="Product", resource_id=str(mapping_in.product_id))
    
    if not await get_store(db, store_id=mapping_in.store_id):
        raise NotFoundException(resource="Store", resource_id=str(mapping_in.store_id))

    if await crud.get_by_composite_key(db, store_id=mapping_in.store_id, product_id=mapping_in.product_id):
        raise ConflictException(detail="This product is already linked to this store.")

    try:
        created_mapping_model = await crud.create(db, mapping_in, current_user.id)
        
        # Convert to Pydantic schema for the response and audit log
        created_schema = schemas.StoreProductOut.model_validate(created_mapping_model)

        # --- Audit Log for Link Creation ---
        audit_logger = AuditLogger(db, current_user=current_user, request=request)
        await audit_logger.record_event(
            action="LINK_PRODUCT_TO_STORE",
            entity_type="StoreProduct",
            entity_id=str(created_schema.id),
            after=json.loads(created_schema.model_dump_json())
        )
        
        return created_schema
    except IntegrityError:
        await db.rollback()
        raise BadRequestException(detail="Invalid store or product ID provided, or link already exists.")


async def get_products_in_store(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[schemas.StoreProductOut]:
    """Retrieves all products linked to a specific store."""
    store_products = await crud.get_all_by_store(db, store_id, skip, limit)
    return [schemas.StoreProductOut.model_validate(sp) for sp in store_products]


async def update_linked_product_details(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID, update_data: schemas.StoreProductUpdate, current_user: User, request: Request) -> schemas.StoreProductOut:
    """Updates the details of a product within a store and logs the changes."""
    db_mapping = await crud.get_by_composite_key(db, store_id, product_id)
    if not db_mapping:
        raise NotFoundException(resource="Store-Product Link", resource_id=f"store:{store_id}, product:{product_id}")
    
    before_schema = schemas.StoreProductOut.model_validate(db_mapping)
    before_state = json.loads(before_schema.model_dump_json())

    updated_mapping_model = await crud.update(db, db_mapping, update_data)
    
    after_schema = schemas.StoreProductOut.model_validate(updated_mapping_model)
    after_state = json.loads(after_schema.model_dump_json())

    # --- Audit Log for Link Update ---
    audit_logger = AuditLogger(db, current_user=current_user, request=request)
    await audit_logger.record_event(
        action="UPDATE_STORE_PRODUCT_LINK",
        entity_type="StoreProduct",
        entity_id=str(db_mapping.id),
        before=before_state,
        after=after_state
    )

    return after_schema


async def unlink(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID, current_user: User, request: Request) -> None:
    """Deactivates the link between a product and a store and logs the action."""
    db_mapping = await crud.get_by_composite_key(db, store_id, product_id)
    if not db_mapping:
        raise NotFoundException(
            resource="Store-Product Link", 
            resource_id=f"store:{store_id}, product:{product_id}"
        )

    before_schema = schemas.StoreProductOut.model_validate(db_mapping)
    before_state = json.loads(before_schema.model_dump_json())

    if db_mapping.stock > 0:
        raise ConflictException(
            detail="Cannot unlink a product that has stock. Please adjust stock to 0 first."
        )

    if await crud.is_in_use(db, store_id, product_id):
        raise ConflictException(
            detail="Cannot unlink a product that is in use in transactions."
        )

    await crud.deactivate(db, db_mapping, current_user.id)
    # Re-fetch to get the deactivated state for the audit log
    deactivated_mapping = await crud.get_by_id(db, db_mapping.id) 
    after_schema = schemas.StoreProductOut.model_validate(deactivated_mapping)
    after_state = json.loads(after_schema.model_dump_json())

    # --- Audit Log for Link Deactivation ---
    audit_logger = AuditLogger(db, current_user=current_user, request=request)
    await audit_logger.record_event(
        action="DEACTIVATE_STORE_PRODUCT_LINK",
        entity_type="StoreProduct",
        entity_id=str(db_mapping.id),
        before=before_state,
        after=after_state
    )