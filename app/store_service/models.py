# /app/store_service/models.py

import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.user_service.models import User
    from app.product_service.models import Product
    from app.inventory_service.models import InventoryItem
    from app.transaction_service.models import InventoryTransaction

class Store(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    gstin: Optional[str] = None
    
    # Relationships
    users: List["User"] = Relationship(back_populates="store")
    products: List["Product"] = Relationship(back_populates="store")
    inventory_items: List["InventoryItem"] = Relationship(back_populates="store")
    transactions: List["InventoryTransaction"] = Relationship(back_populates="store")
    
