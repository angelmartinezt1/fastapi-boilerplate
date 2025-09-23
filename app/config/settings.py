from functools import lru_cache
from .app import AppConfig
from .database import DatabaseConfig


@lru_cache
def get_app_config() -> AppConfig:
    """Singleton para configuración de app"""
    return AppConfig()


@lru_cache
def get_db_config() -> DatabaseConfig:
    """Singleton para configuración de base de datos"""
    return DatabaseConfig()


app_config = get_app_config()
db_config = get_db_config()
