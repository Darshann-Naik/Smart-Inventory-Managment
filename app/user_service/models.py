# /app/user_service/models.py
import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    # These imports are no longer used for relationships but are kept for potential type hinting.
    from app.store_service.models import Store
    from app.transaction_service.models import InventoryTransaction

# Unchanged models...
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
    
    # --- CORRECTION: Removed all foreign_key constraints as requested ---
    # These fields now store UUIDs but are not linked at the database level.
    store_id: Optional[uuid.UUID] = Field(default=None, index=True)
    created_by: Optional[uuid.UUID] = Field(default=None, index=True)
    deactivated_by: Optional[uuid.UUID] = Field(default=None, index=True)
    
    deactivate_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), index=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(timezone.utc)))

    # --- RELATIONSHIPS ---

    # --- CORRECTION: All relationships to Store and self-referencing User relationships are removed ---
    # These cannot exist without the foreign key constraints.
    
    # These relationships can remain as they are valid and depend on other models.
    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)
    transactions: List["InventoryTransaction"] = Relationship(back_populates="user")
