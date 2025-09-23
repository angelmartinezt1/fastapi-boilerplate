from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.routers import root, users, ulid
from app.api import health
from app.api.v1 import sellers
from app.api.v1 import users as v1_users
from app.utils.logger import setup_logger
from app.config.settings import app_config
from app.middleware.lambda_init import LambdaInitMiddleware
from app.exceptions.handlers import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)


def create_app() -> FastAPI:
    """
    App factory - Crea y configura la aplicación FastAPI
    """
    # Setup logger
    logger = setup_logger(app_config.log_level)
    logger.info("Starting FastAPI application", extra={"extra_data": {
        "app_name": app_config.app_name,
        "version": app_config.app_version,
        "environment": app_config.environment,
        "debug": app_config.debug
    }})

    app = FastAPI(
        title="Mi FastAPI App",
        description="API con soporte para desarrollo local y Lambda",
        version="1.0.0",
    )

    # Add middleware
    app.add_middleware(LambdaInitMiddleware)

    # Add exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Registrar rutas
    register_routes(app)

    logger.info("FastAPI application setup completed")
    return app


def register_routes(app: FastAPI) -> None:
    """
    Registra todas las rutas de la aplicación
    """
    app.include_router(root.router)
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(ulid.router)
    app.include_router(sellers.router)
    app.include_router(v1_users.router)


# Instancia de la app para importación directa si es necesario
app = create_app()
