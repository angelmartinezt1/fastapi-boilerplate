from fastapi import APIRouter
from app.config.settings import app_config
from app.schemas.response import StandardResponse
from app.utils.response import create_success_response
from app.utils.logger import logger
from pydantic import BaseModel

router = APIRouter()

settings = app_config


class HealthData(BaseModel):
    status: str
    environment: str
    version: str
    debug: bool
    is_lambda: bool


@router.get("/health", response_model=StandardResponse[HealthData], response_model_exclude_none=True)
async def health_check():
    logger.info("Health check requested", extra={"extra_data": {
        "endpoint": "/health",
        "environment": settings.environment
    }})

    data = HealthData(
        status="healthy",
        environment=settings.environment,
        version=settings.app_version,
        debug=settings.debug,
        is_lambda=settings.is_lambda,
    )

    logger.info("Health check completed", extra={"extra_data": {
        "status": "healthy",
        "environment": settings.environment,
        "is_lambda": settings.is_lambda
    }})

    return create_success_response(
        data=data,
        message="Health check completed successfully"
    )