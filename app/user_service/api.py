# /app/user_service/api.py
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from . import models, schemas, services
from .dependencies import get_current_active_user

# All user/auth routes will be prefixed with /users
router = APIRouter()

@router.post(
    "/register",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Register a new user and associate them with a store."""
    return await services.register(db=db, user_in=user_in)

@router.post(
    "/token",
    response_model=schemas.Token,
    summary="Get access token"
)
async def get_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    """OAuth2 compatible token login to get an access token."""
    return await services.login(db=db, form_data=form_data)

@router.post(
    "/token/refresh",
    response_model=schemas.Token,
    summary="Refresh access token"
)
async def refresh_access_token(
    token_request: schemas.RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Refresh an access token using a valid refresh token."""
    return await services.refresh_token(db=db, token_request=token_request)

@router.get(
    "/me",
    response_model=schemas.User,
    summary="Get current user profile"
)
async def get_current_user(
    current_user: models.User = Depends(get_current_active_user),
):
    """Get the profile of the currently authenticated user."""
    return current_user

@router.put(
    "/me",
    response_model=schemas.User,
    summary="Update current user profile"
)
async def update_current_user(
    update_data: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: models.User = Depends(get_current_active_user),
):
    """Update the profile of the currently authenticated user."""
    return await services.update_profile(
        db=db,
        user=current_user,
        update_data=update_data
    )