# /app/transaction_service/services.py
import uuid
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . import crud, models, schemas
from core.exceptions import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)

async def create_transaction(db: AsyncSession, transaction_in: schemas.TransactionCreate, user_id: uuid.UUID) -> models.InventoryTransaction:
    """
    Service layer for recording an inventory transaction.
    Wraps the atomic CRUD operation in a transaction block.
    """
    async with db.begin_nested(): # Use a nested transaction or savepoint
        try:
            return await crud.create(
                db=db,
                transaction_in=transaction_in,
                user_id=user_id
            )
        except ValueError as e:
            # Business logic errors from CRUD (e.g., insufficient stock)
            raise BadRequestException(detail=str(e))
        except IntegrityError:
            # This can happen if the foreign key for the user/product doesn't exist
            await db.rollback()
            raise NotFoundException(detail="The specified user, store, or product does not exist.")
        except Exception as e:
            logger.error(f"Unexpected error during transaction processing: {e}", exc_info=True)
            await db.rollback() # Ensure rollback on unexpected errors
            raise # Re-raise the original exception to be caught by the generic handler

async def get_all_transactions(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    """Retrieves all transactions for a specific store."""
    return await crud.get_all_by_store(db, store_id, skip, limit)
