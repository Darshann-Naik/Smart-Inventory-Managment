# /core/config.py
import os
from typing import List, Union

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', case_sensitive=True)

    # Project settings
    PROJECT_NAME: str = "AI Inventory Management SaaS"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:D3151998@localhost:5432/inventory"

    # JWT Settings
    SECRET_KEY: str = "80514942a1a897392d6acc5240b6905521cdd7e94678fb39e91e81c51493d4a7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30000
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # AWS
    AWS_ACCESS_KEY_ID: str = "YOUR_AWS_ACCESS_KEY"
    AWS_SECRET_ACCESS_KEY: str = "YOUR_AWS_SECRET_KEY"
    AWS_S3_BUCKET_NAME: str = "your-s3-bucket-name"
    AWS_REGION: str = "ap-south-1"

    # ML Settings
    ML_MODEL_PATH: str = "ml_model.pkl"
# --- Audit Log Settings ---
    # A list of field names that should be redacted in audit logs.
    AUDIT_PII_FIELDS: List[str] = ["password", "email", "token", "access_token", "refresh_token"]
    # How many days to retain audit logs. Set to 0 to retain forever.
    AUDIT_RETENTION_DAYS: int = 365
settings = Settings()