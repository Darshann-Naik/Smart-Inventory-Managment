# /app/transaction_service/models.py

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import ForeignKeyConstraint # <-- Import ForeignKeyConstraint

if TYPE_CHECKING:
    from app.store_service.models import Store
    from app.product_service.models import Product
    from app.user_service.models import User

class TransactionType(str, Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"

class InventoryTransaction(SQLModel, table=True):
    """
    Represents a single movement of inventory (e.g., sale, purchase, adjustment).
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    
    # These columns will be used for the composite foreign key
    store_id: uuid.UUID = Field(foreign_key="store.id", index=True, nullable=False)
    product_id: uuid.UUID = Field(index=True, nullable=False)
    
    recorded_by_user_id: uuid.UUID = Field(foreign_key="user.id", index=True, nullable=False)
    
    transaction_type: TransactionType
    quantity_change: int = Field(description="Positive for stock-in, negative for stock-out")
    
    unit_cost: Optional[float] = Field(default=None)
    total_amount: Optional[float] = Field(default=None)
    
    notes: Optional[str] = None
    transaction_date: datetime = Field(default_factory=datetime.utcnow, index=True, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    store: "Store" = Relationship(back_populates="transactions")
    product: "Product" = Relationship(back_populates="transactions", sa_relationship_kwargs={"foreign_keys": "[InventoryTransaction.store_id, InventoryTransaction.product_id]"})
    recorded_by: "User" = Relationship(back_populates="transactions")

    __table_args__ = (
        # --- THIS IS THE CRITICAL FIX ---
        # Define a composite foreign key that links this table's (store_id, product_id)
        # to the product table's composite primary key (store_id, id).
        ForeignKeyConstraint(
            ["store_id", "product_id"],
            ["product.store_id", "product.id"],
        ),
    )
