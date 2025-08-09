# /app/store_product_service/api.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from . import schemas, services
# from app.user_service.dependencies import require_role # Import if needed

router = APIRouter()

@router.post(
    "/links",
    response_model=schemas.StoreProduct,
    status_code=status.HTTP_201_CREATED,
    summary="Link a product to a store"
    # dependencies=[Depends(require_role(["shop_owner", "admin"]))]
)
async def link_product_to_store(
    mapping_in: schemas.StoreProductCreate, 
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new link between a product and a store with specific pricing/stock."""
    return await services.link_product_to_store(db, mapping_in)

@router.get(
    "/stores/{store_id}/products", 
    response_model=List[schemas.StoreProduct],
    summary="List all products in a specific store"
)
async def list_products_in_store(
    store_id: uuid.UUID, 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db_session)
):
    """Get a list of all products available in a specific store."""
    return await services.get_products_in_store(db, store_id, skip, limit)

@router.put(
    "/links/{store_id}/{product_id}", 
    response_model=schemas.StoreProduct,
    summary="Update a product's details within a store"
    # dependencies=[Depends(require_role(["shop_owner", "admin"]))]
)
async def update_linked_product_details(
    store_id: uuid.UUID, 
    product_id: uuid.UUID, 
    update_data: schemas.StoreProductUpdate, 
    db: AsyncSession = Depends(get_db_session)
):
    """Update a linked product's price, stock, or other store-specific details."""
    return await services.update_linked_product_details(db, store_id, product_id, update_data)

@router.delete(
    "/links/{store_id}/{product_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink a product from a store"
    # dependencies=[Depends(require_role(["shop_owner", "admin"]))]
)
async def unlink_product_from_store(
    store_id: uuid.UUID, 
    product_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db_session)
):
    """Remove the link between a product and a store."""
    await services.unlink_product_from_store(db, store_id, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)