from .base import BaseConfig
from typing import Optional


class DatabaseConfig(BaseConfig):
    """Configuración de MongoDB Atlas"""

    # MongoDB Atlas Configuration
    mongodb_url: Optional[str] = None
    mongodb_database_name: str = "fastapi_app"
    mongodb_min_pool_size: int = 0
    mongodb_max_pool_size: int = 100
    mongodb_max_idle_time_ms: int = 30000
    mongodb_server_selection_timeout_ms: int = 5000
    mongodb_connect_timeout_ms: int = 10000
    mongodb_socket_timeout_ms: int = 20000

    # Connection retry settings
    mongodb_retry_writes: bool = True
    mongodb_retry_reads: bool = True

    # TLS/SSL settings for Atlas
    mongodb_tls: bool = True
    mongodb_tls_allow_invalid_certificates: bool = False

    @property
    def connection_string(self) -> str:
        """Build MongoDB connection string with parameters"""
        if not self.mongodb_url:
            raise ValueError("MongoDB URL is required")

        params = []
        params.append(f"retryWrites={str(self.mongodb_retry_writes).lower()}")
        params.append(f"retryReads={str(self.mongodb_retry_reads).lower()}")
        params.append(f"maxPoolSize={self.mongodb_max_pool_size}")
        params.append(f"minPoolSize={self.mongodb_min_pool_size}")
        params.append(f"maxIdleTimeMS={self.mongodb_max_idle_time_ms}")
        params.append(f"serverSelectionTimeoutMS={self.mongodb_server_selection_timeout_ms}")
        params.append(f"connectTimeoutMS={self.mongodb_connect_timeout_ms}")
        params.append(f"socketTimeoutMS={self.mongodb_socket_timeout_ms}")

        if self.mongodb_tls:
            params.append("tls=true")
            if self.mongodb_tls_allow_invalid_certificates:
                params.append("tlsAllowInvalidCertificates=true")

        # Check if URL already has parameters
        separator = "&" if "?" in self.mongodb_url else "?"
        return f"{self.mongodb_url}{separator}{'&'.join(params)}"