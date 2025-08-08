# /app/inventory_service/services.py

import uuid
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . import crud, models, schemas
from app.product_service.services import get_product_by_id_service
from core.exceptions import ConflictException, NotFoundException, BadRequestException

logger = logging.getLogger(__name__)

async def create_inventory_item_service(db: AsyncSession, item_in: schemas.InventoryItemCreate, store_id: uuid.UUID) -> models.InventoryItem:
    """
    Business logic to create an inventory item.
    - Validates that the product exists.
    - Prevents creating duplicate inventory items for the same product.
    """
    # Validate that the product exists and belongs to the store
    await get_product_by_id_service(db, product_id=item_in.product_id, store_id=store_id)
    
    try:
        item = await crud.create_inventory_item(db=db, item_in=item_in, store_id=store_id)
        logger.info(f"Inventory item created for product '{item_in.product_id}' in store '{store_id}'.")
        return item
    except IntegrityError as e:
        await db.rollback()
        logger.warning(f"Attempt to create duplicate inventory item for product '{item_in.product_id}' in store '{store_id}'.")
        raise ConflictException(detail="An inventory item for this product already exists.") from e

async def get_inventory_item_service(db: AsyncSession, item_id: uuid.UUID, store_id: uuid.UUID) -> models.InventoryItem:
    """
    Business logic to retrieve a single inventory item.
    """
    item = await crud.get_inventory_item(db=db, item_id=item_id, store_id=store_id)
    if not item:
        raise NotFoundException(resource="InventoryItem", resource_id=str(item_id))
    return item

async def get_all_items_service(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryItem]:
    """Business logic to retrieve all inventory items."""
    return await crud.get_all_inventory_items(db=db, store_id=store_id, skip=skip, limit=limit)

async def update_inventory_item_service(db: AsyncSession, item_id: uuid.UUID, item_in: schemas.InventoryItemUpdate, store_id: uuid.UUID) -> models.InventoryItem:
    """
    Business logic to update an inventory item.
    """
    db_item = await get_inventory_item_service(db, item_id=item_id, store_id=store_id)
    
    updated_item = await crud.update_inventory_item(db=db, db_item=db_item, item_in=item_in)
    logger.info(f"Inventory item '{item_id}' updated.")
    return updated_item