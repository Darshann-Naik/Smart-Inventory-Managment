# /app/product_service/services.py

import uuid
import logging
import json
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import Request

from app.product_service import crud, models, schemas
from app.category_service.crud import get as get_category
from core.exceptions import ConflictException, NotFoundException, BadRequestException
from core.utils import generate_acronym
from app.user_service.models import User
from app.audit_log_service.services import AuditLogger

logger = logging.getLogger(__name__)

async def _generate_sku(db: AsyncSession, product_name: str, category_id: uuid.UUID) -> str:
    """
    Generates a new, more robust SKU.
    Pattern: [CATEGORY_PREFIX]-[ACRONYM+CHECKSUM]-[SEQUENTIAL_ID]
    Example: GROC-PGB37-001 for "Parle-G Biscuit"
    """
    category = await get_category(db, category_id=category_id)
    if not category:
        raise BadRequestException(detail="Invalid category ID provided.")
    
    # --- New, More Robust SKU Logic ---
    # 1. Generate an acronym from the first letter of up to 3 words.
    words = product_name.upper().split()
    acronym = "".join(word[0] for word in words[:3])
    
    # 2. Calculate a simple, deterministic checksum from the full product name.
    #    This ensures that "Parle-G Gold" and "Parle-G Glucose" will have different codes.
    checksum = sum(ord(c) for c in product_name) % 100
    
    # 3. Combine them into a unique product code.
    product_code = f"{acronym}{checksum:02d}" # The :02d ensures it's always two digits, e.g., '07'

    sku_prefix = f"{category.prefix}-{product_code}-"
    # --- End of New Logic ---
    
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

async def create_product(db: AsyncSession, product_in: schemas.ProductCreate, current_user: User, request: Request) -> schemas.Product:
    """
    Business logic to create a new product, including SKU generation and audit logging.
    """
    product_data = product_in.model_dump()
    product_data["created_by"] = current_user.id
    
    if await crud.get_by_name_and_category(db, name=product_in.name, category_id=product_in.category_id):
        raise ConflictException(detail=f"Product '{product_in.name}' already exists in this category.")

    product_data["sku"] = await _generate_sku(db, product_name=product_in.name, category_id=product_in.category_id)
        
    try:
        product_model = await crud.create(db, product_data=product_data)
        logger.info(f"Product '{product_model.id}' with SKU '{product_model.sku}' created.")
        
        product_schema = schemas.Product.model_validate(product_model)

        # --- Audit Log for Product Creation ---
        audit_logger = AuditLogger(db, current_user=current_user, request=request)
        await audit_logger.record_event(
            action="CREATE_PRODUCT",
            entity_type="Product",
            entity_id=str(product_schema.id),
            after=json.loads(product_schema.model_dump_json())
        )

        return product_schema
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail=f"A product with the generated SKU '{product_data['sku']}' already exists. Please try again.")

async def get_product(db: AsyncSession, product_id: uuid.UUID) -> schemas.Product:
    """Retrieves a single product and returns it as a Pydantic schema."""
    product = await crud.get_by_id(db=db, product_id=product_id)
    if not product:
        raise NotFoundException(resource="Product", resource_id=str(product_id))
    return schemas.Product.model_validate(product)

async def get_all_products(db: AsyncSession,  skip: int, limit: int) -> List[schemas.Product]:
    """Retrieves all products as Pydantic schemas."""
    products = await crud.get_all(db=db, skip=skip, limit=limit)
    return [schemas.Product.model_validate(p) for p in products]

async def update_product(db: AsyncSession, product_id: uuid.UUID, product_in: schemas.ProductUpdate, current_user: User, request: Request) -> schemas.Product:
    """Business logic to update a product and log the action."""
    db_product = await crud.get_by_id(db, product_id=product_id)
    if not db_product:
        raise NotFoundException(resource="Product", resource_id=str(product_id))
    
    before_schema = schemas.Product.model_validate(db_product)
    before_state = json.loads(before_schema.model_dump_json())
    
    try:
        updated_product_model = await crud.update(db=db, db_product=db_product, product_in=product_in, user_id=current_user.id)
        logger.info(f"Product '{product_id}' updated.")
        
        after_schema = schemas.Product.model_validate(updated_product_model)
        after_state = json.loads(after_schema.model_dump_json())

        # --- Audit Log for Product Update ---
        audit_logger = AuditLogger(db, current_user=current_user, request=request)
        await audit_logger.record_event(
            action="UPDATE_PRODUCT",
            entity_type="Product",
            entity_id=str(product_id),
            before=before_state,
            after=after_state
        )
        return after_schema
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail="Update failed. A product with the same name and category may already exist.")

async def delete_product(db: AsyncSession, product_id: uuid.UUID, current_user: User, request: Request) -> None:
    """Business logic to soft-delete a product and log the action."""
    db_product = await crud.get_by_id(db, product_id=product_id)
    if not db_product:
        raise NotFoundException(resource="Product", resource_id=str(product_id))

    before_schema = schemas.Product.model_validate(db_product)
    before_state = json.loads(before_schema.model_dump_json())
    
    deleted_product_model = await crud.deactivate(db=db, db_product=db_product, user_id=current_user.id)
    after_schema = schemas.Product.model_validate(deleted_product_model)
    after_state = json.loads(after_schema.model_dump_json())

    # --- Audit Log for Product Deactivation ---
    audit_logger = AuditLogger(db, current_user=current_user, request=request)
    await audit_logger.record_event(
        action="DEACTIVATE_PRODUCT",
        entity_type="Product",
        entity_id=str(product_id),
        before=before_state,
        after=after_state
    )

    logger.info(f"Product '{product_id}' soft-deleted.")