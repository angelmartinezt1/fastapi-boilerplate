from fastapi import APIRouter
from app.config.settings import app_config

router = APIRouter()

settings = app_config


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.app_version,
        "debug": settings.debug,
        "is_lambda": settings.is_lambda,
    }