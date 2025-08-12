# /app/transaction_service/schemas.py
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .models import TransactionType

class TransactionBase(BaseModel):
    store_id: uuid.UUID
    product_id: uuid.UUID
    transaction_type: TransactionType
    quantity: int = Field(..., gt=0, description="The absolute number of items in the transaction.")
    unit_cost: float = Field(..., ge=0, description="Cost per item at the time of transaction.")
    notes: Optional[str] = Field(default=None, description="Additional notes for the transaction.")

class TransactionCreate(TransactionBase):
    pass

# There is no 'Update' schema because transactions are immutable.

class Transaction(TransactionBase):
    id: uuid.UUID
    recorded_by_user_id: uuid.UUID
    quantity: int
    total_amount: float
    timestamp: datetime

    class Config:
        from_attributes = True