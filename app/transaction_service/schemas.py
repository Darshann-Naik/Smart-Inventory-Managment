# /app/transaction_service/schemas.py

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .models import TransactionType

# --- RENAMED: from TransactionBase to InventoryTransactionBase ---
class InventoryTransactionBase(BaseModel):
    product_id: uuid.UUID
    quantity_change: int
    transaction_type: TransactionType
    unit_cost: Optional[float] = Field(default=None)
    total_amount: Optional[float] = Field(default=None)
    notes: Optional[str] = None

# --- RENAMED ---
class InventoryTransactionCreate(InventoryTransactionBase):
    pass

# --- RENAMED ---
class InventoryTransactionRead(InventoryTransactionBase):
    id: uuid.UUID
    store_id: uuid.UUID
    recorded_by_user_id: uuid.UUID
    transaction_date: datetime

    class Config:
        from_attributes = True