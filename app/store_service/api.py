# /app/store_service/api.py
import uuid
from typing import List
from fastapi import Depends, status, Response, APIRouter, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from . import schemas, services
from app.user_service.dependencies import get_current_active_user, require_role
from app.user_service.models import User

router = APIRouter()

@router.post(
    "",
    response_model=schemas.StoreOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new store",
    dependencies=[Depends(require_role(["admin", "super_admin"]))]
)
async def create_store(
    store_in: schemas.StoreCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new store. Requires 'admin' or 'super_admin' role."""
    return await services.create_store(db=db, store_in=store_in, current_user=current_user, request=request)

@router.get(
    "",
    response_model=List[schemas.StoreOut],
    summary="List all stores"
)
async def list_stores(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve all active stores with pagination."""
    return await services.get_all_stores(db, skip=skip, limit=limit)

@router.get(
    "/{store_id}",
    response_model=schemas.StoreOut,
    summary="Get a specific store"
)
async def get_store(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a specific store by its ID."""
    return await services.get_store(db, store_id)

@router.put(
    "/{store_id}",
    response_model=schemas.StoreOut,
    summary="Update a store",
    dependencies=[Depends(require_role(["admin", "super_admin"]))]
)
async def update_store(
    store_id: uuid.UUID,
    store_in: schemas.StoreUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user), # Get the user here
):
    """Update a specific store by its ID. Requires 'admin' or 'super_admin' role."""
    return await services.update_store(db=db, store_id=store_id, store_in=store_in, current_user=current_user, request=request)

@router.delete(
    "/{store_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a store",
    dependencies=[Depends(require_role(["super_admin"]))],
)
async def deactivate_store(
    store_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Deactivates a store. This is a soft delete. Requires 'super_admin' role.
    The store cannot be deactivated if it has associated users, products, or transactions.
    """
    await services.deactivate(db=db, store_id=store_id, current_user=current_user, request=request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)