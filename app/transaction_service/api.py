# /app/transaction_service/api.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from app.user_service.dependencies import get_current_active_user
from app.user_service.models import User
from . import schemas, services

router = APIRouter()

@router.post(
    "",
    response_model=schemas.Transaction,
    status_code=status.HTTP_201_CREATED,
    summary="Record an inventory transaction"
)
async def record_transaction(
    transaction_in: schemas.TransactionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Records a new inventory transaction (SALE, PURCHASE, or ADJUSTMENT).
    This endpoint is transactional and will update stock levels and costs atomically.
    - For a SALE, `unit_cost` is ignored; the price is fetched from the system.
    - For a PURCHASE, `unit_cost` is required.
    """
    return await services.create_transaction(
        db=db,
        transaction_in=transaction_in,
        user_id=current_user.id
    )

@router.get(
    "/{store_id}",
    response_model=List[schemas.Transaction],
    summary="List all transactions for a store"
)
async def list_transactions_for_store(
    store_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves a list of all inventory transactions for a specific store.
    """
    return await services.get_all_transactions(db, store_id, skip, limit)

@router.get(
    "/{store_id}/{product_id}",
    response_model=List[schemas.Transaction],
    summary="List all transactions for a specific product in a store"
)
async def list_transactions_for_product_in_store(
    store_id: uuid.UUID,
    product_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves a list of all inventory transactions for a specific product
    within a specific store.
    """
    return await services.get_all_transactions_for_product(db, store_id, product_id, skip, limit)
