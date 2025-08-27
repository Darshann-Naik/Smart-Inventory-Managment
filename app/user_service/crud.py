# /app/user_service/crud.py
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from core.exceptions import BadRequestException, ConflictException
from core.security import hash_password, verify_password
from . import models, schemas

async def get_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """Retrieves a user by email, eager-loading the related role."""
    statement = (
        select(models.User)
        .where(models.User.email == email)
        .options(selectinload(models.User.role)) # Changed from .roles
    )
    result = await db.execute(statement)
    return result.scalars().first()

async def create(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    """Creates a new user and assigns a single role."""
    role_stmt = select(models.Role).where(models.Role.name == user_in.role_name)
    role = (await db.execute(role_stmt)).scalar_one_or_none()
    if not role:
        raise BadRequestException(detail=f"Role '{user_in.role_name}' does not exist.")

    new_user_id = await _generate_user_id(db, role_name=user_in.role_name)

    db_user = models.User(
        user_id=new_user_id,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        store_id=user_in.store_id,
        role=role, # Assign the single role object
    )

    db.add(db_user)
    await db.flush()
    await db.refresh(db_user, attribute_names=["role"]) # Refresh the user and its new role
    
    return db_user

async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[models.User]:
    """Authenticates a user by email and password."""
    user = await get_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def update(db: AsyncSession, db_user: models.User, user_in: schemas.UserUpdate) -> models.User:
    """Updates a user's profile data."""
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return db_user

async def _generate_user_id(db: AsyncSession, role_name: str) -> str:
    """Generates a sequential, prefixed user ID (e.g., SISO001)."""
    prefix_map = {"admin": "SISO", "employee": "SIE", "super_admin": "SISA"}
    prefix = prefix_map.get(role_name)
    if not prefix:
        raise BadRequestException(detail=f"Invalid role name for ID generation: {role_name}")

    tracker = await db.get(models.SequenceTracker, prefix, with_for_update=True)

    if not tracker:
        tracker = models.SequenceTracker(prefix=prefix, last_value=1)
    else:
        tracker.last_value += 1

    db.add(tracker)
    await db.flush()
    return f"{prefix}{tracker.last_value:03d}"