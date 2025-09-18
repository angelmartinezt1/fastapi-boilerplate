from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class BaseConfig(BaseSettings):
    """Configuración base con detección automática de entorno"""

    model_config = SettingsConfigDict(
        # En local lee .env, en Lambda usa variables de entorno
        env_file=".env" if not os.environ.get("AWS_LAMBDA_FUNCTION_NAME") else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
