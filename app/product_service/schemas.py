# /app/product_service/schemas.py
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the product.")
    category_id: uuid.UUID
    description: Optional[str] = Field(default=None, description="Detailed description of the product.")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    category_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    hsn_sac_code: Optional[str] = Field(default=None, max_length=50)
    tax_rate: Optional[float] = None
    image_url: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: uuid.UUID
    sku: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True