# /app/transaction_service/services.py
import uuid
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from . import crud, models, schemas
from core.exceptions import BadRequestException, NotFoundException
from app.ml_service import services as ml_services
logger = logging.getLogger(__name__)

async def create_transaction(
    db: AsyncSession,
    transaction_in: schemas.TransactionCreate,
    user_id: uuid.UUID
) -> models.InventoryTransaction:
    """
    Service layer for recording an inventory transaction.
    Relies on the session-level transaction from the dependency.
    """
    try:
        # The crud function now returns the transaction AND the new stock level
        transaction, new_stock_level = await crud.create(
            db=db,
            transaction_in=transaction_in,
            user_id=user_id
        )

        # --- THIS IS THE INTEGRATION POINT ---
        # Asynchronously tell the ML service to learn from what just happened.
        # This won't block the user's request.
        await ml_services.train_model(transaction, new_stock_level)
        # The dependency will handle the commit when the request successfully finishes.
        return transaction
    except ValueError as e:
        # Raising an exception will cause the dependency to roll back the transaction.
        raise BadRequestException(detail=str(e))
    except IntegrityError:
        raise NotFoundException(detail="The specified user, store, or product does not exist.")
    except Exception as e:
        logger.error(f"Unexpected error during transaction processing: {e}", exc_info=True)
        raise

async def get_all_transactions(db: AsyncSession, store_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    """Retrieves all transactions for a specific store."""
    return await crud.get_all_by_store(db, store_id, skip, limit)

async def get_all_transactions_for_product(db: AsyncSession, store_id: uuid.UUID, product_id: uuid.UUID, skip: int, limit: int) -> List[models.InventoryTransaction]:
    """Retrieves all transactions for a specific product within a store."""
    return await crud.get_all_by_store_and_product(db, store_id, product_id, skip, limit)
