# /app/ml_service/services.py
import logging
from uuid import UUID
from app.transaction_service.models import InventoryTransaction
from .pipeline import get_ml_pipeline, save_model, load_model
from fastapi import APIRouter
from datetime import date, timedelta
from .schemas import StockPrediction, StockPredictionResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# --- GLOBAL MODEL OBJECT ---
# The model is loaded into memory once when the application starts.
ml_model = load_model()
if ml_model is None:
    ml_model = get_ml_pipeline()

def get_features(transaction: InventoryTransaction) -> dict:
    """
    Extracts a feature dictionary from a raw transaction object.
    This is a crucial step to translate our application data into something
    the model can understand (numbers!).
    """
    return {
        "quantity": abs(transaction.quantity),
        "day_of_week": transaction.timestamp.weekday(),
        "month": transaction.timestamp.month,
        "year": transaction.timestamp.year, 
        "is_sale": 1 if transaction.quantity < 0 else 0,
        "unit_cost": transaction.unit_cost or 0.0
    }

async def train_model(transaction: InventoryTransaction, new_stock_level: int):
    """
    Incrementally trains the model with a new transaction.
    This is designed to be called in the background so it doesn't slow down the user's request.
    """
    try:
        features = get_features(transaction)
        target = new_stock_level

        # The core of River: learn from one new example.
        ml_model.learn_one(features, target)

        # Save the updated model's "brain" for the next time the app starts.
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
    
    NOTE: This simple model assumes a typical sale occurs each day to generate a trend.
    A more advanced model could learn to predict days with no sales or with purchases.
    """
    predictions = []
    current_date = start_date
    
    while current_date <= end_date:
        # Create plausible features for a hypothetical transaction on the current_date.
        hypothetical_features = {
            "quantity": 5,  # An average sale size assumption
            "day_of_week": current_date.weekday(),
            "month": current_date.month,
            "year": current_date.year,
            "is_sale": 1,
            "unit_cost": 0.0 # Assuming cost is not a factor for a future sale prediction
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
