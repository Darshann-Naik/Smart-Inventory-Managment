# /app/transaction_service/services.py
import uuid
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . import crud, models, schemas
from core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.ml_service import services as ml_services

logger = logging.getLogger(__name__)

async def create_transaction(
    db: AsyncSession,
    transaction_in: schemas.TransactionCreate,
    user_id: uuid.UUID
) -> models.InventoryTransaction:
    """
    Service layer for recording an inventory transaction.
    - Handles business logic and validation.
    - Calls the CRUD layer to perform database operations.
    - Triggers the ML model to learn from the new transaction.
    """
    try:
        transaction, new_stock_level = await crud.create(
            db=db,
            transaction_in=transaction_in,
            user_id=user_id
        )
        
        # Asynchronously train the ML model without blocking the response
        await ml_services.train_model(transaction, new_stock_level)
        
        return transaction
    except ValueError as e:
        # Catch specific, user-facing errors from the CRUD layer
        raise BadRequestException(detail=str(e))
    except IntegrityError as e:
        # --- THE FIX IS HERE ---
        # Catch potential database integrity issues (like the check constraint violation)
        # and raise a ConflictException, which correctly uses the 'detail' argument.
        await db.rollback()
        logger.warning(f"Database integrity error during transaction creation: {e}")
        raise ConflictException(detail="The transaction could not be completed due to a data conflict or invalid reference.")
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error during transaction processing: {e}", exc_info=True)
        await db.rollback()
        raise

async def get_all_transactions(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    """Retrieves all transactions for a specific store."""
    return await crud.get_all_by_store(db, store_id, skip, limit)

async def get_all_transactions_for_product(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    """Retrieves all transactions for a specific product within a store."""
    return await crud.get_all_by_store_and_product(db, store_id, product_id, skip, limit)
