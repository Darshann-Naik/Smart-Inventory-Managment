# /app/category_service/crud.py

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from .models import Category
from .schemas import CategoryCreate, CategoryUpdate
from app.product_service.models import Product

async def get_category_by_id(db: AsyncSession, *, category_id: uuid.UUID) -> Optional[Category]:
    statement = select(Category).where(Category.id == category_id)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_category_by_prefix(db: AsyncSession, *, prefix: str) -> Optional[Category]:
    statement = select(Category).where(func.upper(Category.prefix) == prefix.upper())
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def get_all_categories(db: AsyncSession) -> List[Category]:
    statement = select(Category)
    result = await db.execute(statement)
    return result.scalars().all()

async def create_category(db: AsyncSession, *, category_in: CategoryCreate) -> Category:
    db_category = Category.model_validate(category_in)
    db_category.prefix = db_category.prefix.upper()
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def update_category(db: AsyncSession, *, db_category: Category, category_in: CategoryUpdate) -> Category:
    update_data = category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    if 'prefix' in update_data:
        db_category.prefix = db_category.prefix.upper()
        
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def delete_category(db: AsyncSession, *, db_category: Category) -> None:
    """Hard deletes a category."""
    await db.delete(db_category)
    await db.commit()

async def is_category_in_use(db: AsyncSession, *, category_id: uuid.UUID) -> bool:
    """Checks if a category is linked to any products."""
    statement = select(func.count(Product.id)).where(Product.category_id == category_id)
    count = await db.execute(statement)
    return count.scalar_one() > 0