# /app/user_service/services.py
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

# CORRECTED: Import 'get' from store_crud with an alias to avoid naming conflicts.
from app.store_service import crud as store_crud
from core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthenticatedException,
)
from core.security import create_access_token, create_refresh_token, decode_token
from . import crud, models, schemas

logger = logging.getLogger(__name__)

async def register(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    """Handles business logic for user registration."""
    if await crud.get_by_email(db, email=user_in.email):
        raise ConflictException(detail=f"A user with email '{user_in.email}' already exists.")

    # CORRECTED: Call the standardized 'get' function from store_crud.
    if not await store_crud.get(db=db, store_id=user_in.store_id):
        raise NotFoundException(resource="Store", resource_id=str(user_in.store_id))

    user = await crud.create(db=db, user_in=user_in)
    logger.info(f"User '{user.email}' registered successfully with user_id '{user.user_id}'.")
    return user

async def login(db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> schemas.Token:
    """Handles user authentication and token generation."""
    user = await crud.authenticate(db, email=form_data.username, password=form_data.password)
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
    return schemas.Token(access_token=access_token, refresh_token=refresh_token)

async def refresh_token(db: AsyncSession, token_request: schemas.RefreshTokenRequest) -> schemas.Token:
    """Handles refreshing an access token."""
    try:
        payload = decode_token(token_request.refresh_token)
        email: Optional[str] = payload.get("sub")
        if not email:
            raise UnauthenticatedException(detail="Invalid refresh token: no subject.")

        user = await crud.get_by_email(db, email=email)
        if not user or not user.is_active:
            raise UnauthenticatedException(detail="User for this token no longer exists or is inactive.")

        user_roles = [role.name for role in user.roles]
        new_access_token = create_access_token(data={"sub": user.email, "roles": user_roles})
        logger.info(f"Access token refreshed for user '{user.email}'.")
        return schemas.Token(access_token=new_access_token, refresh_token=token_request.refresh_token)
    except JWTError:
        logger.warning("Token refresh failed due to JWTError.")
        raise UnauthenticatedException(detail="Invalid or expired refresh token.")

async def update_profile(db: AsyncSession, user: models.User, update_data: schemas.UserUpdate) -> models.User:
    """Handles updating a user's own profile."""
    return await crud.update(db, db_user=user, user_in=update_data)
