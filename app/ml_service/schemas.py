# /app/ml_service/schemas.py
from pydantic import BaseModel
from uuid import UUID

class StockPrediction(BaseModel):
    store_id: UUID
    product_id: UUID
    predicted_stock: float