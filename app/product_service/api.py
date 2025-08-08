# /app/product_service/api.py

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
    "/",
    response_model=schemas.ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    dependencies=[Depends(require_role(["shop_owner", "admin"]))],
)
async def create_product(
    product_in: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Adds a new product to the system for the authenticated user's store.
    """
    return await services.create_product_service(db=db, product_in=product_in, store_id=current_user.store_id)

@router.get(
    "/{product_id}",
    response_model=schemas.ProductRead,
    summary="Get a specific product by ID",
)
async def read_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves details of a specific product belonging to the user's store.
    """
    return await services.get_product_by_id_service(db=db, product_id=product_id, store_id=current_user.store_id)

@router.get(
    "/",
    response_model=List[schemas.ProductRead],
    summary="Retrieve all products for the store",
)
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves a list of all products for the authenticated user's store, with pagination.
    """
    return await services.get_all_products_service(db=db, store_id=current_user.store_id, skip=skip, limit=limit)

@router.put(
    "/{product_id}",
    response_model=schemas.ProductRead,
    summary="Update a product",
    dependencies=[Depends(require_role(["shop_owner", "admin"]))],
)
async def update_product(
    product_id: uuid.UUID,
    product_in: schemas.ProductUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Updates the details of an existing product.
    """
    return await services.update_product_service(db=db, product_id=product_id, product_in=product_in, store_id=current_user.store_id)

@router.delete(
    "/{product_id}",
    response_model=schemas.ProductRead,
    summary="Delete a product (Soft Delete)",
    dependencies=[Depends(require_role(["shop_owner", "admin"]))],
)
async def delete_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Soft-deletes a product from the system. The data is not permanently removed.
    """
    return await services.delete_product_service(db=db, product_id=product_id, store_id=current_user.store_id)