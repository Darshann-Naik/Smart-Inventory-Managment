# /app/ml_service/services.py
import logging
from uuid import UUID
from app.transaction_service.models import InventoryTransaction
from .pipeline import get_ml_pipeline, save_model, load_model
from .schemas import StockPrediction
from datetime import datetime

logger = logging.getLogger(__name__)

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

async def predict_stock(store_id: UUID, product_id: UUID) -> StockPrediction:
    """
    Predicts the stock level for a given store and product.

    NOTE: This is a simplified prediction for demonstration. A robust prediction
    would require creating features that represent the *current* state (e.g., time of day,
    recent sales velocity, etc.), not just past transactions.
    """
    # For this example, we'll create some plausible features for a "next transaction".
    dummy_features = {
        "quantity": 5,  # An average sale size
        "day_of_week": datetime.utcnow().weekday(),
        "month": datetime.utcnow().month,
        "is_sale": 1,
        "unit_cost": 0.0 # Unknown for a future sale
    }

    prediction = ml_model.predict_one(dummy_features)

    return StockPrediction(
        store_id=store_id,
        product_id=product_id,
        predicted_stock=prediction if prediction > 0 else 0.0 # Stock can't be negative
    )