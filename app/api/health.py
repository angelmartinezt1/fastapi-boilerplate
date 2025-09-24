from fastapi import APIRouter
from app.config.settings import app_config, db_config
from app.schemas.response import StandardResponse
from app.utils.response import create_success_response
from app.utils.logger import logger
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

settings = app_config


class HealthData(BaseModel):
    status: str
    environment: str
    version: str
    debug: bool
    is_lambda: bool
    database_status: Optional[str] = None


@router.get(
    "/health",
    response_model=StandardResponse[HealthData],
    response_model_exclude_none=True,
)
async def health_check():
    logger.info(
        "Health check requested",
        extra={
            "extra_data": {"endpoint": "/health", "environment": settings.environment}
        },
    )

    # Check database status if MongoDB URL is configured
    database_status = None
    overall_status = "AWS healthy"

    if db_config.mongodb_url:
        try:
            from app.core.database import check_database_health

            db_healthy = await check_database_health()
            database_status = "connected" if db_healthy else "disconnected"
            if not db_healthy:
                overall_status = "degraded"
                logger.warning(
                    "Database health check failed",
                    extra={"extra_data": {"database_status": database_status}},
                )
        except Exception as e:
            database_status = "error"
            overall_status = "degraded"
            logger.error(
                "Database health check error",
                extra={
                    "extra_data": {"error": str(e), "database_status": database_status}
                },
            )

    data = HealthData(
        status=overall_status,
        environment=settings.environment,
        version=settings.app_version,
        debug=settings.debug,
        is_lambda=settings.is_lambda,
        database_status=database_status,
    )

    logger.info(
        "Health check completed",
        extra={
            "extra_data": {
                "status": overall_status,
                "environment": settings.environment,
                "is_lambda": settings.is_lambda,
                "database_status": database_status,
            }
        },
    )

    return create_success_response(
        data=data, message="Health check completed successfully"
    )
