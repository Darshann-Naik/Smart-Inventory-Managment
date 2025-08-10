# /app/store_product_service/services.py
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . import crud, schemas, models
# CORRECTED: Import the standardized 'get_by_id' and 'get' functions with aliases
from app.product_service.crud import get_by_id as get_product
from app.store_service.crud import get as get_store
from core.exceptions import ConflictException, NotFoundException, BadRequestException

async def link(db: AsyncSession, mapping_in: schemas.StoreProductCreate,user_id:uuid.UUID) -> models.StoreProduct:
    """Links a product to a store with specific pricing and stock details."""
    # CORRECTED: The aliased functions now work correctly
    if not await get_product(db, product_id=mapping_in.product_id):
        raise NotFoundException(resource="Product", resource_id=str(mapping_in.product_id))
    
    if not await get_store(db, store_id=mapping_in.store_id):
        raise NotFoundException(resource="Store", resource_id=str(mapping_in.store_id))

    if await crud.get(db, store_id=mapping_in.store_id, product_id=mapping_in.product_id):
        raise ConflictException(detail="This product is already linked to this store.")

    try:
        return await crud.create(db, mapping_in,user_id)
    except IntegrityError:
        await db.rollback()
        raise BadRequestException(detail="Invalid store or product ID provided.")

async def get_products_in_store(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.StoreProduct]:
    """Retrieves all products linked to a specific store."""
    return await crud.get_all_by_store(db, store_id, skip, limit)

async def update_linked_product_details(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID, update_data: schemas.StoreProductUpdate) -> models.StoreProduct:
    """Updates the details of a product within a specific store."""
    db_mapping = await crud.get(db, store_id, product_id)
    if not db_mapping:
        raise NotFoundException(resource="Store-Product Link", resource_id=f"store:{store_id}, product:{product_id}")
    return await crud.update(db, db_mapping, update_data)

async def unlink(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID, user_id: uuid.UUID):
    """Deactivate the link between a product and a store."""
    db_mapping = await crud.get(db, store_id, product_id)
    if not db_mapping:
        raise NotFoundException(
            resource="Store-Product Link", 
            resource_id=f"store:{store_id}, product:{product_id}"
        )

    if db_mapping.stock > 0:
        raise ConflictException(
            detail="Cannot unlink a product that has stock. Please adjust stock to 0 first."
        )

    if await crud.is_in_use(db, store_id, product_id):
        raise ConflictException(
            detail="Cannot unlink a product that is in use in transactions."
        )

    await crud.deactivate(db, db_mapping, user_id)

