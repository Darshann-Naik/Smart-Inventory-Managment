# /app/category_service/schemas.py

import uuid
from typing import Optional, List
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(default=None)
    prefix: str = Field(..., max_length=4, description="A 2-4 letter uppercase prefix for SKUs (e.g., 'GROC')")
    parent_id: Optional[uuid.UUID] = Field(default=None)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    prefix: Optional[str] = Field(default=None, max_length=4)
    parent_id: Optional[uuid.UUID] = None


class Category(CategoryBase):
    id: uuid.UUID
    # Avoid direct lazy loading → children will be populated only if you eagerly load in query
    children: List["Category"] = Field(default_factory=list)

    class Config:
        from_attributes = True  # allows ORM -> Pydantic conversion


Category.model_rebuild()
