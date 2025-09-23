import asyncio
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from pymongo.database import Database
from app.config.settings import db_config
from app.utils.logger import logger
from typing import Optional

# Global database instances
client: Optional[MongoClient] = None
database: Optional[Database] = None
executor: Optional[ThreadPoolExecutor] = None


def init_database() -> None:
    """Initialize MongoDB connection (sync)"""
    global client, database, executor

    try:
        if not db_config.mongodb_url:
            logger.warning("MongoDB URL not configured, skipping database initialization")
            return

        logger.info("Initializing MongoDB connection", extra={"extra_data": {
            "database_name": db_config.mongodb_database_name,
            "min_pool_size": db_config.mongodb_min_pool_size,
            "max_pool_size": db_config.mongodb_max_pool_size
        }})

        # Create MongoDB client optimized for Lambda/high-performance
        client = MongoClient(
            db_config.connection_string,
            # Lambda-optimized pool settings
            maxPoolSize=2,  # Lambda: max 1-2 concurrent requests
            minPoolSize=1,  # Keep 1 connection warm
            maxIdleTimeMS=60000,  # 1 minute (typical Lambda lifecycle)
            # Aggressive timeouts for faster failures
            serverSelectionTimeoutMS=2000,  # 2 seconds vs 5 seconds
            connectTimeoutMS=3000,  # 3 seconds vs 10 seconds
            socketTimeoutMS=5000,   # 5 seconds vs 20 seconds
            # Performance optimizations
            retryWrites=False,  # Skip retries in Lambda (fail fast)
            retryReads=False,   # Skip read retries
            w=1,  # Minimal write concern
            readPreference="primary",  # No secondary reads
            # Connection efficiency
            maxConnecting=1,  # Only 1 connection attempt at a time
            waitQueueTimeoutMS=1000  # Fast queue timeout
        )

        # Get database
        database = client[db_config.mongodb_database_name]

        # Initialize thread pool executor for async operations
        executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="pymongo")

        # Test connection
        client.admin.command('ping')

        logger.info("MongoDB connection established successfully", extra={"extra_data": {
            "database_name": db_config.mongodb_database_name
        }})

    except Exception as e:
        logger.error("Failed to initialize MongoDB connection", extra={"extra_data": {
            "error": str(e),
            "database_name": db_config.mongodb_database_name
        }})
        raise


def close_database() -> None:
    """Close MongoDB connection"""
    global client, executor

    if client:
        logger.info("Closing MongoDB connection")
        client.close()
        client = None
        logger.info("MongoDB connection closed")

    if executor:
        logger.info("Shutting down thread pool executor")
        executor.shutdown(wait=True)
        executor = None
        logger.info("Thread pool executor shut down")


def get_database() -> Database:
    """Get database instance"""
    if database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return database


def get_client() -> MongoClient:
    """Get client instance"""
    if client is None:
        raise RuntimeError("Database client not initialized. Call init_database() first.")
    return client


def get_executor() -> ThreadPoolExecutor:
    """Get thread pool executor instance"""
    if executor is None:
        raise RuntimeError("Thread pool executor not initialized. Call init_database() first.")
    return executor


async def run_in_executor(func, *args):
    """Run sync function in thread pool executor"""
    loop = asyncio.get_event_loop()
    executor_instance = get_executor()
    return await loop.run_in_executor(executor_instance, func, *args)


# Health check function
async def check_database_health() -> bool:
    """Check if database connection is healthy"""
    try:
        if client is None:
            return False

        def _ping():
            return client.admin.command('ping')

        await run_in_executor(_ping)
        return True
    except Exception as e:
        logger.error("Database health check failed", extra={"extra_data": {"error": str(e)}})
        return False