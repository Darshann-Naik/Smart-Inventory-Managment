# /app/product_service/services.py

import uuid
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.product_service import crud, models, schemas
# CORRECTED: Import 'get' as 'get_category' to avoid name collision and use the standardized function name
from app.category_service.crud import get as get_category
from core.exceptions import ConflictException, NotFoundException, BadRequestException
from core.utils import generate_acronym
from app.user_service.models import User

logger = logging.getLogger(__name__)

async def _generate_sku(db: AsyncSession, product_name: str, category_id: uuid.UUID) -> str:
    """
    Generates a new SKU based on the category and product name.
    Pattern: [CATEGORY_PREFIX]-[PRODUCT_ACRONYM]-[SEQUENTIAL_ID]
    Example: GROC-AA-001
    """
    # CORRECTED: Use the new aliased function 'get_category'
    category = await get_category(db, category_id=category_id)
    if not category:
        raise BadRequestException(detail="Invalid category ID provided.")
    
    sku_prefix = f"{category.prefix}-{generate_acronym(product_name, 3)}-"
    
    last_product = await crud.get_last_by_sku_prefix(db, sku_prefix=sku_prefix)
    
    sequential_id = 1
    if last_product:
        try:
            last_seq_str = last_product.sku.split('-')[-1]
            sequential_id = int(last_seq_str) + 1
        except (IndexError, ValueError):
            logger.warning(f"Could not parse sequential ID from SKU '{last_product.sku}'. Starting sequence from 1.")
    
    return f"{sku_prefix}{sequential_id:03d}"

# The rest of the service functions remain the same...

async def create_product(db: AsyncSession, product_in: schemas.ProductCreate, user_id: uuid.UUID) -> models.Product:
    """
    Business logic to create a new product.
    - Validates category.
    - Generates SKU.
    """
    product_data = product_in.model_dump()
    product_data["created_by"] = user_id
    
    if await crud.get_by_name_and_category(db, name=product_in.name, category_id=product_in.category_id):
        raise ConflictException(detail=f"Product '{product_in.name}' already exists in this category.")

    product_data["sku"] = await _generate_sku(db, product_name=product_in.name, category_id=product_in.category_id)
        
    try:
        product = await crud.create(db, product_data=product_data)
        logger.info(f"Product '{product.id}' with SKU '{product.sku}' created.")
        return product
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail=f"A product with the generated SKU '{product_data['sku']}' already exists. Please try again.")

async def get_product(db: AsyncSession, product_id: uuid.UUID, current_user: User) -> models.Product:
    """
    Business logic to retrieve a single product.
    """
    is_active = None if "super_admin" in current_user.roles else True
    product = await crud.get_by_id(db=db, product_id=product_id, is_active=is_active)
    if not product:
        raise NotFoundException(resource="Product", resource_id=str(product_id))
    return product

async def get_all_products(db: AsyncSession, current_user: User, skip: int, limit: int) -> List[models.Product]:
    """Business logic to retrieve all products for a store."""
    is_active = None if "super_admin" in current_user.roles else True
    products = await crud.get_all(db=db, skip=skip, limit=limit, is_active=is_active)
    return products

async def update_product(db: AsyncSession, product_id: uuid.UUID, product_in: schemas.ProductUpdate,user_id:uuid.UUID) -> models.Product:
    """
    Business logic to update a product.
    """
    # Note: In a real scenario, you'd pass the current_user here to check permissions
    db_product = await crud.get_by_id(db, product_id=product_id)
    if not db_product:
        raise NotFoundException(resource="Product", resource_id=str(product_id))
    
    try:
        updated_product = await crud.update(db=db, db_product=db_product, product_in=product_in,user_id=user_id)
        logger.info(f"Product '{product_id}' updated '.")
        return updated_product
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail="Update failed. A product with the same name and category may already exist.")

async def delete_product(db: AsyncSession, product_id: uuid.UUID,user_id:uuid.UUID) -> models.Product:
    """
    Business logic to soft-delete a product.
    """
    db_product = await crud.get_by_id(db, product_id=product_id)
    if not db_product:
        raise NotFoundException(resource="Product", resource_id=str(product_id))
    
    deleted_product = await crud.deactivate(db=db, db_product=db_product,user_id=user_id)
    logger.info(f"Product '{product_id}' soft-deleted '.")
    return deleted_product
