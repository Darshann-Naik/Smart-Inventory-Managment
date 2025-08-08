# /app/product_service/schemas.py

import uuid
from typing import Optional
from pydantic import BaseModel, Field

# Shared Base Schema
class ProductBase(BaseModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None
    
    # --- MODIFIED ---
    category_id: uuid.UUID
    
    unit_of_measure: Optional[str] = Field(default=None, max_length=50)
    price: float = Field(gt=0, description="Selling price of the product")
    hsn_sac_code: Optional[str] = Field(default=None, max_length=8, description="HSN or SAC code for GST")
    tax_rate: Optional[float] = Field(default=0.0, ge=0.0, le=100.0, description="Applicable GST rate")
    image_url: Optional[str] = None

# Schema for Creating a Product
class ProductCreate(ProductBase):
    # --- MODIFIED ---
    sku: Optional[str] = Field(default=None, max_length=100, description="Leave empty to auto-generate, or provide a custom SKU.")

# Schema for Updating a Product
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    
    # --- MODIFIED ---
    category_id: Optional[uuid.UUID] = None
    
    unit_of_measure: Optional[str] = Field(default=None, max_length=50)
    price: Optional[float] = Field(default=None, gt=0)
    hsn_sac_code: Optional[str] = Field(default=None, max_length=8)
    tax_rate: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

# Schema for Reading/Returning a Product
class ProductRead(ProductBase):
    id: uuid.UUID
    store_id: uuid.UUID
    sku: str
    is_active: bool

    class Config:
        from_attributes = True