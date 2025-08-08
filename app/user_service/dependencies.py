# /Smart-Invetory/app/user_service/dependencies.py

from typing import List
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from core.config import settings
from core.database import get_db_session
from core.exceptions import InvalidTokenException, UnauthorizedException
from app.user_service import crud, models  # Adjust as per your structure

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise InvalidTokenException()
    except JWTError:
        raise InvalidTokenException()

    user = await crud.get_user_by_email(db, email=email)
    if not user:
        raise InvalidTokenException()
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    if not current_user.is_active:
        raise UnauthorizedException(detail="Inactive user")
    return current_user

def require_role(required_roles: List[str]):
    """
    Dependency factory to check for user roles.
    """
    async def role_checker(
        current_user: models.User = Depends(get_current_active_user)
    ) -> models.User:
        user_roles = {role.name for role in current_user.roles}
        if not user_roles.intersection(set(required_roles)):
            raise UnauthorizedException(detail="You do not have enough permissions.")
        return current_user

    return role_checker
