# /app/product_service/crud.py

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from .models import Product
from .schemas import ProductCreate, ProductUpdate

# ... (get_product_by_id and get_product_by_sku remain the same) ...

async def get_product_by_id(db: AsyncSession, *, product_id: uuid.UUID, store_id: uuid.UUID) -> Optional[Product]:
    """Retrieve a product by its ID and store ID."""
    statement = select(Product).where(Product.id == product_id, Product.store_id == store_id, Product.deleted_at == None)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_product_by_sku(db: AsyncSession, *, sku: str, store_id: uuid.UUID) -> Optional[Product]:
    """Retrieve a product by its SKU and store ID."""
    statement = select(Product).where(func.lower(Product.sku) == sku.lower(), Product.store_id == store_id, Product.deleted_at == None)
    result = await db.execute(statement)
    return result.scalar_one_or_none()
    
async def get_products(db: AsyncSession, *, store_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Product]:
    """Retrieve a list of products for a given store."""
    statement = select(Product).where(Product.store_id == store_id, Product.deleted_at == None).offset(skip).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()

async def get_last_product_in_category(db: AsyncSession, *, category_id: uuid.UUID, store_id: uuid.UUID) -> Optional[Product]:
    """Gets the most recently created product in a category to determine the next sequential ID."""
    statement = select(Product).where(
        Product.category_id == category_id,
        Product.store_id == store_id
    ).order_by(Product.created_at.desc()).limit(1)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def create_product(db: AsyncSession, *, product_data: dict) -> Product:
    """Create a new product from prepared data (including SKU)."""
    db_product = Product(**product_data)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

# ... (update_product and soft_delete_product remain the same) ...
async def update_product(db: AsyncSession, *, db_product: Product, product_in: ProductUpdate) -> Product:
    """Update an existing product."""
    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def soft_delete_product(db: AsyncSession, *, db_product: Product) -> Product:
    """Soft delete a product by setting the deleted_at timestamp."""
    from datetime import datetime
    db_product.deleted_at = datetime.utcnow()
    db_product.is_active = False
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product