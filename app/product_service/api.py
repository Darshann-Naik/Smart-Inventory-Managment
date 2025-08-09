# /app/product_service/api.py

import uuid
from typing import List
from fastapi import Depends, status, APIRouter

from core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.user_service.dependencies import get_current_active_user, require_role
from app.user_service.models import User
from . import schemas, services

router = APIRouter()

@router.post(
    "",
    response_model=schemas.Product,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    dependencies=[Depends(require_role(["shop_owner", "super_admin"]))],
)
async def create_product(
    product_in: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Adds a new product to the system for the authenticated user's store.
    """
    return await services.create_product(db=db, product_in=product_in, user_id=current_user.id)

@router.get(
    "/{product_id}",
    response_model=schemas.Product,
    summary="Get a specific product by ID",
)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves details of a specific product.
    - `super_admin` can view deactivated products.
    - Other roles can only view active products.
    """
    return await services.get_product(db=db, product_id=product_id, current_user=current_user)

@router.get(
    "",
    response_model=List[schemas.Product],
    summary="List all products for the store",
)
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves a list of all products for the store.
    - `super_admin` can view deactivated products.
    - Other roles can only view active products.
    """
    return await services.get_all_products(db=db, current_user=current_user, skip=skip, limit=limit)

@router.put(
    "/{product_id}",
    response_model=schemas.Product,
    summary="Update a product",
    dependencies=[Depends(require_role(["shop_owner", "super_admin"]))],
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
    return await services.update_product(db=db, product_id=product_id, product_in=product_in, user_id=current_user.id)

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product (Soft Delete)",
    dependencies=[Depends(require_role(["shop_owner", "super_admin"]))],
)
async def delete_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Soft-deletes a product from the system. The data is not permanently removed.
    """
    await services.delete_product(db=db, product_id=product_id, user_id=current_user.id)
    return