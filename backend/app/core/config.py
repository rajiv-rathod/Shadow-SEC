"""
Core configuration settings for Shadow SEC application
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = (
        "postgresql://shadow_sec_user:password@localhost:5432/shadow_sec_db"
    )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    SEC_API_KEY: Optional[str] = None
    ALPACA_API_KEY: Optional[str] = None
    ALPACA_SECRET_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Stock list for MVP (10 major US stocks)
    TRACKED_STOCKS: list = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "TSLA",
        "META",
        "NVDA",
        "BRK.B",
        "JNJ",
        "V",
    ]

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
