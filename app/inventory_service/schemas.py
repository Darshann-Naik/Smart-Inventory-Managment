# /app/inventory_service/schemas.py

import uuid
from typing import Optional
from pydantic import BaseModel, Field
from app.product_service.schemas import ProductRead

class InventoryItemBase(BaseModel):
    quantity: int = Field(ge=0, description="Current stock quantity")
    reorder_point: Optional[int] = Field(default=0, ge=0, description="Reorder threshold")

class InventoryItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=0)
    reorder_point: Optional[int] = Field(default=0, ge=0)

class InventoryItemUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, ge=0)
    reorder_point: Optional[int] = Field(default=None, ge=0)

class InventoryItemRead(InventoryItemBase):
    id: uuid.UUID
    store_id: uuid.UUID
    product: ProductRead

    class Config:
        from_attributes = True