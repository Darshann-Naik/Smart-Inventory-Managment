# /app/product_service/crud.py
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from datetime import datetime, timezone
from .models import Product
from .schemas import ProductUpdate


async def get_by_sku(db: AsyncSession, sku: str) -> Optional[Product]:
    statement = select(Product).where(func.lower(Product.sku) == sku.lower())
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_by_name_and_category(db: AsyncSession, name: str, category_id: uuid.UUID) -> Optional[Product]:
    statement = select(Product).where(
        func.lower(Product.name) == name.lower(),
        Product.category_id == category_id
    )
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_last_by_sku_prefix(db: AsyncSession, sku_prefix: str) -> Optional[Product]:
    statement = (
        select(Product)
        .where(Product.sku.like(f"{sku_prefix}%"))
        .order_by(Product.created_at.desc())
        .limit(1)
    )
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_by_id(db: AsyncSession, product_id: uuid.UUID, is_active: Optional[bool] = None) -> Optional[Product]:
    statement = select(Product).where(Product.id == product_id)
    if is_active is not None:
        statement = statement.where(Product.is_active == is_active)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_all(db: AsyncSession, skip: int, limit: int, is_active: Optional[bool] = None) -> List[Product]:
    statement = select(Product)
    if is_active is not None:
        statement = statement.where(Product.is_active == is_active)
    statement = statement.offset(skip).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()

async def create(db: AsyncSession, product_data: dict) -> Product:
    db_product = Product(**product_data)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def update(db: AsyncSession, db_product: Product, product_in: ProductUpdate,user_id:uuid.UUID) -> Product:
    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    # If product is being deactivated, set deactivated_by
    if "is_active" in update_data and update_data["is_active"] is False:
        db_product.deactivated_by = user_id
        db_product.deactivate_at = datetime.now(timezone.utc)
    else:
        # Optionally clear deactivated_by if product is reactivated
        db_product.deactivated_by = None    
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def remove(db: AsyncSession, db_product: Product) -> None:
    await db.delete(db_product)
    await db.commit()

async def deactivate(db: AsyncSession, db_product: Product,user_id:uuid.UUID) -> Product:
    """Soft delete a product by setting the deleted_at timestamp."""
    db_product.deactivate_at = datetime.now(timezone.utc)
    db_product.is_active = False
    db_product.deactivated_by=user_id
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product