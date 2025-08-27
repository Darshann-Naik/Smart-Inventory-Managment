# /app/store_product_service/schemas.py

import uuid
from typing import Optional
from pydantic import BaseModel, Field, computed_field
from datetime import datetime

# --- Helper Schema for nested Product data ---
# This schema defines the structure of the 'product' object we expect
# to be loaded from the database relationship.
class _ProductInfo(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

# --- INPUT SCHEMAS ---

class StoreProductCreate(BaseModel):
    """Schema for linking a new product to a store."""
    store_id: uuid.UUID
    product_id: uuid.UUID
    selling_price: float = Field(..., gt=0, description="The selling price of the product in this specific store.")
    last_purchase_price: float = Field(..., gt=0, description="The cost from the most recent purchase transaction")
    stock: int = Field(default=0, ge=0, description="Initial stock level of the product in the store.")
    reorder_point: Optional[int] = Field(default=10, ge=0)
    max_quantity: Optional[int] = Field(default=100, ge=0)

class StoreProductUpdate(BaseModel):
    """Schema for updating an existing store-product link. All fields are optional."""
    selling_price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    reorder_point: Optional[int] = Field(default=None, ge=0)
    max_quantity: Optional[int] = Field(default=None, ge=0)

# --- OUTPUT SCHEMA (Corrected) ---

class StoreProductOut(BaseModel):
    """
    Enhanced output schema that flattens nested product details
    into the final API response.
    """
    # Fields from the StoreProduct model
    id: uuid.UUID
    store_id: uuid.UUID
    product_id: uuid.UUID
    selling_price: float
    last_purchase_price: Optional[float]
    stock: int
    reorder_point: int
    max_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # This field is crucial. It tells Pydantic to expect a nested 'product'
    # object from the ORM model and validate it using the _ProductInfo schema.
    product: _ProductInfo


    class Config:
        # Allows Pydantic to read data from ORM model attributes
        from_attributes = True
        # This config ensures the 'product' object itself is NOT included
        # in the final JSON output, giving you the flat structure you want.
        fields = {'product': {'exclude': True}}
