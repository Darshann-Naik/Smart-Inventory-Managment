# /app/category_service/crud.py

import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select, func
from datetime import datetime, timezone
from .models import Category
from .schemas import CategoryUpdate
from app.product_service.models import Product

async def get(db: AsyncSession, category_id: uuid.UUID) -> Optional[Category]:
    """
    Retrieves a single active category by ID, eagerly loading its active children.
    """
    statement = (
        select(Category)
        .where(Category.id == category_id, Category.is_active == True)
        .options(joinedload(Category.children.and_(Category.is_active == True)))
    )
    result = await db.execute(statement)
    return result.unique().scalar_one_or_none()


async def get_by_prefix(db: AsyncSession, prefix: str) -> Optional[Category]:
    """
    Retrieves a single active category by its unique prefix.
    """
    statement = (
        select(Category)
        .where(func.upper(Category.prefix) == prefix.upper(), Category.is_active == True)
    )
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> List[Category]:
    """
    Retrieves all active categories, eagerly loading their children.
    """
    statement = (
        select(Category)
        .options(joinedload(Category.children))
        .where(Category.is_active == True)
    )
    result = await db.execute(statement)
    return result.unique().scalars().all()


async def create(db: AsyncSession, category_in: dict, user_id:uuid.UUID) -> Category:
    """Creates a new category."""
    db_category = Category.model_validate(category_in)
    db_category.prefix = db_category.prefix.upper()
    db_category.created_by=user_id
    db.add(db_category)
    await db.flush()
    await db.refresh(db_category)
    return db_category

async def update(db: AsyncSession, db_category: Category, category_in: CategoryUpdate) -> Category:
    """Updates an existing category."""
    update_data = category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    if 'prefix' in update_data:
        db_category.prefix = db_category.prefix.upper()
        
    db.add(db_category)
    await db.flush()
    await db.refresh(db_category)
    return db_category

async def deactivate(db: AsyncSession, db_category: Category, user_id: uuid.UUID) -> Category:
    """Soft deletes a category by marking it inactive."""
    db_category.deactivated_at = datetime.now(timezone.utc)
    db_category.is_active = False
    db_category.deactivated_by = user_id

    db.add(db_category)
    await db.flush()
    await db.refresh(db_category)
    return db_category


async def is_in_use(db: AsyncSession, category_id: uuid.UUID) -> bool:
    """Checks if a category is linked to any products."""
    statement = select(func.count(Product.id)).where(Product.category_id == category_id)
    count = await db.execute(statement)
    return count.scalar_one() > 0
