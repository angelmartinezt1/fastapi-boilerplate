"""
Database Initialization Middleware
Handles lazy database initialization for AWS Lambda cold starts and local development
"""
import asyncio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import app_config
from app.core.database import init_database

_db_initialized = False
_init_lock = asyncio.Lock()


class LambdaInitMiddleware(BaseHTTPMiddleware):
    """Middleware to handle database initialization for Lambda and local development"""

    async def dispatch(self, request: Request, call_next):
        global _db_initialized

        # Run initialization in Lambda environment or if not yet initialized
        if not _db_initialized:
            async with _init_lock:
                # Double-check after acquiring lock
                if not _db_initialized:
                    try:
                        if app_config.is_lambda:
                            print("🔄 Lambda cold start: Initializing database...")
                        else:
                            print("🔄 Local development: Initializing database...")
                        await init_database()
                        _db_initialized = True
                        if app_config.is_lambda:
                            print("✅ Lambda: Database initialized successfully")
                        else:
                            print("✅ Local: Database initialized successfully")
                    except Exception as e:
                        if app_config.is_lambda:
                            print(f"❌ Lambda: Database initialization failed: {e}")
                        else:
                            print(f"❌ Local: Database initialization failed: {e}")
                        # Continue anyway, let the route handle the error

        response = await call_next(request)
        return response