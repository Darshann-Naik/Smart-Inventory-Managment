# /app/store_product_service/models.py
import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    from app.store_service.models import Store
    from app.product_service.models import Product
    from app.transaction_service.models import InventoryTransaction

class StoreProduct(SQLModel, table=True):
    store_id: uuid.UUID = Field(foreign_key="store.id", primary_key=True)
    product_id: uuid.UUID = Field(foreign_key="product.id", primary_key=True)

    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    reorder_point: int = Field(default=10, ge=0)
    max_quantity: int = Field(default=100, ge=0)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(timezone.utc))
    )

    # Relationships
    store: "Store" = Relationship(back_populates="product_links")
    product: "Product" = Relationship(back_populates="store_links")
    transactions: List["InventoryTransaction"] = Relationship(back_populates="store_product")
