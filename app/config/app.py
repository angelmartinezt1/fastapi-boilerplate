from .base import BaseConfig
from typing import Optional


class AppConfig(BaseConfig):
    """Configuración principal de la aplicación"""

    # Configuración de la app
    app_name: str = "FastAPI Lambda App"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ["development", "dev", "local"]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "prod"]
