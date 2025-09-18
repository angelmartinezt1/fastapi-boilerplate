from fastapi import FastAPI
from pydantic import BaseModel
from ulid import ULID
from app.config.settings import app_config

settings = app_config


class Usuario(BaseModel):
    ulid: ULID
    nombre: str
    email: str


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

    @app.get("/")
    async def root():
        return {"message": "Hola mundo!"}

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "environment": settings.environment,
            "version": settings.app_version,
            "debug": settings.debug,
            "is_lambda": settings.is_lambda,
        }

    @app.post("/usuarios")
    async def crear_usuario(usuario: Usuario):
        return {"usuario": usuario}

    @app.get("/ulid")
    async def ulid():
        usuario = str(ULID())
        return {"ulid": usuario}


# Instancia de la app para importación directa si es necesario
app = create_app()
