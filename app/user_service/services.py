# /app/user_service/services.py
import logging
import uuid
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from app.store_service import crud as store_crud
from core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthenticatedException,
)
from core.security import create_access_token, create_refresh_token, decode_token
from app.audit_log_service.services import AuditLogger
from . import crud, models, schemas

logger = logging.getLogger(__name__)

async def register(db: AsyncSession, user_in: schemas.UserCreate, request: Request) -> models.User:
    """Handles business logic for user registration and creates an audit log."""
    if await crud.get_by_email(db, email=user_in.email):
        raise ConflictException(detail=f"A user with email '{user_in.email}' already exists.")

    if not await store_crud.get(db=db, store_id=user_in.store_id):
        raise NotFoundException(resource="Store", resource_id=str(user_in.store_id))

    user = await crud.create(db=db, user_in=user_in)
    logger.info(f"User '{user.email}' registered successfully with user_id '{user.user_id}'.")

    user_schema = schemas.User.model_validate(user)
    audit_logger = AuditLogger(db, request=request)
    await audit_logger.record_event(
        action="REGISTER_USER",
        entity_type="User",
        entity_id=str(user.id),
        after=json.loads(user_schema.model_dump_json())
    )

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

    # Get the single role name for the JWT
    user_roles = [user.role.name] if user.role else []
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

        user_roles = [user.role.name] if user.role else []
        new_access_token = create_access_token(data={"sub": user.email, "roles": user_roles})
        logger.info(f"Access token refreshed for user '{user.email}'.")
        return schemas.Token(access_token=new_access_token, refresh_token=token_request.refresh_token)
    except JWTError:
        logger.warning("Token refresh failed due to JWTError.")
        raise UnauthenticatedException(detail="Invalid or expired refresh token.")

async def update_profile(db: AsyncSession, user: models.User, update_data: schemas.UserUpdate, request: Request) -> models.User:
    """Handles updating a user's own profile and creates an audit log."""
    
    before_schema = schemas.User.model_validate(user)
    before_state = json.loads(before_schema.model_dump_json())

    updated_user = await crud.update(db=db, db_user=user, user_in=update_data)
    
    after_schema = schemas.User.model_validate(updated_user)
    after_state = json.loads(after_schema.model_dump_json())
    
    audit_logger = AuditLogger(db, current_user=user, request=request)
    await audit_logger.record_event(
        action="UPDATE_PROFILE",
        entity_type="User",
        entity_id=str(user.id),
        before=before_state,
        after=after_state
    )
    
    return updated_user