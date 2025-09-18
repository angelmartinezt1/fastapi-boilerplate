from functools import lru_cache
from .app import AppConfig


@lru_cache
def get_app_config() -> AppConfig:
    """Singleton para configuración de app"""
    return AppConfig()


app_config = get_app_config()
