# /app/store_service/api.py
import uuid
from typing import List
from fastapi import Depends, status, Response, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from . import schemas, services
from app.user_service.dependencies import require_role

router = APIRouter()

@router.post(
    "",
    response_model=schemas.Store,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new store",
    dependencies=[Depends(require_role(["super_admin"]))],
)
async def create_store(
    store_in: schemas.StoreCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new store. (Admin only)"""
    return await services.create_store(db=db, store_in=store_in)

@router.get(
    "",
    response_model=List[schemas.Store],
    summary="List all stores"
)
async def list_stores(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve all stores with pagination."""
    return await services.get_all_stores(db, skip=skip, limit=limit)

@router.get(
    "/{store_id}",
    response_model=schemas.Store,
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
    response_model=schemas.Store,
    summary="Update a store",
    dependencies=[Depends(require_role(["super_admin"]))],
)
async def update_store(
    store_id: uuid.UUID,
    store_in: schemas.StoreUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update a specific store by its ID. (Admin only)"""
    return await services.update_store(db=db, store_id=store_id, store_in=store_in)

@router.delete(
    "/{store_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a store",
    dependencies=[Depends(require_role(["super_admin"]))],
)
async def delete_store(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a specific store by its ID. (Admin only)"""
    await services.delete_store(db=db, store_id=store_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)