# /app/category_service/api.py

from typing import List
from fastapi import Depends, status, Response, Request # Import Request
import uuid

from core.router import StandardAPIRouter
from core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.user_service.dependencies import get_current_active_user, require_role
from app.user_service.models import User
from . import schemas, services

router = StandardAPIRouter(tags=["Product Categories (Admin)"])

@router.post(
    "",
    response_model=schemas.Category,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new universal product category",
    dependencies=[Depends(require_role(["admin","super_admin"]))],
)
async def create_category(
    category_in: schemas.CategoryCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Creates a new GLOBAL category for organizing products.
    - **prefix**: A unique 2-4 letter code for SKU generation (e.g., 'GROC').
    """
    return await services.create_category(db=db, category_in=category_in, current_user=current_user, request=request)

@router.get(
    "/{category_id}",
    response_model=schemas.Category,
    summary="Get a single category by ID",
)
async def get_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves the details of a single universal product category.
    """
    return await services.get_category(db, category_id=category_id)

@router.get(
    "",
    response_model=List[schemas.Category],
    summary="List all universal product categories",
)
async def list_categories(
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves a list of all universal product categories available in the system.
    """
    return await services.get_all_categories(db=db)

@router.put(
    "/{category_id}",
    response_model=schemas.Category,
    summary="Update a product category",
    dependencies=[Depends(require_role(["admin", "super_admin"]))],
)
async def update_category(
    category_id: uuid.UUID,
    category_in: schemas.CategoryUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Updates the details of a universal product category. This is an admin-only endpoint.
    """
    return await services.update_category(db, category_id=category_id, category_in=category_in, current_user=current_user, request=request)

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a product category",
    dependencies=[Depends(require_role(["super_admin"]))],
)
async def deactivate_category(
    category_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Deletes a universal product category. This is an admin-only endpoint.
    Deletion will fail if the category is currently linked to any products.
    """
    await services.deactivate(db, category_id=category_id, current_user=current_user, request=request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)