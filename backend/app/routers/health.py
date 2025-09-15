"""
Health check router for system monitoring
"""

import logging
from datetime import datetime

import redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.schemas import HealthCheck

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check endpoint
    Returns the status of all critical system components
    """
    try:
        # Check database connectivity
        db.execute("SELECT 1")
        database_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_status = "unhealthy"

    # Check Redis connectivity
    try:
        from backend.app.core.config import settings

        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"

    # Check external services
    services = {
        "gemini_api": (
            "configured" if getattr(settings, "GEMINI_API_KEY") else "not_configured"
        ),
        "finnhub_api": (
            "configured" if getattr(settings, "FINNHUB_API_KEY") else "not_configured"
        ),
        "sec_api": (
            "configured" if getattr(settings, "SEC_API_KEY") else "not_configured"
        ),
    }

    # Determine overall status
    overall_status = "healthy"
    if database_status == "unhealthy" or redis_status == "unhealthy":
        overall_status = "unhealthy"
    elif any(status == "not_configured" for status in services.values()):
        overall_status = "degraded"

    return HealthCheck(
        status=overall_status,
        timestamp=datetime.now(),
        version="1.0.0",
        database=database_status,
        redis=redis_status,
        services=services,
    )


@router.get("/health/database")
async def database_health(db: Session = Depends(get_db)):
    """Specific database health check"""
    try:
        result = db.execute("SELECT version()")
        version = result.fetchone()[0]
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "database_version": version,
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")


@router.get("/health/redis")
async def redis_health():
    """Specific Redis health check"""
    try:
        from backend.app.core.config import settings

        r = redis.from_url(settings.REDIS_URL)
        info = r.info()
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "redis_version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(status_code=503, detail="Redis connection failed")
