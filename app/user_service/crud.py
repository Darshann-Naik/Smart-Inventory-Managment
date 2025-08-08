# /app/user_service/crud.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from core.exceptions import BadRequestException, ConflictException
from core.security import hash_password, verify_password
from . import models, schemas
from app.user_service.models import User 
_ = lambda text: text

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Retrieves a user by email, eager-loading related roles and store data.
    Prevents async lazy-loading crashes by using selectinload.
    """
    statement = (
        select(User)
        .where(User.email == email)
        .options(
            selectinload(User.roles),
            selectinload(User.store)
        )
    )
    result = await db.execute(statement)
    return result.scalars().first()

async def create_user(db: AsyncSession, *, user_in: schemas.UserCreate) -> models.User:
    """
    Creates a new user and then refreshes the user with all relationships
    loaded to ensure it can be correctly serialized in the API response.
    """
    role_stmt = select(models.Role).where(models.Role.name == user_in.role_name)
    role_result = await db.execute(role_stmt)
    role = role_result.scalar_one_or_none()
    if not role:
        raise BadRequestException(detail=f"Role '{user_in.role_name}' does not exist.")

    new_user_id = await generate_user_id(db, role_name=user_in.role_name)

    db_user = models.User(
        user_id=new_user_id,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        store_id=user_in.store_id,
        roles=[role],
    )

    db.add(db_user)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        if "user_email_key" in str(e.orig).lower():
            raise ConflictException(detail=f"A user with email '{user_in.email}' already exists.")
        if "user_store_id_fkey" in str(e.orig).lower():
            raise BadRequestException(detail=f"The store ID '{user_in.store_id}' does not exist.")
        raise ConflictException(detail="A database integrity error occurred.")

    # --- THIS IS THE CORRECTED LOGIC ---
    # After the commit, the db_user object is expired. We need to refresh it
    # to eagerly load the relationships for the response model. This is the
    # correct way to avoid the MissingGreenlet error.
    await db.refresh(db_user, attribute_names=["roles", "store"])
    return db_user


async def generate_user_id(db: AsyncSession, role_name: str) -> str:
    prefix_map = {
        "shop_owner": "SISO",
        "employee": "SIE",
        "super_admin": "SISA",
    }
    prefix = prefix_map.get(role_name)
    if not prefix:
        raise BadRequestException(detail=f"Invalid role name: {role_name}")

    result = await db.execute(
        select(models.SequenceTracker).where(models.SequenceTracker.prefix == prefix).with_for_update()
    )
    tracker = result.scalar_one_or_none()

    if not tracker:
        tracker = models.SequenceTracker(prefix=prefix, last_value=1)
    else:
        tracker.last_value += 1

    db.add(tracker)
    await db.flush()
    return f"{prefix}{tracker.last_value:03d}"

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[models.User]:
    """
    This function relies on get_user_by_email to correctly load the user
    and all necessary relationships.
    """
    user = await get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def update_user(db: AsyncSession, *, db_user: models.User, user_in: schemas.UserUpdate) -> models.User:
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(detail="Update failed. The new email might already be in use.")
        
    # Refresh to get the latest state and relationships
    await db.refresh(db_user, attribute_names=["roles", "store"])
    return db_user
