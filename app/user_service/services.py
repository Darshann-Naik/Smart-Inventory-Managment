# /Smart-Invetory/app/user_service/services.py
import logging
from sqlite3 import IntegrityError
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.store_service import crud as store_crud
from core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthenticatedException,
)
from core.security import create_access_token, create_refresh_token, decode_token
from app.user_service import crud, models, schemas


_ = lambda text: text
logger = logging.getLogger(__name__)

async def register_user(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    """
    Handles the business logic for registering a new user.
    - Validates that the email is not already taken.
    - Validates that the provided store_id exists.
    - Validates that the provided role_name is valid.
    - Creates the user via the CRUD layer.
    """
    if await crud.get_user_by_email(db, email=user_in.email):
        raise ConflictException(detail=f"A user with email '{user_in.email}' already exists.")

    store = await store_crud.get_store_by_id(db=db, store_id=user_in.store_id)
    if not store:
        raise NotFoundException(resource="Store", resource_id=str(user_in.store_id))

    role_result = await db.execute(select(models.Role).where(models.Role.name == user_in.role_name))
    if not role_result.scalar_one_or_none():
        raise BadRequestException(detail=f"Role '{user_in.role_name}' is not a valid role.")

    user = await crud.create_user(db=db, user_in=user_in)
    logger.info(f"User '{user.email}' registered successfully with user_id '{user.user_id}'.")
    return user

async def login_for_token(db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> schemas.Token:
    """
    Handles the business logic for user authentication and token generation.
    - Authenticates the user.
    - Checks if the user is active.
    - Creates and returns access and refresh tokens.
    """
    user = await crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise UnauthenticatedException()

    if not user.is_active:
        logger.warning(f"Inactive user login attempt: {form_data.username}")
        raise UnauthenticatedException(detail="Inactive user")

    user_roles = [role.name for role in user.roles]
    access_token = create_access_token(data={"sub": user.email, "roles": user_roles})
    refresh_token = create_refresh_token(data={"sub": user.email})

    logger.info(f"User '{user.email}' logged in successfully.")
    
    return schemas.Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

async def refresh_access_token(db: AsyncSession, token_request: schemas.RefreshTokenRequest) -> schemas.Token:
    """
    Handles the logic for refreshing an access token.
    - Decodes the refresh token to get the user's email.
    - Fetches the user and creates a new access token.
    """
    try:
        payload = decode_token(token_request.refresh_token)
        email = payload.get("sub")
        if not email:
            raise BadRequestException(detail="Invalid refresh token payload.")

        user = await crud.get_user_by_email(db, email=email)
        if not user:
            raise BadRequestException(detail="User for this token no longer exists.")

        user_roles = [role.name for role in user.roles]
        access_token = create_access_token(data={"sub": user.email, "roles": user_roles})

        logger.info(f"Access token refreshed for user '{user.email}'.")

        return schemas.Token(
            access_token=access_token,
            refresh_token=token_request.refresh_token
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {e}", exc_info=True)
        raise BadRequestException(detail="Invalid or expired refresh token.")

async def update_user_profile(
    db: AsyncSession,
    *,
    user: models.User,
    update_data: schemas.UserUpdate
) -> models.User:
    # Extract only the fields that were actually passed
    fields_to_update = update_data.model_dump(exclude_unset=True)

    for field_name, new_value in fields_to_update.items():
        setattr(user, field_name, new_value)

    db.add(user)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise ConflictException(detail="Update failed. Possibly due to a duplicate email.") from e

    await db.refresh(user)
    return user

