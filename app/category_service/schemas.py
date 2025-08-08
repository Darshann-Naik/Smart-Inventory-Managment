# /app/category_service/schemas.py

import uuid
from typing import Optional, List
from pydantic import BaseModel, Field

# Base schema remains the same
class CategoryBase(BaseModel):
    name: str = Field(max_length=100)
    description: Optional[str] = None
    prefix: str = Field(max_length=4, description="A 2-4 letter uppercase prefix for SKUs (e.g., 'GROC')")
    parent_id: Optional[uuid.UUID] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    prefix: Optional[str] = Field(default=None, max_length=4)
    parent_id: Optional[uuid.UUID] = None

class CategoryRead(CategoryBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

class CategoryReadWithChildren(CategoryRead):
    children: List[CategoryRead] = []