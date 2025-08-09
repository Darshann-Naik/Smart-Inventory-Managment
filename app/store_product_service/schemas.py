# /app/store_product_service/schemas.py
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class StoreProductBase(BaseModel):
    price: float = Field(..., gt=0, description="The selling price of the product in this specific store.")
    stock: int = Field(default=0, ge=0, description="Current stock level of the product in the store.")
    reorder_point: Optional[int] = Field(default=10, ge=0, description="The stock level at which a reorder should be triggered.")
    max_quantity: Optional[int] = Field(default=100, ge=0, description="The maximum quantity of this product to keep in stock.")

class StoreProductCreate(StoreProductBase):
    store_id: uuid.UUID
    product_id: uuid.UUID

class StoreProductUpdate(BaseModel):
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    reorder_point: Optional[int] = Field(default=None, ge=0)
    max_quantity: Optional[int] = Field(default=None, ge=0)

class StoreProduct(StoreProductBase):
    store_id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True