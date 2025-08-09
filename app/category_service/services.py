# /app/category_service/services.py

import uuid
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from core.exceptions import ConflictException, NotFoundException, BadRequestException

logger = logging.getLogger(__name__)

async def create_category(db: AsyncSession, category_in: schemas.CategoryCreate,user_id:uuid.UUID) -> models.Category:
    """Business logic to create a new global category."""
    if category_in.parent_id:
        parent_category = await crud.get(db, category_id=category_in.parent_id)
        if not parent_category:
            raise BadRequestException(detail=f"Parent category with ID '{category_in.parent_id}' not found.")

    if await crud.get_by_prefix(db, prefix=category_in.prefix):
        raise ConflictException(detail=f"Category prefix '{category_in.prefix}' already exists globally.")

    category = await crud.create(db, category_in=category_in.model_dump(),user_id=user_id)
    logger.info(f"Global Category '{category.name}' created.")
    return category

async def get_category(db: AsyncSession, category_id: uuid.UUID) -> models.Category:
    """Business logic to retrieve a single category by its ID."""
    category = await crud.get(db, category_id=category_id)
    if not category:
        raise NotFoundException(resource="Category", resource_id=str(category_id))
    return category

async def get_all_categories(db: AsyncSession) -> List[models.Category]:
    """Business logic to retrieve all global categories."""
    return await crud.get_all(db=db)

async def update_category(db: AsyncSession, category_id: uuid.UUID, category_in: schemas.CategoryUpdate) -> models.Category:
    """Business logic to update a category."""
    db_category = await get_category(db, category_id=category_id)
    
    if category_in.prefix and category_in.prefix.upper() != db_category.prefix:
        if await crud.get_by_prefix(db, prefix=category_in.prefix):
            raise ConflictException(detail=f"Category prefix '{category_in.prefix}' already exists globally.")

    updated_category = await crud.update(db, db_category=db_category, category_in=category_in)
    logger.info(f"Global Category '{updated_category.name}' updated.")
    return updated_category

async def deactivate(db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """
    Business logic to deactivate (soft delete) a category.
    - Marks the category as inactive without permanently removing it.
    - Prevents deactivation if the category is associated with any products.
    """
    db_category = await get_category(db, category_id=category_id)
    
    if await crud.is_in_use(db, category_id=category_id):
        logger.warning(f"Attempt to deactivate category '{category_id}' which is currently in use.")
        raise ConflictException(detail="Cannot deactivate category as it is already linked to one or more products.")
        
    await crud.deactivate(db, db_category=db_category, user_id=user_id)
    logger.info(f"Category ID '{category_id}' has been deactivated.")
