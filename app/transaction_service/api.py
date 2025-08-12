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
    This endpoint is transactional and will update stock levels atomically.
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
    current_user: User = Depends(get_current_active_user) # For authorization
):
    """
    Retrieves a list of all inventory transactions for a specific store.
    (In a real app, you would add role checks here to ensure the user can view these transactions).
    """
    # Optional: Add service-layer logic to check if current_user has access to store_id
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
    current_user: User = Depends(get_current_active_user) # For authorization
):
    """
    Retrieves a list of all inventory transactions for a specific product within a specific store.
    """
    return await services.get_all_transactions_for_product(db, store_id, product_id, skip, limit)
