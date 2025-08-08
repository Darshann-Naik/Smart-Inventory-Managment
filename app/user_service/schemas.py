from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# Dummy translation function
_ = lambda text: text

# Base Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Schema for User Registration
class UserCreate(BaseModel):
    email: EmailStr = Field(..., description=_("User's email address."))
    password: str = Field(..., min_length=8, description=_("User's password (min 8 characters)."))
    first_name: str
    last_name: str
    store_id: UUID
    role_name: str

# Schema for User Update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Schema for returning Role information
class RoleRead(BaseModel):
    name: str

# Schema for returning User Information
class UserRead(UserBase):
    id: UUID  # Internal database UUID
    user_id: str  # Public/custom user identifier like "USR001"
    roles: List[RoleRead]

    class Config:
        from_attributes = True  # Replaces deprecated orm_mode

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
    exp: int  # Expiry time
