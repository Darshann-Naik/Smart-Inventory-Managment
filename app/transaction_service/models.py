# /app/transaction_service/models.py
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    from app.user_service.models import User
    from app.store_service.models import Store
    from app.product_service.models import Product

class TransactionType(str, Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    ADJUSTMENT = "adjustment"

class InventoryTransaction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    store_id: uuid.UUID = Field(foreign_key="store.id", index=True, nullable=False)
    product_id: uuid.UUID = Field(foreign_key="product.id", index=True, nullable=False)
    recorded_by_user_id: uuid.UUID = Field(foreign_key="user.id", index=True, nullable=False)

    transaction_type: TransactionType
    quantity_change: int = Field(description="Negative for SALE, positive for PURCHASE/ADJUSTMENT.")
    unit_cost: Optional[float] = Field(default=None, description="Cost per item. Can be null for non-purchase events.")
    total_amount: float = Field(description="Total amount for the transaction.")
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(DateTime(timezone=True), nullable=False))

    # --- RELATIONSHIPS ---
    store: "Store" = Relationship(back_populates="transactions")
    user: "User" = Relationship(back_populates="transactions")
    product: "Product" = Relationship(back_populates="transactions")