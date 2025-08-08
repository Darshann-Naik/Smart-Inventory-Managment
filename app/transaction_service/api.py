# /app/transaction_service/api.py

from typing import List
from fastapi import Depends, status

from core.router import StandardAPIRouter
from core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.user_service.dependencies import get_current_active_user
from app.user_service.models import User
# --- RENAMED ---
from . import schemas, services

router = StandardAPIRouter()

@router.post(
    "/",
    # --- RENAMED ---
    response_model=schemas.InventoryTransactionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record an inventory transaction",
)
async def record_transaction(
    # --- RENAMED ---
    transaction_in: schemas.InventoryTransactionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Records an inventory transaction (e.g., sale, purchase, adjustment).
    This operation is atomic and will update the inventory stock levels accordingly.
    """
    return await services.record_transaction_service(
        db=db,
        transaction_in=transaction_in,
        store_id=current_user.store_id,
        user_id=current_user.id
    )

@router.get(
    "/",
    # --- RENAMED ---
    response_model=List[schemas.InventoryTransactionRead],
    summary="Get all transactions for the store",
)
async def read_transactions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves a list of all inventory transactions for the user's store.
    """
    return await services.get_all_transactions_service(db=db, store_id=current_user.store_id, skip=skip, limit=limit)