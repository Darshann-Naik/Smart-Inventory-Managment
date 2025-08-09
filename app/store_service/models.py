# /app/store_service/models.py
import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    from app.user_service.models import User
    from app.store_product_service.models import StoreProduct
    from app.transaction_service.models import InventoryTransaction

class Store(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True, unique=True)
    gstin: Optional[str] = Field(default=None, unique=True, index=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(timezone.utc))
    )

    # Relationships
    users: List["User"] = Relationship(back_populates="store")
    product_links: List["StoreProduct"] = Relationship(back_populates="store")
    transactions: List["InventoryTransaction"] = Relationship(back_populates="store")
