# /app/ml_service/services.py
import logging
from uuid import UUID
from datetime import datetime, timedelta, date
from app.transaction_service import models as transaction_models # Use alias for clarity
from .pipeline import get_ml_pipeline, save_model, load_model
from .schemas import StockPrediction, StockPredictionResponse

logger = logging.getLogger(__name__)

# --- GLOBAL MODEL OBJECT ---
ml_model = load_model()
if ml_model is None:
    ml_model = get_ml_pipeline()

def get_features(transaction: transaction_models.InventoryTransaction) -> dict:
    """
    Extracts a feature dictionary from a raw transaction object.
    This version is enhanced to use the more explicit price, cost, and discount fields.
    """
    is_sale = 1 if transaction.transaction_type == transaction_models.TransactionType.SALE else 0
    is_purchase = 1 if transaction.transaction_type == transaction_models.TransactionType.PURCHASE else 0

    return {
        "quantity": abs(transaction.quantity),
        "day_of_week": transaction.timestamp.weekday(),
        "month": transaction.timestamp.month,
        "year": transaction.timestamp.year,
        "is_sale": is_sale,
        "is_purchase": is_purchase,
        # Use the specific price/cost field depending on the transaction type for better learning
        "price_or_cost": transaction.unit_price_at_sale if is_sale else transaction.unit_cost or 0.0,
        "discount": transaction.discount or 0.0
    }

async def train_model(transaction: transaction_models.InventoryTransaction, new_stock_level: int):
    """Incrementally trains the model with a new transaction."""
    try:
        features = get_features(transaction)
        target = new_stock_level
        ml_model.learn_one(features, target)
        save_model(ml_model)
        logger.info(f"ML model successfully updated with transaction {transaction.id}")
    except Exception as e:
        logger.error(f"Failed to train ML model with transaction {transaction.id}: {e}", exc_info=True)

async def predict_stock_for_range(
    store_id: UUID,
    product_id: UUID,
    start_date: date,
    end_date: date
) -> StockPredictionResponse:
    """
    Predicts the stock level for each day within a given date range.
    """
    predictions = []
    current_date = start_date
    
    while current_date <= end_date:
        # Create plausible features for a hypothetical transaction on the current_date.
        hypothetical_features = {
            "quantity": 5, # An average sale size assumption
            "day_of_week": current_date.weekday(),
            "month": current_date.month,
            "year": current_date.year,
            "is_sale": 1,
            "is_purchase": 0,
            "price_or_cost": 0.0, # Price is unknown for a future sale, model will learn this
            "discount": 0.0
        }

        prediction_value = ml_model.predict_one(hypothetical_features)
        
        daily_prediction = StockPrediction(
            prediction_date=current_date,
            predicted_stock=prediction_value if prediction_value > 0 else 0.0
        )
        predictions.append(daily_prediction)
        
        current_date += timedelta(days=1)

    return StockPredictionResponse(
        store_id=store_id,
        product_id=product_id,
        predictions=predictions
    )
