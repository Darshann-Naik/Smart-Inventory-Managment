# /app/transaction_service/services.py

import uuid
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

# --- RENAMED ---
from . import crud, models, schemas
from app.inventory_service.crud import get_inventory_item_by_product_id
from core.exceptions import BadRequestException

logger = logging.getLogger(__name__)

async def record_transaction_service(db: AsyncSession, transaction_in: schemas.InventoryTransactionCreate, store_id: uuid.UUID, user_id: uuid.UUID) -> models.InventoryTransaction:
    """
    Business logic to record a transaction.
    """
    inventory_item = await get_inventory_item_by_product_id(db, product_id=transaction_in.product_id, store_id=store_id)
    if not inventory_item:
        raise BadRequestException(detail="No inventory record for this product. Please add the product to inventory first.")
    
    try:
        transaction = await crud.create_transaction(db=db, transaction_in=transaction_in, store_id=store_id, user_id=user_id)
        logger.info(f"Transaction '{transaction.id}' recorded for product '{transaction.product_id}' in store '{store_id}'.")
        return transaction
    except ValueError as e:
        await db.rollback()
        logger.warning(f"Transaction failed for product '{transaction_in.product_id}': {e}")
        raise BadRequestException(detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"An unexpected error occurred during transaction processing: {e}", exc_info=True)
        raise

async def get_all_transactions_service(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    """Business logic to retrieve all transactions."""
    return await crud.get_transactions(db=db, store_id=store_id, skip=skip, limit=limit)