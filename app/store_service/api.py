# /Smart-Invetory/app/store_service/api.py
import uuid
from typing import List
from fastapi import Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.router import StandardAPIRouter
from core.database import get_db_session
from . import schemas, services
from app.user_service.dependencies import require_role

# The router now uses the StandardAPIRouter which handles response wrapping
router = StandardAPIRouter()

@router.post(
    "/",
    response_model=schemas.StoreRead, # Return the StoreRead schema directly
    status_code=status.HTTP_201_CREATED,
    summary="Create a new store",
    dependencies=[Depends(require_role(["shop_owner", "super_admin"]))],
)
async def create_store(
    store_in: schemas.StoreCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Create a new store.
    The response is automatically wrapped in a SuccessResponse by the StandardAPIRouter.
    """
    return await services.create_new_store(db=db, store_in=store_in)

@router.get(
    "/",
    response_model=List[schemas.StoreRead], # Return a list of StoreRead directly
    summary="Retrieve all stores"
)
async def read_stores(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieve all stores.
    The response is automatically wrapped.
    """
    return await services.get_all_stores(db, skip=skip, limit=limit)

@router.get(
    "/{store_id}",
    response_model=schemas.StoreRead, # Return the StoreRead schema directly
    summary="Get a specific store by ID"
)
async def read_store(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get a specific store by ID.
    The response is automatically wrapped.
    """
    return await services.get_store_by_id(db, store_id)

@router.put(
    "/{store_id}",
    response_model=schemas.StoreRead, # Return the StoreRead schema directly
    summary="Update a store",
    dependencies=[Depends(require_role(["shop_owner", "super_admin"]))],
)
async def update_store(
    store_id: uuid.UUID,
    store_in: schemas.StoreUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Update a specific store by ID.
    The response is automatically wrapped.
    """
    return await services.update_existing_store(db=db, store_id=store_id, store_in=store_in)

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
    """
    Delete a specific store by ID.
    A 204 response has no body, so the StandardAPIRouter will not wrap it.
    """
    await services.delete_store_by_id(db=db, store_id=store_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
