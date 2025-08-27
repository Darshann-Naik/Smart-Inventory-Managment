# /app/user_service/models.py
import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    from app.store_service.models import Store
    from app.transaction_service.models import InventoryTransaction

# The UserRoleLink table is no longer needed and has been removed.

class SequenceTracker(SQLModel, table=True):
    prefix: str = Field(primary_key=True)
    last_value: int = Field(default=0)

class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    
    # Relationship to User (One-to-Many)
    users: List["User"] = Relationship(back_populates="role")


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: str = Field(unique=True, index=True, description="Custom user-facing ID like USR001")
    email: str = Field(unique=True, index=True)
    hashed_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = Field(default=True)
    
    # Foreign Key to the Role table
    role_id: Optional[int] = Field(default=None, foreign_key="role.id", index=True)
    
    store_id: Optional[uuid.UUID] = Field(default=None, index=True)
    created_by: Optional[uuid.UUID] = Field(default=None, index=True)
    deactivated_by: Optional[uuid.UUID] = Field(default=None, index=True)
    
    deactivate_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), index=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(timezone.utc)))

    # --- Relationships ---
    role: Optional["Role"] = Relationship(back_populates="users")
    transactions: List["InventoryTransaction"] = Relationship(back_populates="user")