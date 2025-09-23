from .base import BaseConfig
from typing import Optional
import os


class AppConfig(BaseConfig):
    """Configuración principal de la aplicación"""

    # Configuración de la app
    app_name: str = "FastAPI Lambda App"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    log_level: str = "INFO"

    # Documentation settings
    enable_docs: bool = True

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ["development", "dev", "local"]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "prod"]

    @property
    def is_lambda(self) -> bool:
        """Detect if running in AWS Lambda environment"""
        return (
            os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None
            or os.getenv("AWS_EXECUTION_ENV") is not None
            or os.getenv("LAMBDA_RUNTIME_DIR") is not None
        )
