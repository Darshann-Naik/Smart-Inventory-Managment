# /app/inventory_service/models.py

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, UniqueConstraint
from sqlalchemy import ForeignKeyConstraint # <-- Import ForeignKeyConstraint

if TYPE_CHECKING:
    from app.store_service.models import Store
    from app.product_service.models import Product

class InventoryItem(SQLModel, table=True):
    """
    Represents the actual stock level of a product at a specific store.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    
    # These columns will be used for the composite foreign key
    store_id: uuid.UUID = Field(foreign_key="store.id", index=True, nullable=False)
    product_id: uuid.UUID = Field(index=True, nullable=False)
    
    quantity: int = Field(default=0, ge=0, description="Current stock quantity")
    reorder_point: int = Field(default=0, ge=0, description="Threshold to trigger reorder alerts")
    
    last_counted_at: datetime = Field(default_factory=datetime.utcnow)
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    store: "Store" = Relationship(back_populates="inventory_items")
    product: "Product" = Relationship(back_populates="inventory_items", sa_relationship_kwargs={"foreign_keys": "[InventoryItem.store_id, InventoryItem.product_id]"})

    __table_args__ = (
        # --- THIS IS THE CRITICAL FIX ---
        # Define a composite foreign key that links this table's (store_id, product_id)
        # to the product table's composite primary key (store_id, id).
        ForeignKeyConstraint(
            ["store_id", "product_id"],
            ["product.store_id", "product.id"],
        ),
        UniqueConstraint("store_id", "product_id", name="unique_product_per_store"),
    )
