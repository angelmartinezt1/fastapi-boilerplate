from fastapi import FastAPI
from app.routers import root, health, users, ulid


def create_app() -> FastAPI:
    """
    App factory - Crea y configura la aplicación FastAPI
    """
    app = FastAPI(
        title="Mi FastAPI App",
        description="API con soporte para desarrollo local y Lambda",
        version="1.0.0",
    )

    # Registrar rutas
    register_routes(app)

    return app


def register_routes(app: FastAPI) -> None:
    """
    Registra todas las rutas de la aplicación
    """
    app.include_router(root.router)
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(ulid.router)


# Instancia de la app para importación directa si es necesario
app = create_app()
