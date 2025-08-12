# /app/store_product_service/models.py
import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    from app.store_service.models import Store
    from app.product_service.models import Product
    # Assuming you have a User model for the foreign keys
    from app.user_service.models import User

class StoreProduct(SQLModel, table=True):
    # --- CORRECTION: Added a dedicated UUID primary key ---
    # This 'id' field now serves as the unique identifier for each store-product link.
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # --- These are now regular foreign key fields, not part of the primary key ---
    store_id: uuid.UUID = Field(foreign_key="store.id", index=True)
    product_id: uuid.UUID = Field(foreign_key="product.id", index=True)

    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    reorder_point: int = Field(default=10, ge=0)
    max_quantity: int = Field(default=100, ge=0)
    is_active: bool = Field(default=True)
    
    # These foreign keys remain correct.
    created_by: uuid.UUID = Field(foreign_key="user.id", index=True)
    deactivated_by: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id", index=True)
    
    deactivated_at: Optional[datetime] = Field(default=None, description="Timestamp for soft delete", sa_column=Column(DateTime(timezone=True), index=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(timezone.utc)))

    # --- RELATIONSHIPS ---
    store: "Store" = Relationship(back_populates="product_links")
    product: "Product" = Relationship(back_populates="store_links")
