# /app/store_service/schemas.py
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Base schema with common store attributes
class StoreBase(BaseModel):
    name: str = Field(..., description="The name of the store.")
    gstin: Optional[str] = Field(None, description="The GST Identification Number of the store.")

# Schema for creating a new store. Inherits from Base.
class StoreCreate(StoreBase):
    pass

# Schema for updating a store. All fields are optional.
class StoreUpdate(BaseModel):
    name: Optional[str] = None
    gstin: Optional[str] = None

# CORRECTED: A detailed output schema for API responses.
class StoreOut(StoreBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID

    class Config:
        from_attributes = True