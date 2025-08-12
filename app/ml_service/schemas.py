# /app/ml_service/schemas.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from typing import List

class StockPrediction(BaseModel):
    """Represents a stock prediction for a single day."""
    prediction_date: date
    predicted_stock: float = Field(..., description="The predicted stock level for this date.")

class StockPredictionResponse(BaseModel):
    """The response model for a date range prediction query."""
    store_id: UUID
    product_id: UUID
    predictions: List[StockPrediction]
