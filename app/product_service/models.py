# /app/product_service/models.py

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, UniqueConstraint

if TYPE_CHECKING:
    from app.store_service.models import Store
    from app.inventory_service.models import InventoryItem
    from app.transaction_service.models import InventoryTransaction
    from app.category_service.models import Category

class Product(SQLModel, table=True):
    """
    Represents the master data for all unique products.
    """
    # --- CORRECTED: Both id and store_id now form the composite primary key ---
    # This is required by PostgreSQL for partitioning.
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    store_id: uuid.UUID = Field(foreign_key="store.id", primary_key=True, index=True)
    
    category_id: uuid.UUID = Field(foreign_key="category.id", index=True)
    
    name: str = Field(index=True, max_length=255)
    description: Optional[str] = Field(default=None)
    
    # --- CORRECTED: Removed unique=True here; it's now a composite constraint below ---
    sku: str = Field(max_length=100, index=True, description="Stock Keeping Unit")
    
    unit_of_measure: Optional[str] = Field(default=None, max_length=50)
    price: float = Field(gt=0)
    
    # GST Compliance Fields
    hsn_sac_code: Optional[str] = Field(default=None, max_length=8, description="HSN or SAC")
    tax_rate: Optional[float] = Field(default=0.0, ge=0.0, le=100.0, description="Applicable GST rate")

    image_url: Optional[str] = Field(default=None)
    
    is_active: bool = Field(default=True)
    deleted_at: Optional[datetime] = Field(default=None, index=True, description="Timestamp for soft delete")

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    store: "Store" = Relationship(back_populates="products")
    category: "Category" = Relationship(back_populates="products")
    inventory_items: List["InventoryItem"] = Relationship(back_populates="product")
    transactions: List["InventoryTransaction"] = Relationship(back_populates="product")

    # --- CORRECTED: Added a composite unique constraint for sku + store_id ---
    __table_args__ = (
        UniqueConstraint("sku", "store_id", name="unique_sku_per_store"),
        {"postgresql_partition_by": "HASH (store_id)"},
    )
