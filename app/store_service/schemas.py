# /app/store_service/schemas.py
import uuid
from typing import Optional
from pydantic import BaseModel, Field

class StoreBase(BaseModel):
    name: str = Field(..., description="The name of the store.")
    gstin: Optional[str] = Field(default=None, description="The GST Identification Number of the store.")

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    gstin: Optional[str] = None

class Store(StoreBase):
    id: uuid.UUID

    class Config:
        from_attributes = True