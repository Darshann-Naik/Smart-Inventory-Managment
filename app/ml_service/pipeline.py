# /app/ml_service/pipeline.py
import pickle
import logging
from river import compose, linear_model, preprocessing

from core.config import settings

logger = logging.getLogger(__name__)

def get_ml_pipeline():
    """
    Defines and creates the River ML pipeline.
    This is where you can experiment with different models or add more preprocessing steps.
    """
    model = compose.Pipeline(
        ('scale', preprocessing.StandardScaler()),
        ('lin_reg', linear_model.LinearRegression())
    )
    return model

def save_model(model):
    """
    Saves the trained ML model object to a file using pickle.
    """
    try:
        with open(settings.ML_MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
    except Exception as e:
        logger.error(f"Error saving ML model: {e}", exc_info=True)


def load_model():
    """
    Loads the ML model from a file. If the file doesn't exist,
    it returns None.
    """
    try:
        with open(settings.ML_MODEL_PATH, 'rb') as f:
            logger.info(f"Loading existing ML model from {settings.ML_MODEL_PATH}")
            return pickle.load(f)
    except FileNotFoundError:
        logger.warning("ML model file not found. A new model will be created.")
        return None
    except Exception as e:
        logger.error(f"Error loading ML model: {e}", exc_info=True)
        return None