"""
Lambda Initialization Middleware
Handles lazy database initialization for AWS Lambda cold starts
"""
import asyncio
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import app_config
from app.core.database import init_database

_db_initialized = False
_init_lock = asyncio.Lock()


class LambdaInitMiddleware(BaseHTTPMiddleware):
    """Middleware to handle Lambda-specific initialization"""

    async def dispatch(self, request: Request, call_next):
        global _db_initialized

        # Only run this in Lambda environment
        if app_config.is_lambda and not _db_initialized:
            async with _init_lock:
                # Double-check after acquiring lock
                if not _db_initialized:
                    try:
                        print("🔄 Lambda cold start: Initializing database...")
                        await init_database()
                        _db_initialized = True
                        print("✅ Lambda: Database initialized successfully")
                    except Exception as e:
                        print(f"❌ Lambda: Database initialization failed: {e}")
                        # Continue anyway, let the route handle the error

        response = await call_next(request)
        return response