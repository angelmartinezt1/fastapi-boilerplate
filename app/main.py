from fastapi import FastAPI
from app.routers import root, users, ulid
from app.api import health
from app.api.v1 import sellers
from app.utils.logger import setup_logger
from app.config.settings import app_config
from app.middleware.lambda_init import LambdaInitMiddleware


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

    # Add Lambda initialization middleware
    app.add_middleware(LambdaInitMiddleware)

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


# Instancia de la app para importación directa si es necesario
app = create_app()
