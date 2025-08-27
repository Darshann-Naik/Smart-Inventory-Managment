# /app/store_product_service/api.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.user_service.models import User
from core.database import get_db_session
from . import schemas, services
from app.user_service.dependencies import get_current_active_user, require_role

router = APIRouter()

@router.post(
    "/link",
    response_model=schemas.StoreProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Link a product to a store",
    dependencies=[Depends(require_role(["admin", "super_admin"]))]
)
async def link_product_to_store(
    mapping_in: schemas.StoreProductCreate, 
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Creates a new link between a product and a store, defining its price,
    stock level, and other store-specific attributes.
    """
    return await services.link(db, mapping_in, current_user=current_user, request=request)

@router.get(
    "/store/{store_id}", 
    response_model=List[schemas.StoreProductOut],
    summary="List all products in a specific store"
)
async def list_products_in_store(
    store_id: uuid.UUID, 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db_session)
):
    """
    Retrieves a paginated list of all products available in a specific store.
    """
    return await services.get_products_in_store(db, store_id, skip, limit)

@router.put(
    "/link/{store_id}/{product_id}", 
    response_model=schemas.StoreProductOut,
    summary="Update a product's details within a store",
    dependencies=[Depends(require_role(["admin", "super_admin"]))]
)
async def update_linked_product_details(
    store_id: uuid.UUID, 
    product_id: uuid.UUID, 
    update_data: schemas.StoreProductUpdate, 
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Updates a linked product's price, stock, or other store-specific details.
    """
    return await services.update_linked_product_details(db, store_id, product_id, update_data, current_user=current_user, request=request)

@router.delete(
    "/link/{store_id}/{product_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink a product from a store",
    dependencies=[Depends(require_role(["super_admin"]))]
)
async def unlink_product_from_store(
    store_id: uuid.UUID, 
    product_id: uuid.UUID, 
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deactivates the link between a product and a store.

    This operation will fail if the product has stock or is part of any
    existing transactions.
    """
    await services.unlink(db, store_id, product_id, current_user=current_user, request=request)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)