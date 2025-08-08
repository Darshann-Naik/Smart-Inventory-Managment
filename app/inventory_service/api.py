# /app/inventory_service/api.py

import uuid
from typing import List
from fastapi import Depends, status

from core.router import StandardAPIRouter
from core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.user_service.dependencies import get_current_active_user, require_role
from app.user_service.models import User
from . import schemas, services

router = StandardAPIRouter()

@router.post(
    "/items",
    response_model=schemas.InventoryItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new inventory item",
    dependencies=[Depends(require_role(["shop_owner", "admin", "employee"]))],
)
async def create_inventory_item(
    item_in: schemas.InventoryItemCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Adds stock for a specific product in the user's store.
    """
    return await services.create_inventory_item_service(db=db, item_in=item_in, store_id=current_user.store_id)

@router.get(
    "/items/{item_id}",
    response_model=schemas.InventoryItemRead,
    summary="Get a specific inventory item",
)
async def read_inventory_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves details of a specific inventory item from the user's store.
    """
    return await services.get_inventory_item_service(db=db, item_id=item_id, store_id=current_user.store_id)

@router.get(
    "/items",
    response_model=List[schemas.InventoryItemRead],
    summary="Get all inventory items for the store",
)
async def read_inventory_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves a list of all inventory items for the authenticated user's store.
    """
    return await services.get_all_items_service(db=db, store_id=current_user.store_id, skip=skip, limit=limit)

@router.put(
    "/items/{item_id}",
    response_model=schemas.InventoryItemRead,
    summary="Update an inventory item",
    dependencies=[Depends(require_role(["shop_owner", "admin", "employee"]))],
)
async def update_inventory_item(
    item_id: uuid.UUID,
    item_in: schemas.InventoryItemUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Updates an inventory item's quantity or reorder point.
    """
    return await services.update_inventory_item_service(db=db, item_id=item_id, item_in=item_in, store_id=current_user.store_id)