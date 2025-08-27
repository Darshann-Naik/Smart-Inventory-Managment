# /app/category_service/services.py
import uuid
import logging
import json
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from . import crud, models, schemas
from core.exceptions import ConflictException, NotFoundException, BadRequestException
from app.audit_log_service.services import AuditLogger
from app.user_service.models import User

logger = logging.getLogger(__name__)

async def create_category(db: AsyncSession, category_in: schemas.CategoryCreate, current_user: User, request: Request) -> schemas.Category:
    """Business logic to create a new global category and log the action."""
    if category_in.parent_id:
        parent_category = await crud.get(db, category_id=category_in.parent_id)
        if not parent_category:
            raise BadRequestException(detail=f"Parent category with ID '{category_in.parent_id}' not found.")

    if await crud.get_by_prefix(db, prefix=category_in.prefix):
        raise ConflictException(detail=f"Category prefix '{category_in.prefix}' already exists globally.")

    category_model = await crud.create(db, category_in=category_in.model_dump(), user_id=current_user.id)
    logger.info(f"Global Category '{category_model.name}' created.")
    
    category_schema = schemas.Category.model_validate(category_model)

    # --- Audit Log for Category Creation ---
    audit_logger = AuditLogger(db, current_user=current_user, request=request)
    await audit_logger.record_event(
        action="CREATE_CATEGORY",
        entity_type="Category",
        entity_id=str(category_schema.id),
        after=json.loads(category_schema.model_dump_json())
    )

    return category_schema

async def get_category(db: AsyncSession, category_id: uuid.UUID) -> schemas.Category:
    """Business logic to retrieve a single category by its ID."""
    category = await crud.get(db, category_id=category_id)
    if not category:
        raise NotFoundException(resource="Category", resource_id=str(category_id))
    return schemas.Category.model_validate(category)

async def get_all_categories(db: AsyncSession) -> List[schemas.Category]:
    """Business logic to retrieve all global categories."""
    categories = await crud.get_all(db=db)
    return [schemas.Category.model_validate(cat) for cat in categories]

async def update_category(db: AsyncSession, category_id: uuid.UUID, category_in: schemas.CategoryUpdate, current_user: User, request: Request) -> schemas.Category:
    """Business logic to update a category and log the action."""
    db_category = await crud.get(db, category_id=category_id)
    if not db_category:
        raise NotFoundException(resource="Category", resource_id=str(category_id))
        
    before_schema = schemas.Category.model_validate(db_category)
    before_state = json.loads(before_schema.model_dump_json())
    
    if category_in.prefix and category_in.prefix.upper() != db_category.prefix:
        if await crud.get_by_prefix(db, prefix=category_in.prefix):
            raise ConflictException(detail=f"Category prefix '{category_in.prefix}' already exists globally.")

    updated_category_model = await crud.update(db, db_category=db_category, category_in=category_in)
    logger.info(f"Global Category '{updated_category_model.name}' updated.")
    
    after_schema = schemas.Category.model_validate(updated_category_model)
    after_state = json.loads(after_schema.model_dump_json())

    # --- Audit Log for Category Update ---
    audit_logger = AuditLogger(db, current_user=current_user, request=request)
    await audit_logger.record_event(
        action="UPDATE_CATEGORY",
        entity_type="Category",
        entity_id=str(category_id),
        before=before_state,
        after=after_state
    )
    
    return after_schema

async def deactivate(db: AsyncSession, category_id: uuid.UUID, current_user: User, request: Request) -> None:
    """
    Business logic to deactivate a category and log the action.
    """
    db_category = await crud.get(db, category_id=category_id)
    if not db_category:
        raise NotFoundException(resource="Category", resource_id=str(category_id))

    before_schema = schemas.Category.model_validate(db_category)
    before_state = json.loads(before_schema.model_dump_json())
        
    if await crud.is_in_use(db, category_id=category_id):
        logger.warning(f"Attempt to deactivate category '{category_id}' which is currently in use.")
        raise ConflictException(detail="Cannot deactivate category as it is already linked to one or more products.")
        
    deactivated_category = await crud.deactivate(db, db_category=db_category, user_id=current_user.id)
    after_schema = schemas.Category.model_validate(deactivated_category)
    after_state = json.loads(after_schema.model_dump_json())

    # --- Audit Log for Category Deactivation ---
    audit_logger = AuditLogger(db, current_user=current_user, request=request)
    await audit_logger.record_event(
        action="DEACTIVATE_CATEGORY",
        entity_type="Category",
        entity_id=str(category_id),
        before=before_state,
        after=after_state
    )
    
    logger.info(f"Category ID '{category_id}' has been deactivated.")