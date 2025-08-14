# /app/store_product_service/services.py

import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . import crud, schemas, models
# Assuming these CRUD functions are correctly defined in their respective services
from app.product_service.crud import get_by_id as get_product_by_id
from app.store_service.crud import get as get_store # Assuming 'get' here refers to get_by_id or similar
from core.exceptions import ConflictException, NotFoundException, BadRequestException

async def link(db: AsyncSession, mapping_in: schemas.StoreProductCreate, user_id: uuid.UUID) -> models.StoreProduct:
    """
    Links a product to a store with specific pricing and stock details.
    The returned object is ready for API response serialization.
    """
    # 1. Validate that the referenced Product and Store actually exist.
    if not await get_product_by_id(db, product_id=mapping_in.product_id):
        raise NotFoundException(resource="Product", resource_id=str(mapping_in.product_id))
    
    if not await get_store(db, store_id=mapping_in.store_id):
        raise NotFoundException(resource="Store", resource_id=str(mapping_in.store_id))

    # 2. Check if this link already exists using the correct CRUD function.
    if await crud.get_by_composite_key(db, store_id=mapping_in.store_id, product_id=mapping_in.product_id):
        raise ConflictException(detail="This product is already linked to this store.")

    # 3. Create the link. The CRUD function now handles returning the fully detailed object.
    try:
        # The crud.create function is now the single source of truth.
        # It returns the ORM object with the 'product' relationship loaded.
        # No more manual data construction is needed here.
        return await crud.create(db, mapping_in, user_id)
    except IntegrityError:
        await db.rollback()
        # This error can happen if, in a race condition, the link was created
        # after our check above. It's a good safeguard.
        raise BadRequestException(detail="Invalid store or product ID provided, or link already exists.")


async def get_products_in_store(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.StoreProduct]:
    """
    Retrieves all products linked to a specific store.
    The CRUD function returns objects ready for API response serialization.
    """
    # This function was already correct. No changes needed.
    return await crud.get_all_by_store(db, store_id, skip, limit)


async def update_linked_product_details(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID, update_data: schemas.StoreProductUpdate) -> models.StoreProduct:
    """
    Updates the details of a product within a specific store.
    The returned object is ready for API response serialization.
    """
    # Use the correct CRUD function to get the link to be updated.
    db_mapping = await crud.get_by_composite_key(db, store_id, product_id)
    if not db_mapping:
        raise NotFoundException(resource="Store-Product Link", resource_id=f"store:{store_id}, product:{product_id}")
    
    # The crud.update function handles the update and returns the detailed object.
    return await crud.update(db, db_mapping, update_data)


async def unlink(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID, user_id: uuid.UUID) -> None:
    """Deactivates the link between a product and a store."""
    # Use the correct CRUD function to get the link to be deactivated.
    db_mapping = await crud.get_by_composite_key(db, store_id, product_id)
    if not db_mapping:
        raise NotFoundException(
            resource="Store-Product Link", 
            resource_id=f"store:{store_id}, product:{product_id}"
        )

    # Business logic check: Prevent unlinking if there is stock.
    if db_mapping.stock > 0:
        raise ConflictException(
            detail="Cannot unlink a product that has stock. Please adjust stock to 0 first."
        )

    # Business logic check: Prevent unlinking if the product has transaction history.
    if await crud.is_in_use(db, store_id, product_id):
        raise ConflictException(
            detail="Cannot unlink a product that is in use in transactions."
        )

    await crud.deactivate(db, db_mapping, user_id)
    # This function returns None, indicating a successful operation with no content.
