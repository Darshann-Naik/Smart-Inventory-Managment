# /app/user_service/schemas.py
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# Base schema for user attributes
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Schema for creating a new user (registration)
class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User's email address.")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters).")
    first_name: str
    last_name: str
    store_id: UUID
    role_name: str

# Schema for updating a user's profile
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Base schema for role data
class RoleBase(BaseModel):
    name: str

# Schema for reading role data
class Role(RoleBase):
    class Config:
        from_attributes = True

# The primary User schema for API responses
class User(UserBase):
    id: UUID
    user_id: str
    roles: List[Role]

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenPayload(BaseModel):
    sub: str  # Subject (user email)
    roles: List[str] = []
    exp: Optional[int] = None