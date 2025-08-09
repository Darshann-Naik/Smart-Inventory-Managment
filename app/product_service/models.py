# /app/product_service/models.py
import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, UniqueConstraint
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    from app.store_product_service.models import StoreProduct
    from app.category_service.models import Category

class Product(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True, max_length=255)
    category_id: uuid.UUID = Field(foreign_key="category.id", index=True)

    sku: str = Field(unique=True, index=True, description="e.g., ELEC-MOBILE-001")
    description: Optional[str] = None
    hsn_sac_code: Optional[str] = Field(default=None, max_length=8, description="HSN or SAC")
    tax_rate: Optional[float] = Field(default=0.0, ge=0.0, le=100.0, description="Applicable GST rate")
    image_url: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_by:uuid.UUID = Field(foreign_key="user.id", index=True)
    deactivated_by:uuid.UUID = Field(foreign_key="user.id", index=True, default=None,)
    deactivate_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp for soft delete",
        # CORRECTED: The 'index=True' parameter has been moved inside the sa_column's Column object.
        sa_column=Column(DateTime(timezone=True), index=True)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(timezone.utc))
    )

    # Relationships
    store_links: List["StoreProduct"] = Relationship(back_populates="product")
    category: "Category" = Relationship(back_populates="products")

    __table_args__ = (
        UniqueConstraint("name", "category_id", name="unique_name_in_category"),
    )
