# /Smart-Invetory/app/user_service/api.py
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.router import StandardAPIRouter
from core.database import get_db_session
from . import models, schemas, services
from .dependencies import get_current_active_user

# The router now uses the StandardAPIRouter which handles response wrapping
router = StandardAPIRouter()

@router.post(
    "/auth/register",
    response_model=schemas.UserRead, # Return the UserRead schema directly
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Register a new user and associate them with a store.
    The response is automatically wrapped in a SuccessResponse by the StandardAPIRouter.
    """
    return await services.register_user(db=db, user_in=user_in)

@router.post(
    "/auth/token",
    response_model=schemas.Token, # Return the Token schema directly
    summary="Login for access token"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    """
    OAuth2 compatible token login, gets an access token for future requests.
    The response is automatically wrapped.
    """
    return await services.login_for_token(db=db, form_data=form_data)

@router.post(
    "/auth/token/refresh",
    response_model=schemas.Token, # Return the Token schema directly
    summary="Refresh access token"
)
async def refresh_token(
    token_request: schemas.RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Refresh the access token using a valid refresh token.
    The response is automatically wrapped.
    """
    return await services.refresh_access_token(db=db, token_request=token_request)


@router.get(
    "/me", # Simplified path, full path will be /api/v1/users/me
    response_model=schemas.UserRead, # Return the UserRead schema directly
    summary="Get current user"
)
async def read_current_user(
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get current user profile.
    The response is automatically wrapped.
    """
    return current_user


@router.put(
    "/me",
    response_model=schemas.UserRead,
    summary="Update current user"
)
async def update_current_user_profile(
    update_data: schemas.UserUpdate,
    db_session: AsyncSession = Depends(get_db_session),
    authenticated_user: models.User = Depends(get_current_active_user),
):
    """
    Update the profile of the currently authenticated user.
    """
    return await services.update_user_profile(
        db=db_session,
        user=authenticated_user,
        update_data=update_data
    )

