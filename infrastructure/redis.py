# /infrastructure/redis.py
import redis.asyncio as redis
import logging
from core.config import settings

logger = logging.getLogger(__name__)

# This will be initialized on application startup
redis_pool = None

def init_redis_pool():
    """Initializes the Redis connection pool."""
    # This function is now disabled
    logger.warning("Redis initialization is currently disabled.")
    global redis_pool
    redis_pool = None
    # try:
    #     redis_pool = redis.ConnectionPool.from_url(
    #         f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    #         decode_responses=True
    #     )
    #     logger.info(f"Successfully configured Redis connection pool for {settings.REDIS_HOST}:{settings.REDIS_PORT}.")
    # except Exception as e:
    #     logger.error(f"--- FATAL: Could not configure Redis connection pool: {e} ---")
    #     redis_pool = None

async def get_redis_client() -> redis.Redis:
    """Dependency to get a Redis client from the connection pool."""
    # Raise an error because Redis is disabled.
    raise NotImplementedError("Redis is currently disabled in the application configuration.")
    # if redis_pool is None:
    #     raise ConnectionError("Redis connection pool is not available.")
    # return redis.Redis(connection_pool=redis_pool)

async def check_redis_connection():
    """Checks the Redis connection by performing a PING."""
    # This function is now disabled
    logger.warning("Redis connection check is currently disabled.")
    return True
    # try:
    #     client = await get_redis_client()
    #     await client.ping()
    #     logger.info("--- Redis connection successful. ---")
    #     return True
    # except Exception as e:
    #     logger.error(f"--- FATAL: Could not connect to Redis. Please ensure it is running. Error: {e} ---")
    #     return False