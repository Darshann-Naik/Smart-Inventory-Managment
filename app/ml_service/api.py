# /app/ml_service/api.py
from uuid import UUID
from datetime import date, timedelta
from fastapi import APIRouter, Query, HTTPException, status
from . import services, schemas

router = APIRouter()

@router.get(
    "/predict-stock/{store_id}/{product_id}",
    response_model=schemas.StockPredictionResponse,
    summary="Predict future stock level for a product over a date range"
)
async def predict_stock_level(
    store_id: UUID,
    product_id: UUID,
    start_date: date = Query(None, description="Start date for the prediction range (YYYY-MM-DD). Defaults to tomorrow."),
    end_date: date = Query(None, description="End date for the prediction range (YYYY-MM-DD). Defaults to 7 days from start_date.")
):
    """
    Predicts the future stock level for a specific product for each day
    within a given date range.
    """
    # Provide sensible defaults if dates are not specified
    if start_date is None:
        start_date = date.today() + timedelta(days=1)
    if end_date is None:
        end_date = start_date + timedelta(days=6) # Default to a 7-day range

    # Add validation for the date range
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The start_date cannot be after the end_date."
        )
    
    if (end_date - start_date).days > 30: # Limit the range to prevent overly long requests
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The prediction date range cannot exceed 31 days."
        )

    return await services.predict_stock_for_range(store_id, product_id, start_date, end_date)
