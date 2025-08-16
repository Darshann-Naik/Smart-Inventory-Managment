# /app/category_service/models.py
import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    from app.product_service.models import Product

class Category(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(max_length=100, unique=True, index=True)
    description: Optional[str] = None
    prefix: str = Field(max_length=4, unique=True, description="A unique, global prefix for SKU generation (e.g., 'GROC')")
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="category.id", nullable=True)
    is_active: bool = Field(default=True)
    created_by:uuid.UUID = Field(foreign_key="user.id", index=True,default=None)
    deactivated_by:uuid.UUID = Field(foreign_key="user.id", index=True, default=None, nullable=True)
    deactivated_at: Optional[datetime] = Field(
    default=None,
    description="Timestamp for soft delete",
    sa_column=Column(DateTime(timezone=True), index=True, nullable=True)
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
    products: List["Product"] = Relationship(back_populates="category")
    parent: Optional["Category"] = Relationship(back_populates="children", sa_relationship_kwargs=dict(remote_side="Category.id"))
    children: List["Category"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"lazy": "selectin"}
    )