# /app/transaction_service/schemas.py
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, root_validator
from .models import TransactionType

class TransactionBase(BaseModel):
    store_id: uuid.UUID
    product_id: uuid.UUID
    transaction_type: TransactionType
    quantity: int = Field(..., gt=0, description="The absolute number of items in the transaction.")
    notes: Optional[str] = Field(default=None, description="Additional notes for the transaction.")

class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    unit_cost: Optional[float] = Field(default=None, ge=0, description="Required cost per unit for a PURCHASE transaction.")
    discount: Optional[float] = Field(default=0.0, ge=0, description="Optional discount for a SALE transaction.")

    @root_validator(pre=True)
    def check_business_rules(cls, values):
        """Pydantic validator to enforce transaction logic."""
        ttype = values.get("transaction_type")
        if ttype == TransactionType.PURCHASE and values.get("unit_cost") is None:
            raise ValueError("unit_cost is required for a PURCHASE transaction.")
        if ttype == TransactionType.SALE and values.get("unit_cost") is not None:
            raise ValueError("unit_cost must not be provided for a SALE transaction.")
        return values

class Transaction(TransactionBase):
    """The full transaction model for API responses."""
    id: uuid.UUID
    recorded_by_user_id: uuid.UUID
    quantity: int
    total_amount: float
    timestamp: datetime
    unit_cost: Optional[float]
    unit_price_at_sale: Optional[float]
    discount: Optional[float]
    cost_of_goods_sold: Optional[float]

    class Config:
        from_attributes = True
