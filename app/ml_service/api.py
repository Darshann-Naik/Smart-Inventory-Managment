# /app/ml_service/api.py
from uuid import UUID
from fastapi import APIRouter

from . import services, schemas

router = APIRouter()

@router.get(
    "/predict-stock/{store_id}/{product_id}",
    response_model=schemas.StockPrediction,
    summary="Predict future stock level for a product"
)
async def predict_stock_level(store_id: UUID, product_id: UUID):
    """
    Predicts the future stock level for a specific product within a store.
    Note: This is an example endpoint. The prediction is based on a generalized model
    and hypothetical next-transaction features.
    """
    return await services.predict_stock(store_id, product_id)