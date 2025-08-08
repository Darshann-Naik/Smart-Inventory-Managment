# /app/user_service/models.py

import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.store_service.models import Store
    from app.transaction_service.models import InventoryTransaction 

# ... (SequenceTracker, UserRoleLink, Role models are unchanged) ...
class SequenceTracker(SQLModel, table=True):
    prefix: str = Field(primary_key=True)
    last_value: int = Field(default=0)

class UserRoleLink(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)

class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: str = Field(unique=True, index=True, description="Custom user-facing ID like USR001")
    email: str = Field(unique=True, index=True)
    hashed_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = Field(default=True)
    store_id: uuid.UUID = Field(foreign_key="store.id")

    # Relationships
    store: "Store" = Relationship(back_populates="users")
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)
    
    # --- ADD THIS RELATIONSHIP ---
    transactions: List["InventoryTransaction"] = Relationship() # Relationship is one-way from Transaction to User