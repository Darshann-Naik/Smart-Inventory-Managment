# /app/product_service/services.py

import uuid
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from app.category_service.crud import get_category_by_id
from core.exceptions import ConflictException, NotFoundException, BadRequestException
from core.utils import generate_acronym

logger = logging.getLogger(__name__)

async def _generate_sku(db: AsyncSession, product_name: str, category_id: uuid.UUID, store_id: uuid.UUID) -> str:
    """
    Generates a new SKU based on the category and product name.
    Pattern: [CATEGORY_PREFIX]-[PRODUCT_ACRONYM]-[SEQUENTIAL_ID]
    Example: GROC-AA-001
    """
    category = await get_category_by_id(db, category_id=category_id, store_id=store_id)
    if not category:
        raise BadRequestException(detail="Invalid category ID provided.")
    
    last_product = await crud.get_last_product_in_category(db, category_id=category_id, store_id=store_id)
    
    sequential_id = 1
    if last_product and last_product.sku.startswith(category.prefix):
        try:
            last_seq_str = last_product.sku.split('-')[-1]
            sequential_id = int(last_seq_str) + 1
        except (IndexError, ValueError):
            # Fallback if SKU format is unexpected
            logger.warning(f"Could not parse sequential ID from SKU '{last_product.sku}'. Starting sequence from 1.")
    
    product_acronym = generate_acronym(product_name, 3)
    
    return f"{category.prefix}-{product_acronym}-{sequential_id:03d}"


async def create_product_service(db: AsyncSession, product_in: schemas.ProductCreate, store_id: uuid.UUID) -> models.Product:
    """
    Business logic to create a new product.
    - Validates category.
    - Generates SKU if not provided, otherwise validates custom SKU.
    """
    product_data = product_in.model_dump()
    product_data["store_id"] = store_id
    
    # Handle SKU
    if product_in.sku:
        # User provided a custom SKU, validate its uniqueness
        existing_product = await crud.get_product_by_sku(db, sku=product_in.sku, store_id=store_id)
        if existing_product:
            raise ConflictException(detail=f"Product with custom SKU '{product_in.sku}' already exists.")
        product_data["sku"] = product_in.sku
    else:
        # Auto-generate SKU
        product_data["sku"] = await _generate_sku(db, product_name=product_in.name, category_id=product_in.category_id, store_id=store_id)
        
    product = await crud.create_product(db, product_data=product_data)
    logger.info(f"Product '{product.id}' with SKU '{product.sku}' created for store '{store_id}'.")
    return product

# ... (other service functions remain the same) ...

async def get_product_by_id_service(db: AsyncSession, product_id: uuid.UUID, store_id: uuid.UUID) -> models.Product:
    """
    Business logic to retrieve a single product.
    - Raises NotFoundException if the product doesn't exist.
    """
    product = await crud.get_product_by_id(db=db, product_id=product_id, store_id=store_id)
    if not product:
        raise NotFoundException(resource="Product", resource_id=str(product_id))
    return product

async def get_all_products_service(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.Product]:
    """Business logic to retrieve all products for a store."""
    products = await crud.get_products(db=db, store_id=store_id, skip=skip, limit=limit)
    return products

async def update_product_service(db: AsyncSession, product_id: uuid.UUID, product_in: schemas.ProductUpdate, store_id: uuid.UUID) -> models.Product:
    """
    Business logic to update a product.
    - Ensures the product exists before updating.
    """
    db_product = await get_product_by_id_service(db, product_id=product_id, store_id=store_id)
    
    updated_product = await crud.update_product(db=db, db_product=db_product, product_in=product_in)
    logger.info(f"Product '{product_id}' updated for store '{store_id}'.")
    return updated_product

async def delete_product_service(db: AsyncSession, product_id: uuid.UUID, store_id: uuid.UUID) -> models.Product:
    """
    Business logic to soft-delete a product.
    - Checks if the product is associated with active inventory.
    """
    db_product = await get_product_by_id_service(db, product_id=product_id, store_id=store_id)
    
    deleted_product = await crud.soft_delete_product(db=db, db_product=db_product)
    logger.info(f"Product '{product_id}' soft-deleted for store '{store_id}'.")
    return deleted_product