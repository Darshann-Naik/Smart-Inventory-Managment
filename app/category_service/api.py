# /app/category_service/api.py

from typing import List
from fastapi import Depends, status, Response
import uuid

from core.router import StandardAPIRouter
from core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.user_service.dependencies import get_current_active_user, require_role
from app.user_service.models import User
from . import schemas, services

router = StandardAPIRouter(tags=["Product Categories (Admin)"])

@router.post(
    "/",
    response_model=schemas.CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new universal product category",
    dependencies=[Depends(require_role(["super_admin"]))],
)
async def create_category(
    category_in: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Creates a new GLOBAL category for organizing products.
    This is an admin-only endpoint.
    - **prefix**: A unique 2-4 letter code for SKU generation (e.g., 'GROC').
    """
    return await services.create_category_service(db=db, category_in=category_in)

@router.get(
    "/{category_id}",
    response_model=schemas.CategoryRead,
    summary="Get a single category by ID",
)
async def get_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves the details of a single universal product category.
    """
    return await services.get_category_by_id_service(db, category_id=category_id)

@router.get(
    "/",
    response_model=List[schemas.CategoryRead],
    summary="Get all universal product categories",
)
async def get_all_categories(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves a list of all universal product categories available in the system.
    """
    return await services.get_all_categories_service(db=db)

@router.put(
    "/{category_id}",
    response_model=schemas.CategoryRead,
    summary="Update a product category",
    dependencies=[Depends(require_role(["super_admin"]))],
)
async def update_category(
    category_id: uuid.UUID,
    category_in: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Updates the details of a universal product category. This is an admin-only endpoint.
    """
    return await services.update_category_service(db, category_id=category_id, category_in=category_in)

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product category",
    dependencies=[Depends(require_role(["super_admin"]))],
)
async def delete_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Deletes a universal product category. This is an admin-only endpoint.
    Deletion will fail if the category is currently linked to any products.
    """
    await services.delete_category_service(db, category_id=category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)