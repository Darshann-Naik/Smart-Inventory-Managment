# /app/category_service/models.py

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.product_service.models import Product

class Category(SQLModel, table=True):
    """
    Represents a UNIVERSAL product category, managed by admins.
    This is not tied to a specific store.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    
    name: str = Field(max_length=100, unique=True, index=True)
    description: Optional[str] = None
    prefix: str = Field(max_length=4, unique=True, description="A unique, global prefix for SKU generation (e.g., 'GROC')")
    
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="category.id", nullable=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    products: List["Product"] = Relationship(back_populates="category")
    
    # Self-referencing relationship for parent/child categories
    parent: Optional["Category"] = Relationship(back_populates="children", sa_relationship_kwargs=dict(remote_side="Category.id"))
    children: List["Category"] = Relationship(back_populates="parent")
